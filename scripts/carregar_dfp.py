"""
Tutorial: Pipeline de Limpeza e Carga de Dados

Este é o script principal de extração. Ele baixa os dados de três anos,
passa por todas as regras de limpeza necessárias para remover a "sujeira"
que vem da CVM, cruza com o cadastro de setores e salva tudo
em um arquivo CSV e em um banco de dados SQLite.
"""
import io
import sqlite3
import zipfile
import time
from contextlib import closing
from pathlib import Path
import pandas as pd
import requests

ANOS = [2023, 2024, 2025]
DEMOS = ["DRE", "BPA", "BPP"]
ORIGENS = ["con", "ind"]
BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


COLUNAS_CONTA = [
    "cd_cvm", "nome", "cd_conta", "ds_conta", "valor", "ano",
    "demonstracao", "origem", "versao",
]


def _codigo_cvm(valor):
    codigo = str(valor).strip()
    return codigo.lstrip("0") or "0"


def ler_demo(z, demo, origem, ano):
    """Lê e normaliza uma demonstração contida no ZIP anual da CVM."""
    nome_arquivo = f"dfp_cia_aberta_{demo}_{origem}_{ano}.csv"
    if nome_arquivo not in z.namelist():
        return pd.DataFrame(columns=COLUNAS_CONTA)

    df = pd.read_csv(
        z.open(nome_arquivo),
        sep=";",
        encoding="latin-1",
        decimal=",",
        dtype={"CD_CVM": str, "CD_CONTA": str, "ESCALA_MOEDA": str},
    )
    obrigatorias = {
        "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
        "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
    }
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise ValueError(
            f"{nome_arquivo} não contém as colunas obrigatórias: "
            f"{', '.join(sorted(ausentes))}"
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
        "cd_cvm": df["CD_CVM"].map(_codigo_cvm),
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


def baixar_com_retry(url, tentativas=3):
    """Caso a internet caia, o script tenta baixar novamente."""
    if tentativas < 1:
        raise ValueError("tentativas deve ser pelo menos 1.")
    for i in range(tentativas):
        try:
            resposta = requests.get(url, timeout=300)
            resposta.raise_for_status()
            return resposta.content
        except requests.exceptions.RequestException:
            if i < tentativas - 1:
                time.sleep(2)
            else:
                raise


def preferir_consolidado(contas):
    """Mantém dados consolidados; usa individuais quando não há consolidados."""
    chaves = ["ano", "cd_cvm", "demonstracao"]
    if contas.empty or "origem" not in contas.columns:
        return contas.copy()
    tem_consolidado = contas["origem"].eq("con").groupby(
        [contas[coluna] for coluna in chaves], dropna=False
    ).transform("any")
    return contas.loc[contas["origem"].eq("con") | ~tem_consolidado].copy()


def filtrar_empresas_com_receita(contas):
    """Mantém empresas com receita de venda positiva no ano mais recente."""
    if contas.empty:
        return contas.copy()
    receita = contas.loc[
        contas["cd_conta"].astype(str).str.strip().eq("3.01")
        & pd.to_numeric(contas["valor"], errors="coerce").gt(0)
    ]
    if receita.empty:
        return contas.iloc[0:0].copy()
    ultimo_ano = contas["ano"].max()
    validas = receita.loc[receita["ano"].eq(ultimo_ano), "cd_cvm"].unique()
    return contas.loc[contas["cd_cvm"].isin(validas)].copy()


def encontrar_conflitos(contas):
    """Retorna todas as linhas com chave empresa/ano/demonstração/conta duplicada."""
    chaves = ["ano", "cd_cvm", "demonstracao", "cd_conta"]
    if contas.empty or not set(chaves).issubset(contas.columns):
        return contas.iloc[0:0].copy()
    duplicadas = contas.duplicated(subset=chaves, keep=False)
    return contas.loc[duplicadas].copy()


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
        "cd_cvm": cadastro["CD_CVM"].map(_codigo_cvm),
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


def main():
    print("Iniciando o download e processamento...")
    partes = []

    # Baixa o cadastro: vira a tabela empresas e dá o setor de cada empresa
    url_cad = f"{BASE_URL}/CAD/DADOS/cad_cia_aberta.csv"
    cadastro = pd.read_csv(io.BytesIO(baixar_com_retry(url_cad)), sep=";", encoding="latin-1", dtype=str)
    print(f"Colunas do cadastro: {', '.join(cadastro.columns)}")
    empresas = preparar_empresas(cadastro)
    mapa_setor = dict(zip(empresas["cd_cvm"], empresas["setor"]))

    for ano in ANOS:
        print(f"Baixando dados do ano {ano}...")
        url = f"{BASE_URL}/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
        conteudo = baixar_com_retry(url)

        with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
            for demo in DEMOS:
                for origem in ORIGENS:
                    partes.append(ler_demo(z, demo, origem, ano))

    contas = pd.concat(partes, ignore_index=True)
    if contas.empty:
        raise ValueError("Nenhuma demonstração DFP foi encontrada nos arquivos baixados.")

    # Adiciona o setor
    contas["setor"] = contas["cd_cvm"].map(mapa_setor).fillna("Não Informado")

    contas = preferir_consolidado(contas)
    contas = filtrar_empresas_com_receita(contas)

    # Avisa sobre contas repetidas; indicadores.py deixa esses valores ausentes
    conflitos = encontrar_conflitos(contas)
    if not conflitos.empty:
        chaves = conflitos[["ano", "cd_cvm", "demonstracao", "cd_conta"]].drop_duplicates()
        print(
            f"Aviso: {len(chaves)} contas aparecem repetidas na mesma "
            f"empresa/ano/demonstração. Exemplos:\n{chaves.head(5).to_string(index=False)}"
        )

    # Salva os arquivos
    caminho_csv = DATA_DIR / "contas.csv"
    contas.to_csv(caminho_csv, sep=";", index=False, encoding="utf-8-sig", decimal=",")
    print(f"Arquivo contas.csv salvo com {len(contas)} linhas.")

    caminho_db = DATA_DIR / "catalogo.db"
    with closing(sqlite3.connect(caminho_db)) as conn:
        with conn:
            contas.to_sql("contas", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cd_cvm ON contas(cd_cvm);")
            empresas.to_sql("empresas", conn, if_exists="replace", index=False)
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_empresas_cd_cvm ON empresas(cd_cvm);"
            )
    ativas = int(empresas["situacao"].str.upper().eq("ATIVO").sum())
    print(
        f"Banco de dados catalogo.db atualizado "
        f"(tabela empresas: {len(empresas)} empresas, {ativas} ativas)."
    )

if __name__ == "__main__":
    main()