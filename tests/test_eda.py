"""
O notebook notebooks/eda.ipynb (MA4, a EDA) roda inteiro, do começo ao fim, sem erro.
No teste ele usa sempre os dados falsos (RAIOX_DADOS=falsos), como no CI, que não tem a data/ real:
assim o "Restart & Run All" é conferido em todo PR, e os PNG de docs/graficos/ (dos dados reais) não são tocados.
"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parent.parent
NOTEBOOK = RAIZ / "notebooks" / "eda.ipynb"
PNGS = ["eda_1_nulos.png", "eda_2_distribuicoes.png", "eda_3_extremos.png", "eda_4_cobertura.png"]


def test_notebook_eda_roda_inteiro_com_os_dados_falsos(monkeypatch):
    monkeypatch.setenv("RAIOX_DADOS", "falsos")       # o kernel do notebook herda as variáveis do pytest
    antes = {p: (RAIZ / "docs" / "graficos" / p).stat().st_mtime for p in PNGS if (RAIZ / "docs" / "graficos" / p).exists()}

    nb = nbformat.read(NOTEBOOK, as_version=4)       # lido na memória: o arquivo do Git não muda
    NotebookClient(nb, timeout=180, kernel_name="python3",
                   resources={"metadata": {"path": str(NOTEBOOK.parent)}}).execute()

    saidas = "".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.outputs)
    assert "usando dados falsos? True" in saidas
    assert saidas.count("não foi gravado") == len(PNGS)  # os 4 gráficos foram feitos, nenhum gravado
    assert "- Base:" in saidas and "- Cobertura:" in saidas  # chegou ao resumo, a última célula de código
    depois = {p: (RAIZ / "docs" / "graficos" / p).stat().st_mtime for p in antes}
    assert depois == antes                                # os PNG dos dados reais continuam os mesmos


def test_notebook_eda_vai_para_o_git_com_os_graficos():
    # Ao contrário do aprender/passo_a_passo.ipynb, a EDA é um entregável (guia_projeto_final.pdf §6, "notebooks"):
    # vai para o Git já rodado, para a banca ver os gráficos no GitHub sem rodar nada.
    nb = nbformat.read(NOTEBOOK, as_version=4)
    imagens = sum("image/png" in o.get("data", {}) for c in nb.cells if c.cell_type == "code" for o in c.outputs)
    assert imagens == len(PNGS)
