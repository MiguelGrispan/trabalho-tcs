"""
Script de Cálculo de Indicadores
Objetivo: Gerar o arquivo indicadores.csv (Contrato C2) para o Eduardo.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


COLUNAS_SAIDA = [
    "cd_cvm", "nome", "setor", "ano", "receita", "receita_2a_antes",
    "cresc_2a", "margem_ebit", "margem_liquida", "ativo_total",
    "endividamento", "origem", "versao",
]
CONTAS = {"3.01": "receita", "3.05": "ebit", "3.11": "lucro", "1": "ativo", "2.03": "pl"}


def calcular():
    caminho_contas = DATA_DIR / "contas.csv"
    df = pd.read_csv(
        caminho_contas,
        sep=";",
        encoding="utf-8-sig",
        decimal=",",
        dtype={"cd_cvm": str, "cd_conta": str},
    )
    obrigatorias = {
        "ano", "cd_cvm", "nome", "setor", "cd_conta", "valor",
        "demonstracao", "origem", "versao",
    }
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise ValueError(
            f"{caminho_contas} não contém as colunas obrigatórias: "
            f"{', '.join(sorted(ausentes))}. Rode scripts/carregar_dfp.py."
        )

    df["cd_conta"] = df["cd_conta"].astype("string").str.strip()
    df["ano"] = pd.to_numeric(df["ano"], errors="raise").astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    # contas.csv já vem limpo de carregar_dfp.py (regras em raiox/limpeza.py):
    # uma linha por conta e só empresas com receita de venda positiva.
    df = df.loc[df["cd_conta"].isin(list(CONTAS))].copy()

    resultado = _montar_indicadores(df) if not df.empty else pd.DataFrame(columns=COLUNAS_SAIDA)
    resultado.to_csv(
        DATA_DIR / "indicadores.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
        decimal=",",
    )
    return resultado


def _montar_indicadores(df):
    """Uma linha por empresa no ano mais recente, com os indicadores do C2."""
    # pivot (e não pivot_table) falha se houver conta repetida, em vez de escolher uma.
    pivot = (
        df.pivot(index=["ano", "cd_cvm", "nome"], columns="cd_conta", values="valor")
        .reindex(columns=list(CONTAS))
        .rename(columns=CONTAS)
        .reset_index()
    )

    ano_atual = int(df["ano"].max())
    base = pivot[pivot["ano"] == ano_atual].copy()
    ref = pivot.loc[pivot["ano"] == ano_atual - 2, ["cd_cvm", "receita"]]
    base = base.merge(
        ref.rename(columns={"receita": "receita_2a_antes"}), on="cd_cvm", how="left"
    )

    receita = base["receita"]
    ebit = base["ebit"]
    lucro = base["lucro"]
    ativo = base["ativo"]
    patrimonio_liquido = base["pl"]
    receita_anterior = base["receita_2a_antes"]

    base["cresc_2a"] = (
        receita.div(receita_anterior).sub(1).where(receita_anterior.gt(0))
    )
    base["margem_ebit"] = ebit.div(receita).where(receita.gt(0))
    base["margem_liquida"] = lucro.div(receita).where(receita.gt(0))
    base["ativo_total"] = ativo
    base["endividamento"] = (
        1 - patrimonio_liquido.div(ativo)
    ).where(ativo.gt(0))

    dre = df.loc[
        df["demonstracao"].eq("DRE")
        & df["ano"].eq(ano_atual)
        & df["cd_conta"].eq("3.01"),
        ["cd_cvm", "setor", "origem", "versao"],
    ].drop_duplicates("cd_cvm", keep="first")
    base = base.merge(dre, on="cd_cvm", how="left")
    base["setor"] = base["setor"].fillna("Não Informado")
    return base.reindex(columns=COLUNAS_SAIDA).sort_values("nome")


if __name__ == "__main__":
    calcular()