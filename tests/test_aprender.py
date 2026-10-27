"""
O notebook aprender/passo_a_passo.ipynb roda inteiro, do começo ao fim, sem erro.
Ele usa o código real (raiox/), então quebra se uma mudança no código deixar o passo a passo desatualizado.
Não chama a IA. No CI roda com os dados falsos; na sua máquina, com os dados reais se existirem.
"""
from pathlib import Path

import nbformat
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
