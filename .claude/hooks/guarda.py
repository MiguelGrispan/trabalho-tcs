#!/usr/bin/env python3
"""Guarda do Raio-X: os hooks do Claude Code e a conferência do CI, num script só.

O Claude Code chama este script em 3 momentos (`.claude/settings.json`) e manda um JSON pela entrada padrão:
    python3 guarda.py inicio    SessionStart: o que ele imprime vira contexto do Claude
    python3 guarda.py antes     PreToolUse: código 2 bloqueia a ação; JSON com "ask" pergunta a você
    python3 guarda.py fim       Stop: código 2 impede o Claude de parar e devolve o erro para ele
E o teste `tests/test_guarda.py` usa a mesma lista de proibidos para conferir o repositório inteiro no CI:
    python3 guarda.py conferir  código 1 se o Git tem dado, .env, chave ou arquivo grande

Por que um script: uma lista de proibidos só, testada, para o hook e para o CI.
Só biblioteca padrão: roda com o python3 do Mac ou do Linux, sem instalar nada.

Regra de desenho (aprendida na revisão do PR #30): o hook procura o perigo em QUALQUER lugar do comando e não tenta
entender o shell. Tentar separar "texto de mensagem" de "comando" abriu furos duas vezes. Na dúvida, bloqueia, e a
mensagem de bloqueio diz a saída certa (mensagem de commit ou PR vai por arquivo: -F / --body-file).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# CLAUDE_PROJECT_DIR é a raiz do repositório; o Claude Code passa essa variável para todo hook
RAIZ = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()

# Chave de API do Google (Gemini): começa com AIza e tem 39 caracteres
CHAVE_GOOGLE = r"AIza[0-9A-Za-z_-]{35}"
LIMITE_BYTES = 10 * 1024 * 1024  # REGRAS-IA.md, seção 2: nada acima de 10 MB

# "git", com as opções que vêm antes do subcomando (git -C pasta, git -c x=y, git --no-pager), em qualquer ponto do texto
GIT = r"""\bgit\b(?:\s+(?:-C\s+(?:"[^"]*"|'[^']*'|\S+)|-c\s+\S+|--[\w-]+(?:=\S+)?|-[a-zA-Z]+))*\s+"""
RESTO = r"[^\n;&|]*"  # o resto do mesmo comando

# Comandos que reescrevem a história ou apagam trabalho (CLAUDE.md, regra 8)
PERIGOSOS = [
    (GIT + r"rebase\b", "o rebase reescreve a história"),
    (GIT + r"pull\b" + RESTO + r"\s(-r|--rebase)(?![\w-])", "o pull --rebase reescreve a história"),
    (GIT + r"push\b" + RESTO + r"(\s(-\w*f\w*|--force(-with-lease)?)(?![\w-])|\s\+\S)",
     "o push --force (ou +branch) pode apagar o trabalho de um colega"),
    (GIT + r"reset\b" + RESTO + r"--hard\b", "o reset --hard apaga mudanças sem commit"),
    (GIT + r"clean\b", "o git clean apaga arquivos fora do Git (com -x, a data/ e o .env)"),
    (GIT + r"add\b" + RESTO + r"\s(-\w*f\w*|--force)(?![\w-])", "o add --force passa por cima do .gitignore (data/, .env)"),
]

# As próprias travas e o CI: mudam o computador e os PRs de todos
TRAVAS = (".claude/settings.json", ".claude/hooks/", ".claude/agents/", ".github/workflows/", "tests/test_guarda.py")
ESCREVE = r"(>|\bsed\s+-i|\bperl\s+-p?i|\brm\b|\bmv\b|\bcp\b|\btee\b|\btruncate\b)"

SAIDA_MENSAGEM = ("Se é só o texto de uma mensagem de commit ou PR, escreva a mensagem num arquivo fora do repositório "
                  "com a ferramenta Write e use git commit -F <arquivo> ou gh pr create --body-file <arquivo>.")


def git(*args):
    """Roda um comando git na raiz e devolve a saída (vazia se der erro ou se não houver git, como no contêiner).
    core.quotePath=false: nome com acento sai como é ("data/relatório.csv"), não entre aspas e com códigos."""
    try:
        r = subprocess.run(["git", "-C", str(RAIZ), "-c", "core.quotePath=false", *args], capture_output=True, text=True)
    except OSError:
        return ""
    return r.stdout.strip()


def normalizar(nome):
    """'Náthally' -> 'nathally', 'Miguel Alves' -> 'miguelalves'."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", sem_acento.lower())


def bloquear(motivo):
    """Código 2: a ação não acontece em nenhum modo, e o motivo vai para o Claude."""
    print(motivo, file=sys.stderr)
    sys.exit(2)


def perguntar(motivo):
    """JSON com "ask": o Claude Code mostra o motivo e pede o seu ok."""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": motivo,
    }}, ensure_ascii=False))
    sys.exit(0)


def proibido(caminho):
    """Diz por que um arquivo não pode ir para o Git, ou None se pode (REGRAS-IA.md, seção 2)."""
    minusculo = caminho.lower()
    if minusculo.startswith("data/") and minusculo != "data/.gitkeep":
        return "dado da CVM ou gerado (data/)"
    if re.search(r"(^|/)[^/]*\.env(\.[^/]*)?$", minusculo) and not minusculo.endswith(".env.example"):
        return "um .env (chave ou senha)"
    if minusculo.endswith(".streamlit/secrets.toml"):
        return "segredos do Streamlit"
    if re.search(r"\.(db|sqlite3?|zip|parquet)$", minusculo):
        return "banco ou arquivo de dados"
    if re.search(r"\.tfstate(\.|$)|\.tfvars(\.json)?$", minusculo):
        return "estado ou variáveis do Terraform (podem guardar senha)"
    arquivo = RAIZ / caminho
    if arquivo.is_file() and arquivo.stat().st_size > LIMITE_BYTES:
        return "arquivo acima de 10 MB"
    return None


def donos():
    """Lê a tabela 'Estrutura e donos' do CLAUDE.md. Uma fonte só: mudou lá, o hook acompanha."""
    mapa, dentro = {}, False
    for linha in (RAIZ / "CLAUDE.md").read_text(encoding="utf-8").splitlines():
        if linha.startswith("## "):
            dentro = linha.startswith("## Estrutura e donos")
        elif dentro and linha.startswith("|") and "`" in linha:
            colunas = [c.strip() for c in linha.strip("|").split("|")]
            for caminho in re.findall(r"`([^`]+)`", colunas[0]):
                mapa[caminho] = colunas[-1]
    return mapa


def dono_de(relativo):
    """O caminho mais específico vence: avaliacao/avaliar.py é do Eduardo, o resto de avaliacao/ é da Náthally."""
    melhor, dono = "", None
    for caminho, pessoa in donos().items():
        casa = relativo == caminho or (caminho.endswith("/") and relativo.startswith(caminho))
        if casa and len(caminho) > len(melhor):
            melhor, dono = caminho, pessoa
    return dono


def linhas_novas(diff):
    """Só as linhas que o commit acrescenta (apagar uma chave vazada tem de poder), sem o cabeçalho '+++ b/arquivo'."""
    return [l for l in diff.splitlines() if l.startswith("+") and not re.match(r"\+\+\+ (a/|b/|/dev/null)", l)]


def commit_levaria():
    """O que está no stage, mudado ou novo na pasta (fora do .gitignore). O hook roda ANTES do comando, então não
    sabe o que um git add no mesmo comando vai pôr: confere tudo o que está solto. Na dúvida, bloqueia."""
    arquivos = set(git("diff", "--cached", "--name-only", "--diff-filter=d").splitlines())
    arquivos |= set(git("diff", "--name-only", "--diff-filter=d").splitlines())
    novos = git("ls-files", "--others", "--exclude-standard").splitlines()
    arquivos |= set(novos)
    texto = "\n".join(linhas_novas(git("diff", "--cached")) + linhas_novas(git("diff")))
    for novo in novos:
        arquivo = RAIZ / novo
        if arquivo.is_file() and arquivo.stat().st_size <= LIMITE_BYTES:
            texto += "\n" + arquivo.read_text(encoding="utf-8", errors="ignore")
    ruins = [f"{f} ({proibido(f)})" for f in sorted(arquivos) if proibido(f)]
    if re.search(CHAVE_GOOGLE, texto):
        ruins.append("uma chave do Google (AIza...) num arquivo mudado ou novo")
    return ruins


def antes(dados):
    ferramenta = dados.get("tool_name", "")
    entrada = dados.get("tool_input", {})

    if ferramenta == "Bash":
        cmd = entrada.get("command", "")
        # 1. O .env (chave do Gemini) nunca passa pelo Claude; o .env.example pode
        if re.search(r"\.env\b(?!\.example)", cmd):
            bloquear("Bloqueado: o .env guarda a chave do Gemini e não passa pelo Claude (CLAUDE.md, Cuidados). "
                     "Se precisar, a pessoa roda o comando no terminal dela. Não tente outro caminho. " + SAIDA_MENSAGEM)
        # 2. Git perigoso: a regra de permissão só compara o começo do comando; aqui lemos o comando inteiro
        for padrao, motivo in PERIGOSOS:
            if re.search(padrao, cmd):
                bloquear(f"Bloqueado: {motivo} (CLAUDE.md, regra 8). Para trazer a main: git merge main. " + SAIDA_MENSAGEM)
        # 3. Commit: nunca na main e nunca com dado, .env, chave ou arquivo grande (REGRAS-IA.md, seção 2)
        if re.search(GIT + r"commit\b", cmd):
            if git("branch", "--show-current") == "main":
                bloquear("Bloqueado: você está na main. Rode /inicio-de-sessao para criar a branch pessoa-tarefa "
                         "(CLAUDE.md, regra 8).")
            ruins = commit_levaria()
            if ruins:
                bloquear("Bloqueado: o commit pode levar " + "; ".join(ruins) + ". Tire do stage com "
                         "git restore --staged <arquivo>, ponha no .gitignore o que é seu e confira o git status "
                         "(REGRAS-IA.md, seção 2).")
        # 4. As travas e o CI mudados pelo terminal (sed -i, >, rm, mv...)
        if any(t in cmd for t in TRAVAS) and re.search(ESCREVE, cmd):
            perguntar("Este comando muda as travas ou o CI de todos. O grupo sabe? (CLAUDE.md, pastas comuns)")
        # 5. Gemini de verdade gasta crédito pré-pago: pergunta antes.
        #    Atenção: no raiox/ia.py o padrão é COM IA (python -m raiox.ia sem --sem-ia; preparar_raio_x sem usar_ia=False)
        gemini = (re.search(r"""RAIOX_IA_REAL=["']?1|--com-ia|usar_ia\s*=\s*True|rodar_tela_com_ia|gerar_llm\(""", cmd)
                  or (re.search(r"-m\s*raiox\.ia\b", cmd) and "--sem-ia" not in cmd)
                  or ("preparar_raio_x(" in cmd and "usar_ia=False" not in cmd))
        if gemini:
            perguntar("Isto chama o Gemini e gasta crédito (≈ US$ 0,0012 por raio-x). "
                      "Mais de 10 chamadas: avise o grupo antes (CLAUDE.md, Cuidados).")

    if ferramenta in ("Edit", "Write", "NotebookEdit"):
        caminho = entrada.get("file_path") or entrada.get("notebook_path") or ""
        try:
            relativo = Path(caminho).resolve().relative_to(RAIZ).as_posix()
        except ValueError:
            return  # arquivo fora do projeto: não é com este hook
        # 6. As próprias travas e o CI
        if relativo.startswith(TRAVAS):
            perguntar(f"{relativo} muda as travas ou o CI de todos. O grupo sabe? (CLAUDE.md, pastas comuns)")
        # 7. Contrato antes de código (CLAUDE.md, regra 2)
        if relativo == "contratos.md":
            perguntar("O contratos.md é o formato entre as partes. Quem recebe já foi avisado? (CLAUDE.md, regra 2)")
        # 8. Pasta de outro dono (CLAUDE.md, regra 1). Quem sou: RAIOX_PESSOA ou o nome do Git
        dono = dono_de(relativo)
        if dono and " " in dono:  # não é um nome, é uma regra (ex.: docs/professor/, "ninguém edita")
            perguntar(f"{relativo}: {dono} (CLAUDE.md, Estrutura e donos)")
        eu = normalizar(os.environ.get("RAIOX_PESSOA") or git("config", "user.name"))
        if dono and not eu.startswith(normalizar(dono)):
            perguntar(f"{relativo} está na pasta de {dono}. {dono} deu o ok no grupo? (CLAUDE.md, regra 1)")


def fim(dados):
    if dados.get("stop_hook_active"):
        return  # já devolvemos o Claude uma vez; não prende ele num laço infinito
    mudancas = git("status", "--porcelain")
    if not re.search(r'\.(py|ipynb)"?$', mudancas, re.M):
        return  # nenhum código mudou: não gasta os ~10 s dos testes
    # Mesma mudança que já passou? Não roda de novo (a marca fica em .git/, que nunca vai para o Git)
    marca = RAIZ / ".git" / "raiox-testes-ok"
    assinatura = hashlib.sha256((git("diff", "HEAD") + mudancas).encode())
    for novo in git("ls-files", "--others", "--exclude-standard").splitlines():  # arquivo novo não aparece no diff
        if (RAIZ / novo).is_file():
            assinatura.update((RAIZ / novo).read_bytes())
    assinatura = assinatura.hexdigest()
    if marca.is_file() and marca.read_text() == assinatura:
        return
    python = os.environ.get("RAIOX_PYTHON") or (
        str(RAIZ / ".venv/bin/python") if (RAIZ / ".venv/bin/python").exists() else "python3")
    try:
        r = subprocess.run([os.path.expanduser(python), "-m", "pytest", "-q", "-x"],
                           cwd=RAIZ, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as erro:
        print(f"guarda.py: não consegui rodar os testes ({erro}).", file=sys.stderr)
        sys.exit(1)  # código 1 = aviso que não bloqueia
    if "No module named pytest" in r.stderr:
        print("guarda.py: este Python não tem pytest. Ponha RAIOX_PYTHON no seu .claude/settings.local.json "
              "(aprender/claude-code.md).", file=sys.stderr)
        sys.exit(1)
    if r.returncode != 0:
        fim_da_saida = "\n".join(r.stdout.splitlines()[-25:])
        bloquear("Os testes falharam. Conserte antes de dizer pronto (CLAUDE.md, regra 3):\n" + fim_da_saida)
    if marca.parent.is_dir():
        marca.write_text(assinatura)


def inicio(dados):
    ramo = git("branch", "--show-current")
    linhas = [f"Branch atual: {ramo or '(nenhuma)'}."]
    if ramo == "main":
        linhas.append("Está na main: antes de mudar arquivos, rode /inicio-de-sessao.")
    pendentes = git("status", "--short").splitlines()
    if pendentes:
        linhas.append(f"{len(pendentes)} arquivo(s) com mudança sem commit: "
                      + ", ".join(p[3:] for p in pendentes[:5]))
    plano = RAIZ / "docs" / "PLANO.md"
    nota = re.search(r"\*\*Em ([^*]+)\*\*", plano.read_text(encoding="utf-8")) if plano.is_file() else None
    if nota:
        linhas.append(f"A seção 0 do PLANO foi escrita em {nota.group(1)} Confira no GitHub se envelheceu.")
    print("\n".join(linhas))


def conferir():
    """Confere o repositório inteiro com a mesma lista do hook. Roda no CI pelo tests/test_guarda.py."""
    ruins = [f"{f}: {proibido(f)}" for f in git("ls-files").splitlines() if proibido(f)]
    ruins += [f"chave do Google em {linha.split(':')[0]}" for linha in git("grep", "-nE", CHAVE_GOOGLE).splitlines()]
    for ruim in ruins:
        print(ruim)
    return 1 if ruins else 0


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "conferir":
        sys.exit(conferir())
    dados = {} if sys.stdin.isatty() else json.loads(sys.stdin.read() or "{}")
    try:
        {"inicio": inicio, "antes": antes, "fim": fim}[modo](dados)
    except SystemExit:
        raise
    except Exception as erro:
        # Bug no hook não pode travar o trabalho: avisa e libera (código 1 não bloqueia).
        # As travas duras são as regras deny do .claude/settings.json e o CI.
        print(f"guarda.py ({modo}): {erro!r}", file=sys.stderr)
        sys.exit(1)
