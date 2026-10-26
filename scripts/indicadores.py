"""
Script de Cálculo de Indicadores
Objetivo: Gerar o arquivo indicadores.csv (Contrato C2) para o Eduardo.
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


COLUNAS_SAIDA = [
    "cd_cvm", "nome", "setor", "ano", "receita", "receita_2a_antes",
    "cresc_2a", "margem_ebit", "margem_liquida", "ativo_total",
    "endividamento", "origem", "versao",
]


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
        "ano", "cd_cvm", "nome", "cd_conta", "ds_conta", "valor",
        "demonstracao", "origem",
    }
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise ValueError(
            f"{caminho_contas} não contém as colunas obrigatórias: "
            f"{', '.join(sorted(ausentes))}"
        )
    if "setor" not in df.columns:
        df["setor"] = "Não Informado"
    if "versao" not in df.columns:
        df["versao"] = pd.NA

    df["cd_conta"] = df["cd_conta"].astype("string").str.strip()
    df["ano"] = pd.to_numeric(df["ano"], errors="raise").astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    df = df.loc[
        df["cd_conta"].isin(["3.01", "3.05", "3.11", "1", "2.03"])
    ].copy()

    # Considera apenas empresas cuja conta 3.01 representa receita de vendas.
    chaves_conta = ["ano", "cd_cvm", "demonstracao", "cd_conta"]
    valores_por_chave = df.groupby(chaves_conta, dropna=False)["valor"]
    conflitos_mask = valores_por_chave.transform("nunique").gt(1)
    conflitos = df.loc[conflitos_mask, chaves_conta].drop_duplicates()
    # Só avisa sobre contas que entram no cálculo: todas as do último ano
    # e a receita de dois anos antes (usada no cresc_2a).
    ultimo_ano = df["ano"].max()
    relevantes = conflitos["ano"].eq(ultimo_ano) | (
        conflitos["ano"].eq(ultimo_ano - 2) & conflitos["cd_conta"].eq("3.01")
    )
    conflitos = conflitos.loc[relevantes]
    if not conflitos.empty:
        exemplos = conflitos.head(5).to_dict("records")
        warnings.warn(
            f"{len(conflitos)} combinações de conta têm valores divergentes; "
            f"esses indicadores serão deixados ausentes. Exemplos: {exemplos}",
            RuntimeWarning,
            stacklevel=2,
        )
    df.loc[conflitos_mask, "valor"] = np.nan

    empresas_validas = df.loc[
        df["cd_conta"].eq("3.01")
        & df["valor"].gt(0)
        & df["ds_conta"].astype("string").str.contains(
            "Receita de Venda", case=False, na=False
        ),
        "cd_cvm",
    ].unique()
    df = df[df["cd_cvm"].isin(empresas_validas)]

    if df.empty:
        resultado = pd.DataFrame(columns=COLUNAS_SAIDA)
        resultado.to_csv(
            DATA_DIR / "indicadores.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
            decimal=",",
        )
        return resultado

    pivot = df.pivot_table(
        index=["ano", "cd_cvm", "nome"],
        columns="cd_conta",
        values="valor",
        aggfunc="first",
    ).reset_index()
    pivot = pivot.rename(columns={"3.01": "receita", "3.05": "ebit", "3.11": "lucro", "1": "ativo", "2.03": "pl"})

    ano_atual = int(df["ano"].max())
    ano_referencia = ano_atual - 2
    base = pivot[pivot["ano"] == ano_atual].copy()
    if "receita" not in pivot.columns:
        base["receita"] = np.nan
        ref = pd.DataFrame(columns=["cd_cvm", "receita_2a_antes"])
    else:
        ref = pivot.loc[pivot["ano"] == ano_referencia, ["cd_cvm", "receita"]]
        ref = ref.rename(columns={"receita": "receita_2a_antes"})
    base = base.merge(ref, on="cd_cvm", how="left")

    receita = base.get("receita", pd.Series(np.nan, index=base.index))
    ebit = base.get("ebit", pd.Series(np.nan, index=base.index))
    lucro = base.get("lucro", pd.Series(np.nan, index=base.index))
    ativo = base.get("ativo", pd.Series(np.nan, index=base.index))
    patrimonio_liquido = base.get("pl", pd.Series(np.nan, index=base.index))
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
    resultado = base.reindex(columns=COLUNAS_SAIDA).sort_values("nome")
    resultado.to_csv(
        DATA_DIR / "indicadores.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
        decimal=",",
    )
    return resultado

if __name__ == "__main__":
    calcular()