"""
Testes da guarda do Claude Code (.claude/hooks/guarda.py) e da configuração do projeto (.claude/settings.json).
Rodar na raiz do repositório:  python -m pytest -q tests/test_guarda.py

O guarda.py roda como o Claude Code o roda: um processo que recebe um JSON pela entrada padrão.
  código 2      → bloqueia (a ação não acontece)
  JSON com ask  → pergunta à pessoa
  nada          → libera
Os testes com Git usam um repositório de mentira numa pasta temporária: nada muda no repositório de verdade.
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
    "git push origin miguel-tela --force",      # o --force no fim: a regra deny do settings.json não pega; o hook pega
    "git push -f origin miguel-tela",
    "git rebase main",
    "git reset --hard HEAD~1",
    "git clean -fdx",
    "git add -f data/contas.csv",
    f"python3 - <<'EOF'\nprint(open('{ENV}').read())\nEOF",   # heredoc fora de commit e PR é código: continua conferido
    # achados do revisor no PR #30: o shell executa $( ) dentro da mensagem, então ela não pode esconder o comando
    f'gh issue create --title "x" --body "$(cat {ENV})"',
    f'git commit -m "$(cat <<EOF\n$(cat {ENV})\nEOF\n)"',     # heredoc com EOF sem aspas: o shell executa o $( )
    "git pull --rebase origin main",
    "git -C ../outra-pasta push origin miguel-tela --force",
    "cd app && git rebase main",
])
def test_bloqueia_env_e_git_que_apaga_trabalho(comando):
    r = bash(comando)
    assert decisao(r) == "bloqueia"
    assert "Bloqueado" in r.stderr


@pytest.mark.parametrize("comando", [
    "RAIOX_IA_REAL=1 streamlit run app/streamlit_app.py",
    "python -m avaliacao.avaliar --com-ia",
    "python -m raiox.ia --cvm 5410 --produto ERP --objetivo venda",   # sem --sem-ia, o raiox.ia chama o Gemini
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
    "python -m raiox.ia --cvm 5410 --produto ERP --objetivo venda --sem-ia",
    "python -m avaliacao.avaliar",
    'grep -rn "git rebase" docs/',                             # procurar o texto não é rodar o comando
    'python -c "from raiox.ia import validar_e_preencher"',   # importar não chama o Gemini
])
def test_libera_o_trabalho_normal(comando):
    assert decisao(bash(comando)) == "libera"


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
    ("miguel", ".github/workflows/testes.yml", "ask"),
])
def test_pergunta_antes_de_mexer_em_pasta_de_outro_dono(pessoa, arquivo, esperado):
    assert decisao(editar(arquivo, pessoa=pessoa)) == esperado


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
    r = bash('git commit -m "teste"', raiz=repo)
    assert decisao(r) == "bloqueia"
    assert "main" in r.stderr


@precisa_git
def test_bloqueia_commit_com_dado_ou_chave(repo):
    (repo / "data").mkdir()
    (repo / "data" / "contas.csv").write_text("a,b\n1,2\n")
    git(repo, "add", "-f", "data/contas.csv")
    r = bash('git commit -m "dados"', raiz=repo)
    assert decisao(r) == "bloqueia"
    assert "data/contas.csv" in r.stderr

    git(repo, "restore", "--staged", "data/contas.csv")
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    git(repo, "add", "config.py")
    assert "chave do Google" in bash('git commit -m "config"', raiz=repo).stderr


@precisa_git
def test_libera_commit_limpo_mesmo_que_a_mensagem_fale_de_env_e_rebase(repo):
    (repo / "novo.py").write_text("x = 1\n")
    git(repo, "add", "novo.py")
    assert decisao(bash(f'git commit -m "explica por que o {ENV} e o git rebase são proibidos"', raiz=repo)) == "libera"
    # o jeito que o Claude Code escreve mensagem longa: heredoc, com "aspas" no meio
    heredoc = f'git commit -m "$(cat <<\'EOF\'\nO "{ENV}" fica fora; nada de git rebase.\nEOF\n)"'
    assert decisao(bash(heredoc, raiz=repo)) == "libera"
    # no meio de um comando composto também (achado do revisor)
    (repo / "outro.py").write_text("y = 2\n")
    assert decisao(bash(f'git add outro.py && git commit -m "fala do {ENV}"', raiz=repo)) == "libera"


def test_libera_pr_cuja_descricao_fala_do_env():
    corpo = f'gh pr create --title "Travas" --body "$(cat <<\'EOF\'\nDeny para ler o "{ENV}".\nEOF\n)"'
    assert decisao(bash(corpo)) == "libera"
    assert decisao(bash(f'git push -u origin x && {corpo}')) == "libera"
    assert decisao(bash(corpo + f" && cat {ENV}")) == "bloqueia"     # o que vem depois da mensagem continua conferido


@precisa_git
def test_commit_com_add_no_mesmo_comando_confere_o_que_o_add_vai_por(repo):
    """O hook roda antes do comando: o git add ainda não aconteceu, então ele olha os arquivos novos e mudados."""
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    r = bash('git add . && git commit -m "config"', raiz=repo)
    assert decisao(r) == "bloqueia" and "chave do Google" in r.stderr

    (repo / "config.py").unlink()
    with open(repo / "grande.bin", "wb") as f:
        f.truncate(10 * 1024 * 1024 + 1)
    r = bash(f'git -C {repo} add -A && git -C {repo} commit -m "grande"', raiz=repo)
    assert decisao(r) == "bloqueia" and "acima de 10 MB" in r.stderr


@precisa_git
def test_libera_o_commit_que_apaga_uma_chave_vazada(repo):
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    git(repo, "add", "config.py")
    git(repo, "commit", "-qm", "erro")                     # entrou sem passar pelo hook (ex.: fora do Claude Code)
    (repo / "config.py").write_text('CHAVE = ""\n')
    git(repo, "add", "config.py")
    assert decisao(bash('git commit -m "tira a chave"', raiz=repo)) == "libera"


@precisa_git
def test_libera_commit_na_branch_nova_criada_no_mesmo_comando(repo):
    git(repo, "switch", "-q", "main")
    assert decisao(bash('git switch -c eduardo-nova && git commit -m "x"', raiz=repo)) == "libera"
    assert decisao(bash(f'git -C {repo} commit -m "x"', raiz=repo)) == "bloqueia"


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
    git(repo, "switch", "-q", "main")
    assert "/inicio-de-sessao" in rodar("inicio", raiz=repo).stdout


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
    (repo / "data" / "contas.csv").write_text("a\n")
    (repo / "data" / "relatório.csv").write_text("a\n")    # com acento, o Git põe o nome entre aspas se não avisarmos
    (repo / f"{ENV}.local").write_text("SENHA=x\n")         # qualquer .env, não só o de nome exato
    (repo / "config.py").write_text(f'CHAVE = "{CHAVE_FALSA}"\n')
    git(repo, "add", "-f", "data/contas.csv", "data/relatório.csv", f"{ENV}.local", "config.py")
    git(repo, "commit", "-qm", "erro de propósito")
    r = rodar("conferir", raiz=repo)
    assert r.returncode == 1
    for esperado in ("data/contas.csv", "data/relatório.csv", f"{ENV}.local", "chave do Google em config.py"):
        assert esperado in r.stdout


# ---------------------------------------------------------------- configuração
def test_settings_do_projeto_liga_a_guarda_e_as_travas():
    config = json.loads((PASTA / ".claude" / "settings.json").read_text(encoding="utf-8"))
    regras = config["permissions"]
    assert f"Read({ENV})" in regras["deny"]
    assert "Bash(git push --force *)" in regras["deny"]
    assert "Bash(gh pr merge *)" in regras["ask"]          # o "pode" antes do merge, até no modo bypass
    comandos = {evento: grupo["hooks"][0]["command"] for evento, grupos in config["hooks"].items() for grupo in grupos}
    assert comandos.keys() == {"SessionStart", "PreToolUse", "Stop"}
    for evento, modo in [("SessionStart", "inicio"), ("PreToolUse", "antes"), ("Stop", "fim")]:
        assert comandos[evento].endswith(f'.claude/hooks/guarda.py" {modo}')


def test_revisor_so_le():
    texto = (PASTA / ".claude" / "agents" / "revisor.md").read_text(encoding="utf-8")
    cabecalho = texto.split("---")[1]
    ferramentas = next(linha for linha in cabecalho.splitlines() if linha.startswith("tools:"))
    assert "Edit" not in ferramentas and "Write" not in ferramentas
