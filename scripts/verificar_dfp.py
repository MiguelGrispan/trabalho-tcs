# %% [markdown]
# ## Inspeção inicial dos dados da CVM
#
# Primeira tarefa do Marcos (S1): quantas empresas têm receita na DFP 2025,
# com que nomes de conta e em que escala.
#
# Importando as bibliotecas:

# %%
import io
import zipfile

import pandas as pd
import requests

# %% [markdown]
# Baixando o zip de 2025 e lendo a DRE consolidada e a individual (regra 1):

# %%
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"

resposta = requests.get(URL, timeout=180)
z = zipfile.ZipFile(io.BytesIO(resposta.content))

# Nomes dos CSVs dentro do zip
print(z.namelist())


# Regra 1: sep=";", encoding="latin-1", decimal="," e CD_CONTA como texto
def ler_dre(origem):
    return pd.read_csv(
        z.open(f"dfp_cia_aberta_DRE_{origem}_2025.csv"),
        sep=";", encoding="latin-1", decimal=",",
        dtype={"CD_CONTA": str, "CD_CVM": str},
    )


# Regra 5: o consolidado; quem não tem controladas só publica o individual
con = ler_dre("con")
ind = ler_dre("ind")
dre = pd.concat([con, ind[~ind["CD_CVM"].isin(con["CD_CVM"])]], ignore_index=True)
print(dre.info())

# %% [markdown]
# Filtrando o exercício e a versão (regras 2 e 3):

# %%
# Regra 2: só o exercício do ano
dre = dre[dre["ORDEM_EXERC"] == "ÚLTIMO"]

# Regra 3: só a maior versão de cada empresa
maior_versao = dre.groupby("CD_CVM")["VERSAO"].transform("max")
dre = dre[dre["VERSAO"] == maior_versao]

print(dre.info())

# %% [markdown]
# Analisando a conta de receita (3.01):

# %%
receita = dre[dre["CD_CONTA"] == "3.01"]

print("Empresas com conta 3.01:", receita["CD_CVM"].nunique())
print("  delas, com DRE consolidada:",receita.loc[receita["CD_CVM"].isin(con["CD_CVM"]), "CD_CVM"].nunique())

# Bancos e seguradoras aparecem com outro nome
print("Linhas por descrição da conta:")
print(receita["DS_CONTA"].value_counts())
vendas = receita[receita["DS_CONTA"].str.contains("receita de venda", case=False, na=False)]
print("Empresas com receita de venda na 3.01:", vendas["CD_CVM"].nunique())
print("Empresas com receita de venda positiva:", vendas.loc[pd.to_numeric(vendas["VL_CONTA"]) > 0, "CD_CVM"].nunique())

# Escalas usadas (MIL ou UNIDADE)
print(receita["ESCALA_MOEDA"].value_counts())
