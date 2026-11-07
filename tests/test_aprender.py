"""
O notebook aprender/passo_a_passo.ipynb roda inteiro, do começo ao fim, sem erro.
Ele usa o código real (raiox/), então quebra se uma mudança no código deixar o passo a passo desatualizado.
Não chama a IA. No CI roda com os dados falsos; na sua máquina, com os dados reais se existirem.
"""
from pathlib import Path
import re
import subprocess
import sys

import nbformat
import pytest
from nbclient import NotebookClient

NOTEBOOK = Path(__file__).resolve().parent.parent / "aprender" / "passo_a_passo.ipynb"


def test_notebook_passo_a_passo_roda_inteiro():
    nb = nbformat.read(NOTEBOOK, as_version=4)
    NotebookClient(nb, timeout=180, kernel_name="python3",
                   resources={"metadata": {"path": str(NOTEBOOK.parent)}}).execute()
    saidas = "".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.outputs)
    assert "removidos:" in saidas and "5 passed" in saidas      # o validador e os testes rodaram de verdade


def test_notebook_esta_sem_saidas():
    # o notebook vai para o Git limpo: quem abre roda e prevê, em vez de ler a resposta pronta
    nb = nbformat.read(NOTEBOOK, as_version=4)
    assert all(not c.get("outputs") for c in nb.cells if c.cell_type == "code")


@pytest.mark.parametrize("nome", ["rodar_tela", "rodar_tela_com_ia", "rodar_testes"])
@pytest.mark.skipif(sys.platform == "win32", reason="atalhos .command são para macOS; Windows não exige Bash")
def test_atalho_para_se_nao_consegue_criar_o_ambiente(nome):
    # Exercita só a criação do ambiente, sem abrir tela, instalar pacotes ou chamar IA.
    # Se o Python exigido não estiver instalado, o atalho deve parar antes do pip.
    atalho = NOTEBOOK.parent / "atalhos" / f"{nome}.command"
    criacao = re.search(r"\nelse\n(.*?)\nfi", atalho.read_text(encoding="utf-8"), re.S)
    assert criacao is not None
    resultado = subprocess.run(
        ["bash", "-c", "python3.14() { return 7; }\n" + criacao.group(1)
         + "\nprintf 'continuou fora do ambiente'"],
        capture_output=True, text=True, timeout=5,
    )
    assert resultado.returncode == 1
    assert resultado.stdout == ""
