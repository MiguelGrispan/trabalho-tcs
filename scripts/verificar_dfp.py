"""
Tutorial: Inspeção Inicial dos Dados

Antes de começarmos a processar os dados, precisamos entender como
eles chegam da CVM. Este script baixa o arquivo do ano de 2025,
aplica os filtros básicos e nos mostra um resumo: quantas empresas
temos, quais os nomes das contas de receita e se os valores estão
em reais ou em milhares.
"""
import io
import zipfile
import pandas as pd
import requests

URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"
NOME_DRE = "dfp_cia_aberta_DRE_con_2025.csv"

def main():
    print("Baixando os dados de 2025...")
    resposta = requests.get(URL, timeout=180)
    resposta.raise_for_status()

    # Abrimos o arquivo compactado direto na memória
    with zipfile.ZipFile(io.BytesIO(resposta.content)) as arquivo_zip:
        # Lemos a planilha com as configurações padrão para arquivos brasileiros
        dre = pd.read_csv(
            arquivo_zip.open(NOME_DRE),
            sep=";", encoding="latin-1", decimal=",",
            dtype={"CD_CONTA": str, "CD_CVM": str},
        )

    # Filtramos para manter apenas o último exercício e a versão mais recente enviada
    ordem_exercicio = (
        dre["ORDEM_EXERC"].astype("string").str.strip().str.upper()
    )
    dre = dre.loc[ordem_exercicio.eq("ÚLTIMO")].copy()
    dre["_versao_num"] = pd.to_numeric(dre["VERSAO"], errors="coerce")
    dre = dre.loc[dre["_versao_num"].eq(dre.groupby("CD_CVM")["_versao_num"].transform("max"))]

    # Isolamos a conta de Receita para analisar
    receita = dre[dre["CD_CONTA"].str.strip() == "3.01"]

    print("\n--- RESULTADO ---")
    print(f"Empresas com dados de receita: {receita['CD_CVM'].nunique()}")
    print("\nNomes das contas de receita encontradas:")
    print(receita["DS_CONTA"].value_counts().head(10).to_string())
    print("\nEscalas de valores utilizadas:")
    print(receita["ESCALA_MOEDA"].value_counts().to_string())

if __name__ == "__main__":
    main()