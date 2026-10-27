"""Regras de limpeza dos dados da CVM.

Todas as regras ficam aqui e são aplicadas uma única vez, em
scripts/carregar_dfp.py. Quem lê contas.csv ou catalogo.db depois
(indicadores, interface) recebe os dados já limpos: uma linha por
empresa/ano/demonstração/conta e só empresas com receita de venda
positiva no exercício mais recente.
"""
import pandas as pd

COLUNAS_CONTA = [
    "cd_cvm", "nome", "cd_conta", "ds_conta", "valor", "ano",
    "demonstracao", "origem", "versao",
]
CHAVES_CONTA = ["ano", "cd_cvm", "demonstracao", "cd_conta"]


def codigo_cvm(valor):
    """Remove espaços e zeros à esquerda do código CVM."""
    codigo = str(valor).strip()
    return codigo.lstrip("0") or "0"


def limpar_demo(df, demo, origem, ano):
    """Normaliza uma demonstração lida do arquivo anual da CVM."""
    obrigatorias = {
        "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
        "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
    }
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise ValueError(
            f"dfp_cia_aberta_{demo}_{origem}_{ano}.csv não contém as colunas "
            f"obrigatórias: {', '.join(sorted(ausentes))}"
        )

    ordem_exercicio = (
        df["ORDEM_EXERC"].astype("string").str.strip().str.upper()
    )
    df = df.loc[ordem_exercicio.eq("ÚLTIMO")].copy()
    df["_versao"] = pd.to_numeric(df["VERSAO"], errors="coerce")
    df = df.loc[df["_versao"].notna()]
    if df.empty:
        return pd.DataFrame(columns=COLUNAS_CONTA)

    maior_versao = df.groupby("CD_CVM")["_versao"].transform("max")
    df = df.loc[df["_versao"].eq(maior_versao)].copy()

    # Algumas empresas enviam mais de um período na mesma versão
    # (ex.: 2023-03-31 e 2023-12-31); fica só o encerramento mais recente.
    df["_fim_exercicio"] = pd.to_datetime(df["DT_FIM_EXERC"], errors="coerce")
    df = df.loc[df["_fim_exercicio"].notna()]
    if df.empty:
        return pd.DataFrame(columns=COLUNAS_CONTA)
    maior_fim = df.groupby("CD_CVM")["_fim_exercicio"].transform("max")
    df = df.loc[df["_fim_exercicio"].eq(maior_fim)].copy()

    escalas = df["ESCALA_MOEDA"].fillna("").str.strip().str.upper()
    fatores = pd.Series(index=df.index, dtype="float64")
    fatores.loc[escalas.str.startswith("MIL")] = 1000
    fatores.loc[
        escalas.str.startswith(("UNIDADE", "REAL"))
    ] = 1
    escalas_invalidas = fatores.isna()
    if escalas_invalidas.any():
        valores = sorted(escalas.loc[escalas_invalidas].unique())
        raise ValueError(f"Escala monetária não reconhecida: {valores}")

    valores = pd.to_numeric(df["VL_CONTA"], errors="raise")
    resultado = pd.DataFrame({
        "cd_cvm": df["CD_CVM"].map(codigo_cvm),
        "nome": df["DENOM_CIA"].astype("string").str.strip(),
        "cd_conta": df["CD_CONTA"].astype("string").str.strip(),
        "ds_conta": df["DS_CONTA"].astype("string").str.strip(),
        "valor": valores * fatores,
        "ano": ano,
        "demonstracao": demo,
        "origem": origem,
        "versao": df["_versao"].astype("int64"),
    })
    # Linhas que só diferem em colunas descartadas (ex.: DT_INI_EXERC) viram iguais.
    resultado = resultado[COLUNAS_CONTA].drop_duplicates()
    return resultado.reset_index(drop=True)


def preferir_consolidado(contas):
    """Mantém dados consolidados; usa individuais quando não há consolidados."""
    chaves = ["ano", "cd_cvm", "demonstracao"]
    if contas.empty or "origem" not in contas.columns:
        return contas.copy()
    tem_consolidado = contas["origem"].eq("con").groupby(
        [contas[coluna] for coluna in chaves], dropna=False
    ).transform("any")
    return contas.loc[contas["origem"].eq("con") | ~tem_consolidado].copy()


def encontrar_conflitos(contas):
    """Retorna todas as linhas com chave empresa/ano/demonstração/conta duplicada."""
    if contas.empty or not set(CHAVES_CONTA).issubset(contas.columns):
        return contas.iloc[0:0].copy()
    duplicadas = contas.duplicated(subset=CHAVES_CONTA, keep=False)
    return contas.loc[duplicadas].copy()


def resolver_conflitos(contas):
    """Deixa uma linha por empresa/ano/demonstração/conta.

    Repetições com o mesmo valor viram uma linha só; com valores diferentes,
    o valor fica ausente em vez de escolher um deles.
    """
    if contas.empty or not set(CHAVES_CONTA).issubset(contas.columns):
        return contas.copy()
    divergentes = (
        contas.groupby(CHAVES_CONTA, dropna=False)["valor"]
        .transform("nunique", dropna=False)
        .gt(1)
    )
    resultado = contas.assign(valor=contas["valor"].mask(divergentes))
    return resultado.drop_duplicates(CHAVES_CONTA).reset_index(drop=True)


def filtrar_empresas_com_receita(contas):
    """Mantém empresas com receita de venda positiva no ano mais recente."""
    if contas.empty:
        return contas.copy()
    # Bancos e seguradoras usam a 3.01 para outras receitas; ficam de fora.
    receita = contas.loc[
        contas["cd_conta"].astype(str).str.strip().eq("3.01")
        & pd.to_numeric(contas["valor"], errors="coerce").gt(0)
        & contas["ds_conta"].astype("string").str.contains(
            "receita de venda", case=False, na=False
        )
    ]
    if receita.empty:
        return contas.iloc[0:0].copy()
    ultimo_ano = contas["ano"].max()
    validas = receita.loc[receita["ano"].eq(ultimo_ano), "cd_cvm"].unique()
    return contas.loc[contas["cd_cvm"].isin(validas)].copy()


def preparar_empresas(cadastro):
    """Monta a tabela empresas: uma linha por código CVM, a partir do cadastro."""
    obrigatorias = {"CD_CVM", "DENOM_SOCIAL", "CNPJ_CIA", "SIT", "SETOR_ATIV"}
    ausentes = obrigatorias.difference(cadastro.columns)
    if ausentes:
        raise ValueError(
            "cad_cia_aberta.csv não contém as colunas obrigatórias: "
            f"{', '.join(sorted(ausentes))}"
        )

    empresas = pd.DataFrame({
        "cd_cvm": cadastro["CD_CVM"].map(codigo_cvm),
        "nome": cadastro["DENOM_SOCIAL"].astype("string").str.strip(),
        "cnpj": cadastro["CNPJ_CIA"].astype("string").str.strip(),
        "situacao": cadastro["SIT"].astype("string").str.strip(),
        "setor": cadastro["SETOR_ATIV"].astype("string").str.strip(),
    })
    empresas["setor"] = empresas["setor"].fillna("Não Informado")

    # A mesma empresa aparece uma vez por mercado (bolsa, balcão);
    # fica uma linha por código, preferindo o registro ativo.
    ativo = empresas["situacao"].str.upper().eq("ATIVO").fillna(False)
    empresas = (
        empresas.assign(_ativo=ativo)
        .sort_values(["cd_cvm", "_ativo"], ascending=[True, False], kind="stable")
        .drop_duplicates("cd_cvm")
        .drop(columns="_ativo")
    )
    return empresas.reset_index(drop=True)
