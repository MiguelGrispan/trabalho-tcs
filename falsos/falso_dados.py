"""
Falso do contrato C1 (raiox/dados.py do Marcos). Mesmas funções, sem banco de dados:
lista as empresas da mesma tabela que o raiox/ia.py usa (a falsa, enquanto não houver data/indicadores.csv).
"""
from raiox.segmentos import carregar_indicadores


def buscar_empresas(texto: str) -> list[dict]:
    """Empresas cujo nome contém o texto, ordenadas por nome."""
    df, _ = carregar_indicadores()
    achadas = df[df["nome"].str.upper().str.contains(texto.strip().upper(), regex=False)].sort_values("nome")
    return [{"cd_cvm": int(e.cd_cvm), "nome": e.nome, "setor": e.setor} for e in achadas.itertuples()]


def registrar_consulta(registro: dict) -> None:
    """No real, grava uma linha na tabela consultas do catalogo.db. Aqui só mostra no terminal."""
    print("[consulta registrada]", registro)
