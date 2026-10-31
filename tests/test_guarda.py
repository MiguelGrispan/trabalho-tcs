"""
Testes da guarda do Claude Code (.claude/hooks/guarda.py) e da configuração do projeto (.claude/settings.json).
Rodar na raiz do repositório:  python -m pytest -q tests/test_guarda.py

O guarda.py roda como o Claude Code o roda: um processo que recebe um JSON pela entrada padrão.
  código 2      → bloqueia (a ação não acontece)
  JSON com ask  → pergunta à pessoa
  nada          → libera
Os testes com Git usam um repositório de mentira numa pasta temporária: nada muda no repositório de verdade.
Muitos casos vieram do subagent revisor, que revisou o PR #30 duas vezes e achou furos nas duas.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PASTA = Path(__file__).resolve().parent.parent
GUARDA = PASTA / ".claude" / "hooks" / "guarda.py"
ENV = "." + "env"                      # escrito assim para o próprio hook não bloquear quem roda grep neste arquivo
CHAVE_FALSA = "AIza" + "x" * 35        # parece uma chave do Google, mas não é
URL_SENHA_FALSA = "postgresql://postgres:" + "Abc12345" + "@servidor:5432/raiox"   # montada em pedaços pelo mesmo motivo

TEM_GIT = shutil.which("git") is not None
precisa_git = pytest.mark.skipif(not TEM_GIT, reason="sem git (ex.: dentro do contêiner)")
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "Teste", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "Teste", "GIT_COMMITTER_EMAIL": "t@t"}


def rodar(modo, dados=None, raiz=PASTA, pessoa="eduardo", **env):
    return subprocess.run([sys.executable, str(GUARDA), modo], input=json.dumps(dados or {}),
                          capture_output=True, text=True,
                          env={**os.environ, "CLAUDE_PROJECT_DIR": str(raiz), "RAIOX_PESSOA": pessoa, **env})


def decisao(r):
    if r.returncode == 2:
        return "bloqueia"
    if r.stdout.strip():
        return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
    assert r.returncode == 0, r.stderr
    return "libera"


def bash(comando, **kw):
    return rodar("antes", {"tool_name": "Bash", "tool_input": {"command": comando}}, **kw)


def editar(relativo, raiz=PASTA, **kw):
    return rodar("antes", {"tool_name": "Edit", "tool_input": {"file_path": str(raiz / relativo)}}, raiz=raiz, **kw)


def git(raiz, *args):
    return subprocess.run(["git", "-C", str(raiz), *args], check=True, capture_output=True, text=True, env=GIT_ENV)


@pytest.fixture
def repo(tmp_path):
    """Repositório de mentira, com o CLAUDE.md e o PLANO de verdade, numa branch de trabalho."""
    for nome in ("CLAUDE.md", "docs/PLANO.md"):
        destino = tmp_path / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text((PASTA / nome).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / ".gitignore").write_text("data/*\n.pytest_cache/\n__pycache__/\n")
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "base")
    git(tmp_path, "switch", "-q", "-c", "eduardo-teste")
    return tmp_path


# ---------------------------------------------------------------- comandos (PreToolUse, Bash)
@pytest.mark.parametrize("comando", [
    f"cat {ENV}",
    f"grep GOOGLE {ENV}",
    f'cat -b "{ENV}"',
    f"echo oi\ncat {ENV}",
    f"python3 - <<'EOF'\nprint(open('{ENV}').read())\nEOF",
    f'gh issue create --title "x" --body "$(cat {ENV})"',            # o shell executa o $( ) da mensagem
    f'gh issue create --body "`cat {ENV}`"',
    f"echo '-m \"'; cat {ENV}; echo '\"'",                           # aspas que enganavam a 2ª versão
    f"git commit -m \"$(cat <<'EOF'\nmsg\nEOF\ncat {ENV}\nEOF\n)\"",  # heredoc que fecha antes do que parece
    f'git commit -m "explica o {ENV}"',                              # só texto? vai por arquivo (-F); ver abaixo
    f"cat {ENV.upper()}",                                            # o disco do Mac não diferencia maiúscula
    f"cat {ENV}_prod",
])
def test_bloqueia_qualquer_comando_que_cite_o_env(comando):
    r = bash(comando)
    assert decisao(r) == "bloqueia"
    assert "-F <arquivo>" in r.stderr          # a mensagem de bloqueio ensina a saída certa


@pytest.mark.parametrize("comando", [
    'grep -rn "AIza" .',                       # "onde a chave é usada?": o grep na pasta inteira lê o .env (3ª revisão)
    "grep -rn GOOGLE_API_KEY .",
    "rg AIza",
    "find . -name '.*' -exec cat {} +",
    "cat .e*",
    'python -c "from dotenv import dotenv_values; print(dotenv_values())"',
    "docker compose config",                   # o compose mostra as variáveis já lidas do .env
    "printenv",
])
def test_bloqueia_busca_que_le_o_env_sem_citar_o_nome(comando):
    r = bash(comando)
    assert decisao(r) == "bloqueia"
    assert "ferramenta Grep" in r.stderr


@pytest.mark.parametrize("comando", [
    "git push origin miguel-tela --force",      # o --force no fim: a regra deny do settings.json não pega; o hook pega
    "git push -f origin miguel-tela",
    "git push -uf origin miguel-tela",
    "git push origin +main",
    "git -C ../outra-pasta push origin miguel-tela --force",
    "git rebase main",
    "git --no-pager rebase main",
    'git -C "minha pasta" rebase main',
    "cd app && git rebase main",
    "echo oi\ngit rebase main",                 # comando em linha nova (achado da 2ª revisão)
    "if true; then git push --force; fi",
    "bash -c 'git reset --hard'",
    "echo main | xargs git rebase",
    "git pull --rebase origin main",
    "git pull -r",
    "git reset --hard HEAD~1",
    "git clean -fdx",
    "git add -f data/contas.csv",
    "git add -fA",
    "git config pull.rebase true",               # o que o próprio Git sugere quando o pull diverge
    "git -c pull.rebase=true pull",
    'git commit --no-verify -m "x"',              # pularia o pre-commit
    "git -c core.hooksPath=/dev/null commit -m x",
    "git config --unset core.hooksPath",
    "git push origin main",                       # main só por PR (o GitHub também recusa)
    "git push origin HEAD:main",
    "git push --mirror origin",
    "git push origin --delete miguel-tela",
    "git push origin :miguel-tela",
    "git push origin '+main'",
    "git push --force-if-includes origin x",
    "git stage -f data/contas.csv",
    "git reset --har HEAD~1",                     # o Git aceita a opção abreviada
    'git -c "a b=c" rebase main',
])
def test_bloqueia_git_que_apaga_trabalho(comando):
    r = bash(comando)
    assert decisao(r) == "bloqueia"
    assert "Bloqueado" in r.stderr


@pytest.mark.parametrize("comando", [
    "RAIOX_IA_REAL=1 streamlit run app/streamlit_app.py",
    'RAIOX_IA_REAL="1" streamlit run app/streamlit_app.py',
    "python -m avaliacao.avaliar --com-ia",
    "python -m raiox.ia --cvm 5410 --produto ERP --objetivo venda",   # sem --sem-ia, o raiox.ia chama o Gemini
    "python3.11 -mraiox.ia --cvm 5410",
    'python -c "from raiox.ia import gerar_llm; gerar_llm({}, [])"',
    "bash aprender/atalhos/rodar_tela_com_ia.command",                # o atalho liga o Gemini por dentro
])
def test_pergunta_antes_de_gastar_credito_do_gemini(comando):
    r = bash(comando)
    assert decisao(r) == "ask"
    assert "Gemini" in r.stdout


@pytest.mark.parametrize("comando", [
    f"cat {ENV}.example",
    "python -m pytest -q",
    ".venv/bin/python -c 'import os; print(os.environ)'",
    "git push -u origin miguel-tela",
    "git push --set-upstream origin feature-fix",
    "git pull",
    "git log --oneline -5",
    "python -m raiox.ia --cvm 5410 --produto ERP --objetivo venda --sem-ia",
    "python -m avaliacao.avaliar",
    'python -c "from raiox.ia import validar_e_preencher"',   # importar não chama o Gemini
    "gh pr create --title 'Travas' --body-file /tmp/corpo.md",  # mensagem por arquivo: a saída certa
    "cat .claude/hooks/guarda.py",                              # ler as travas pode
    "git grep -n AIza",                                         # git grep só lê arquivos do Git
    "grep -n validar raiox/ia.py",                              # grep num arquivo pode
    "find . -name '*.py'",
    "git config core.hooksPath .githooks",                      # ligar o pre-commit pode
    "git push origin v1.0",                                     # tag pode
    "git push -u origin eduardo-main-fix",                      # "main" dentro do nome da branch pode
])
def test_libera_o_trabalho_normal(comando):
    assert decisao(bash(comando)) == "libera"


def test_pergunta_antes_de_mudar_as_travas_pelo_terminal():
    assert decisao(bash("sed -i '' 's/2/0/' .claude/hooks/guarda.py")) == "ask"
    assert decisao(bash("echo x >> .github/workflows/testes.yml")) == "ask"


# ---------------------------------------------------------------- arquivos (PreToolUse, Edit e Write)
@pytest.mark.parametrize("pessoa, arquivo, esperado", [
    ("eduardo", "app/streamlit_app.py", "ask"),            # pasta do Miguel
    ("miguel", "app/streamlit_app.py", "libera"),
    ("marcos", "Dockerfile", "ask"),
    ("eduardo", "raiox/ia.py", "libera"),
    ("eduardo", "avaliacao/avaliar.py", "libera"),         # o caminho mais específico vence...
    ("eduardo", "avaliacao/regras_prompt.md", "ask"),      # ...o resto de avaliacao/ é da Náthally
    ("nathally", "docs/produto/persona.md", "libera"),     # sem acento também vale
    ("eduardo", "docs/professor/requisitos_projeto.MD", "ask"),
    ("eduardo", "docs/PLANO.md", "libera"),                # pasta comum: o /fim-de-sessao edita sempre
    ("eduardo", "contratos.md", "ask"),
    ("eduardo", ".claude/settings.json", "ask"),           # as travas e o CI mudam a máquina e os PRs de todos
    ("eduardo", ".claude/hooks/guarda.py", "ask"),
    ("eduardo", ".claude/agents/revisor.md", "ask"),
    ("eduardo", "tests/test_guarda.py", "ask"),
    ("miguel", ".github/workflows/testes.yml", "ask"),
    ("eduardo", ".claude/settings.local.json", "ask"),      # aceita disableAllHooks: desligaria tudo
    ("eduardo", ".githooks/pre-commit", "ask"),
    ("eduardo", "CLAUDE.md", "ask"),                       # a tabela de donos e as travas moram nele
    ("eduardo", ".gitignore", "ask"),                      # tirar o .env dali desligaria a proteção
    ("eduardo", ".claude/skills/fim-de-sessao/SKILL.md", "ask"),
])
def test_pergunta_antes_de_mexer_em_pasta_de_outro_dono(pessoa, arquivo, esperado):
    assert decisao(editar(arquivo, pessoa=pessoa)) == esperado


def test_multiedit_tambem_passa_pela_guarda():
    r = rodar("antes", {"tool_name": "MultiEdit", "tool_input": {"file_path": str(PASTA / "app" / "streamlit_app.py")}})
    assert decisao(r) == "ask"


def test_mensagem_diz_de_quem_e_a_pasta():
    assert "Miguel" in editar("infra/main.tf").stdout
    assert "ninguém edita" in editar("docs/professor/guia_projeto_final.pdf").stdout


def test_arquivo_fora_do_projeto_nao_e_com_a_guarda(tmp_path):
    r = rodar("antes", {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "x.py")}})
    assert decisao(r) == "libera"


def test_tabela_de_donos_do_claude_md_continua_legivel():
    """O hook lê a tabela do CLAUDE.md. Se alguém mudar o formato dela, este teste avisa."""
    spec = importlib.util.spec_from_file_location("guarda", GUARDA)
    guarda = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guarda)
    assert guarda.dono_de("app/streamlit_app.py") == "Miguel"
    assert guarda.dono_de("raiox/ia.py") == "Eduardo"
    assert guarda.dono_de("scripts/carregar_dfp.py") == "Marcos"
    assert guarda.dono_de("avaliacao/regras_prompt.md") == "Náthally"
    assert guarda.dono_de("docs/PLANO.md") is None


# ---------------------------------------------------------------- commit
@precisa_git
def test_bloqueia_commit_na_main(repo):
    git(repo, "switch", "-q", "main")
    for comando in ('git commit -m "teste"', f'git -C {repo} commit -m "x"', 'git commit -m "x" && git switch -c nova'):
        r = bash(comando, raiz=repo)
        assert decisao(r) == "bloqueia" and "main" in r.stderr, comando


@precisa_git
def test_libera_commit_limpo_com_mensagem_por_arquivo(repo, tmp_path_factory):
    mensagem = tmp_path_factory.mktemp("msg") / "mensagem.txt"
    mensagem.write_text(f"Explica por que o {ENV} e o git rebase são proibidos.\n")
    (repo / "novo.py").write_text("x = 1\n")
    git(repo, "add", "novo.py")
    assert decisao(bash(f"git commit -F {mensagem}", raiz=repo)) == "libera"
    assert decisao(bash('git add novo.py && git commit -m "novo"', raiz=repo)) == "libera"


@precisa_git
def test_bloqueia_commit_com_dado_ou_chave(repo):
    (repo / "data").mkdir()
    (repo / "data" / "contas.csv").write_text("a,b\n1,2\n")
    git(repo, "add", "-f", "data/contas.csv")
    r = bash('git commit -m "dados"', raiz=repo)
    assert decisao(r) == "bloqueia" and "data/contas.csv" in r.stderr

    git(repo, "restore", "--staged", "data/contas.csv")
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    git(repo, "add", "config.py")
    assert "chave do Google" in bash('git commit -m "config"', raiz=repo).stderr


@precisa_git
@pytest.mark.parametrize("comando", [
    'git add . && git commit -m "x"',
    'git add .\ngit commit -m "x"',
    'git commit -am "x"',
    "bash -c 'git add -A && git commit -m x'",
])
def test_commit_confere_o_que_esta_solto_na_pasta(repo, comando):
    """O hook roda antes do comando: não sabe o que um git add vai pôr no stage. Por isso confere tudo o que está
    mudado ou novo na pasta (fora do .gitignore). Na dúvida, bloqueia."""
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    r = bash(comando, raiz=repo)
    assert decisao(r) == "bloqueia" and "chave do Google" in r.stderr


@precisa_git
def test_commit_confere_arquivo_grande_e_arquivo_rastreado_mudado(repo):
    with open(repo / "grande.bin", "wb") as f:
        f.truncate(10 * 1024 * 1024 + 1)
    assert "acima de 10 MB" in bash('git add -A && git commit -m "grande"', raiz=repo).stderr
    (repo / "grande.bin").unlink()
    (repo / "config.py").write_text("CHAVE = ''\n")
    git(repo, "add", "config.py")
    git(repo, "commit", "-qm", "config")
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')    # rastreado e mudado, ainda fora do stage
    assert "chave do Google" in bash('git commit -am "x"', raiz=repo).stderr


@precisa_git
def test_libera_o_commit_que_tira_do_git_uma_chave_ou_um_dado(repo):
    (repo / "data").mkdir()
    (repo / "data" / "contas.csv").write_text("a\n")
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    git(repo, "add", "-f", "data/contas.csv", "config.py")
    git(repo, "commit", "-qm", "erro")                     # entrou sem passar pelo hook (ex.: fora do Claude Code)
    (repo / "config.py").write_text('CHAVE = ""\n')
    git(repo, "add", "config.py")
    git(repo, "rm", "-q", "--cached", "data/contas.csv")
    assert decisao(bash('git commit -m "tira a chave e o dado"', raiz=repo)) == "libera"


@precisa_git
def test_commit_com_senha_de_banco_de_verdade_e_bloqueado(repo):
    (repo / "config.py").write_text(f'URL = "{URL_SENHA_FALSA}"\n')
    assert "senha de banco" in bash('git add config.py && git commit -m "x"', raiz=repo).stderr
    (repo / "config.py").write_text('URL = "postgresql://postgres:postgres@localhost:5432/raiox"\n')  # a de teste local
    assert decisao(bash('git add config.py && git commit -m "x"', raiz=repo)) == "libera"


@precisa_git
@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="o root lê qualquer arquivo")
def test_commit_que_nao_da_para_conferir_e_bloqueado(repo):
    """Na dúvida, bloqueia: um arquivo novo que o hook não consegue ler pode ter a chave (3ª revisão)."""
    segredo = repo / "segredo.py"
    segredo.write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    segredo.chmod(0)
    try:
        assert decisao(bash('git add -A && git commit -m "x"', raiz=repo)) == "bloqueia"
    finally:
        segredo.chmod(0o644)


# ---------------------------------------------------------------- pre-commit do Git (.githooks/pre-commit)
@pytest.fixture
def repo_com_precommit(repo):
    """O repositório de mentira com o pre-commit do time ligado, como o /inicio-de-sessao liga."""
    git(repo, "config", "core.hooksPath", str(PASTA / ".githooks"))
    return repo


def commitar(raiz, *args):
    """Commit de verdade, pelo Git (o pre-commit roda), como no terminal ou no VS Code."""
    return subprocess.run(["git", "-C", str(raiz), "commit", "-q", *args], capture_output=True, text=True, env=GIT_ENV)


def test_precommit_e_executavel():
    assert os.access(PASTA / ".githooks" / "pre-commit", os.X_OK)


@precisa_git
def test_precommit_cancela_o_que_o_hook_do_claude_nao_ve(repo_com_precommit):
    repo = repo_com_precommit
    # o arquivo nasce e entra no stage no mesmo comando: só o Git, na hora do commit, vê
    subprocess.run(f"echo 'K=\"{CHAVE_FALSA}\"' > cfg.py && git add -A", shell=True, cwd=repo, check=True)
    r = commitar(repo, "-m", "x")
    assert r.returncode != 0 and "chave do Google" in r.stderr
    git(repo, "restore", "--staged", "cfg.py")
    (repo / "cfg.py").unlink()

    (repo / "data").mkdir()
    (repo / "data" / "contas.csv").write_text("a\n")
    git(repo, "add", "-f", "data/contas.csv")
    r = commitar(repo, "-m", "x")
    assert r.returncode != 0 and "data/contas.csv" in r.stderr
    git(repo, "restore", "--staged", "data/contas.csv")

    (repo / "novo.py").write_text("x = 1\n")
    git(repo, "add", "novo.py")
    assert commitar(repo, "-m", "limpo").returncode == 0


@precisa_git
def test_precommit_cancela_commit_na_main(repo_com_precommit):
    repo = repo_com_precommit
    git(repo, "switch", "-q", "main")
    (repo / "novo.py").write_text("x = 1\n")
    git(repo, "add", "novo.py")
    r = commitar(repo, "-m", "x")
    assert r.returncode != 0 and "main" in r.stderr


@precisa_git
def test_pre_merge_commit_cancela_merge_que_cria_commit_na_main(repo_com_precommit):
    repo = repo_com_precommit
    (repo / "a.py").write_text("a = 1\n")
    git(repo, "add", "a.py")
    git(repo, "commit", "-qm", "na branch")
    git(repo, "switch", "-q", "main")
    (repo / "b.py").write_text("b = 1\n")
    git(repo, "add", "b.py")
    git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "na main, só para o teste divergir")
    r = subprocess.run(["git", "-C", str(repo), "merge", "--no-ff", "-m", "merge", "eduardo-teste"],
                       capture_output=True, text=True, env=GIT_ENV)
    assert r.returncode != 0 and "main" in r.stderr


# ---------------------------------------------------------------- fim da resposta (Stop)
@precisa_git
def test_stop_nao_roda_testes_sem_codigo_mudado(repo):
    assert rodar("fim", raiz=repo).returncode == 0


@precisa_git
def test_stop_devolve_o_claude_quando_o_teste_falha(repo):
    (repo / "test_x.py").write_text("def test_x():\n    assert False\n")
    r = rodar("fim", raiz=repo, RAIOX_PYTHON=sys.executable)
    assert r.returncode == 2
    assert "Os testes falharam" in r.stderr
    # na 2ª vez o Claude Code avisa que já devolveu uma vez: libera, para não virar laço infinito
    assert rodar("fim", {"stop_hook_active": True}, raiz=repo, RAIOX_PYTHON=sys.executable).returncode == 0


@precisa_git
def test_stop_lembra_do_que_ja_passou_e_roda_de_novo_quando_muda(repo):
    teste = repo / "test_x.py"
    teste.write_text("def test_x():\n    assert True\n")
    assert rodar("fim", raiz=repo, RAIOX_PYTHON=sys.executable).returncode == 0
    assert (repo / ".git" / "raiox-testes-ok").is_file()
    teste.write_text("def test_x():\n    assert 1 == 2\n")
    assert rodar("fim", raiz=repo, RAIOX_PYTHON=sys.executable).returncode == 2


# ---------------------------------------------------------------- começo da sessão (SessionStart)
@precisa_git
def test_inicio_diz_a_branch_e_a_data_do_plano(repo):
    saida = rodar("inicio", raiz=repo).stdout
    assert "Branch atual: eduardo-teste" in saida
    assert "seção 0 do PLANO foi escrita em" in saida
    assert "core.hooksPath" in saida                   # avisa que o pre-commit do time está desligado neste clone
    git(repo, "switch", "-q", "main")
    assert "/inicio-de-sessao" in rodar("inicio", raiz=repo).stdout
    git(repo, "config", "core.hooksPath", ".githooks")
    assert "core.hooksPath" not in rodar("inicio", raiz=repo).stdout


# ---------------------------------------------------------------- o repositório inteiro (roda no CI)
@precisa_git
def test_repositorio_sem_dado_chave_nem_arquivo_grande():
    """A trava que vale para os 4, inclusive para quem sobe arquivo pelo navegador: o CI roda este teste em todo PR."""
    if not (PASTA / ".git").exists():
        pytest.skip("sem .git (ex.: dentro do contêiner)")
    r = rodar("conferir")
    assert r.returncode == 0, "Não pode ir para o Git:\n" + r.stdout


@precisa_git
def test_conferir_acha_dado_e_chave_no_git(repo):
    (repo / "data").mkdir()
    arquivos = {
        "data/contas.csv": "a\n",
        "data/relatório.csv": "a\n",       # com acento, o Git põe o nome entre aspas se não avisarmos
        f"{ENV}.local": "SENHA=x\n",       # qualquer .env, não só o de nome exato
        f"prod{ENV}": "SENHA=x\n",
        "BASE.ZIP": "x",                   # maiúscula também
        "banco.sqlite": "x",
        "config.py": f'CHAVE = "{CHAVE_FALSA}"\n',
        "banco.py": f'URL = "{URL_SENHA_FALSA}"\n',
        "exemplo.py": 'URL = "postgresql://postgres:postgres@localhost:5432/raiox"\n',   # a de teste local pode
        "plano.tfplan": "x",
        "id_rsa": "x",
        "credentials.json": "{}",
    }
    for nome, conteudo in arquivos.items():
        (repo / nome).write_text(conteudo)
    git(repo, "add", "-f", *arquivos)
    git(repo, "commit", "-qm", "erro de propósito")
    r = rodar("conferir", raiz=repo)
    assert r.returncode == 1
    for esperado in ["data/contas.csv", "data/relatório.csv", f"{ENV}.local", f"prod{ENV}", "BASE.ZIP", "banco.sqlite",
                     "plano.tfplan", "id_rsa", "credentials.json",
                     "chave do Google em config.py", "senha de banco em banco.py"]:
        assert esperado in r.stdout
    assert "exemplo.py" not in r.stdout


# ---------------------------------------------------------------- configuração
def test_settings_do_projeto_liga_a_guarda_e_as_travas():
    config = json.loads((PASTA / ".claude" / "settings.json").read_text(encoding="utf-8"))
    regras = config["permissions"]
    assert f"Read({ENV})" in regras["deny"] and f"Read({ENV}.*)" in regras["deny"]
    assert "Bash(git push --force *)" in regras["deny"]
    assert "Bash(gh *merge*)" in regras["ask"]             # a 2ª trava do merge, até no modo bypass
    comandos = {evento: grupo["hooks"][0]["command"] for evento, grupos in config["hooks"].items() for grupo in grupos}
    assert comandos.keys() == {"SessionStart", "PreToolUse", "Stop"}
    assert "MultiEdit" in config["hooks"]["PreToolUse"][0]["matcher"]
    for evento, modo in [("SessionStart", "inicio"), ("PreToolUse", "antes"), ("Stop", "fim")]:
        assert comandos[evento].endswith(f'.claude/hooks/guarda.py" {modo}')


def test_revisor_so_le():
    texto = (PASTA / ".claude" / "agents" / "revisor.md").read_text(encoding="utf-8")
    cabecalho = texto.split("---")[1]
    ferramentas = next(linha for linha in cabecalho.splitlines() if linha.startswith("tools:"))
    assert "Edit" not in ferramentas and "Write" not in ferramentas
