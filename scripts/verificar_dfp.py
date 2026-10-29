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
# Baixando o zip de 2025 e lendo a DRE consolidada (regra 1):

# %%
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"

resposta = requests.get(URL, timeout=180)
z = zipfile.ZipFile(io.BytesIO(resposta.content))

# Nomes dos CSVs dentro do zip
print(z.namelist())

# Regra 1: sep=";", encoding="latin-1", decimal="," e CD_CONTA como texto
dre = pd.read_csv(
    z.open("dfp_cia_aberta_DRE_con_2025.csv"),
    sep=";", encoding="latin-1", decimal=",",
    dtype={"CD_CONTA": str, "CD_CVM": str},
)
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

# Bancos e seguradoras aparecem com outro nome
print(receita["DS_CONTA"].value_counts().head(10))

# Escalas usadas (MIL ou UNIDADE)
print(receita["ESCALA_MOEDA"].value_counts())
