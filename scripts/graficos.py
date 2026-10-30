# %% [markdown]
# ## Exploração e gráficos de validação
#
# Importando as bibliotecas:

# %%
import matplotlib.pyplot as plt
import pandas as pd

# Mostra todas as colunas, sem "...", usando a largura toda do terminal
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# %% [markdown]
# Carregando o `contas.csv` como `DataFrame`:

# %%
# dtype=str: sem isso o pandas pode ler "1" como número e "3.01" como texto na mesma coluna
data = pd.read_csv('data/contas.csv', dtype={"cd_cvm": str, "cd_conta": str})

# Printando informações gerais da base de dados
print(data.info())

# %% [markdown]
# Quantas empresas têm todas as contas dos 6 indicadores no último ano:

# %%
# Contas que os 6 indicadores usam: (demonstração, código da conta)
CONTAS_NECESSARIAS = [
    ("DRE", "3.01"),  # receita líquida
    ("DRE", "3.05"),  # EBIT
    ("DRE", "3.11"),  # lucro do período
    ("BPA", "1"),     # ativo total
    ("BPP", "2.03"),  # patrimônio líquido
]

ano_atual = data["ano"].max()
ultimo_ano = data[data["ano"] == ano_atual]

empresas_validas = set(data["cd_cvm"])
print(f"Empresas na base: {len(empresas_validas)}")

for demonstracao, conta in CONTAS_NECESSARIAS:
    tem_conta = ultimo_ano[(ultimo_ano["demonstracao"] == demonstracao) & (ultimo_ano["cd_conta"] == conta)]
    # & entre conjuntos: fica só quem está nos dois
    empresas_validas = empresas_validas & set(tem_conta["cd_cvm"])
    print(f"  com {demonstracao} {conta} em {ano_atual}: {len(empresas_validas)}")

# Sem filtro pela receita de 2 anos antes: quem não tem fica com crescimento vazio (regra 7)
data = data[data["cd_cvm"].isin(empresas_validas)]

print(data.info())

# %%
print(data.head(10))                     # primeiras 10 linhas, para ver como os dados são
print(data["setor"].value_counts())      # quantas linhas por setor
print(data["valor"].describe())          # mínimo, máximo e média dos valores

# %%
# Receita (3.01) por empresa e ano, em formato de tabela
receita = data[(data["demonstracao"] == "DRE") & (data["cd_conta"] == "3.01")]
print(receita.pivot_table(index="nome", columns="ano", values="valor").head(10))

# %% [markdown]
# Carregando o `indicadores.csv`:

# %%
indicadores = pd.read_csv('data/indicadores.csv', dtype={"cd_cvm": str})

print(indicadores.info())

# %% [markdown]
# Histogramas: um gráfico por indicador, para achar valores absurdos

# %%
# Coluna -> faixa "razoável". Fora da faixa = suspeito, vale investigar
FAIXAS = {
    "cresc_2a":       (-1, 3),   # -100% a +300%
    "margem_ebit":    (-1, 1),
    "margem_liquida": (-1, 1),
    "endividamento":  (0, 2),    # passivo / ativo
}

fig, eixos = plt.subplots(2, 2, figsize=(11, 7))
eixos = eixos.flatten()  # grade 2x2 vira uma lista de 4 eixos

for idx, coluna in enumerate(FAIXAS):
    minimo, maximo = FAIXAS[coluna]
    valores = indicadores[coluna].dropna()
    fora = valores[(valores < minimo) | (valores > maximo)]

    # clip: valores fora da faixa vão para a borda do gráfico
    eixos[idx].hist(valores.clip(minimo, maximo), bins=40, color="#2a78d6")
    eixos[idx].axvline(0, color="gray", linewidth=1)
    eixos[idx].set_title(f"{coluna}  ({len(fora)} de {len(valores)} fora de [{minimo}, {maximo}])")

fig.suptitle(f"Distribuição dos indicadores ({indicadores['ano'].max()})")
fig.tight_layout()

# %%
# Lista os casos mais extremos para conferir na fonte (CVM / RI da empresa)
for coluna in FAIXAS:
    minimo, maximo = FAIXAS[coluna]
    fora = indicadores[(indicadores[coluna] < minimo) | (indicadores[coluna] > maximo)]
    fora = fora.copy()
    fora["distancia"] = fora[coluna].abs()
    fora = fora.sort_values("distancia", ascending=False)

    print(f"\n{coluna}: {len(fora)} fora da faixa. Mais extremos:")
    print(fora[["nome", "receita", coluna]].head(5))

# %% [markdown]
# Receita x ativo total (escala log): erro de unidade (mil vs unidade) aparece como ponto isolado

# %%
positivos = indicadores[(indicadores["receita"] > 0) & (indicadores["ativo_total"] > 0)]

fig, eixo = plt.subplots(figsize=(7, 6))
eixo.scatter(positivos["ativo_total"], positivos["receita"], s=12, alpha=0.6, color="#2a78d6")
eixo.set_xscale("log")
eixo.set_yscale("log")
eixo.set_xlabel("Ativo total (R$)")
eixo.set_ylabel("Receita líquida (R$)")
eixo.set_title("Receita x ativo total")

print(f"Empresas com receita <= 0 (fora do gráfico de dispersão): {len(indicadores) - len(positivos)}")

# %% [markdown]
# Empresas por ano na base de contas: se um ano tiver bem menos, faltou carregar algo

# %%
# Uma linha por empresa e ano, depois conta quantas empresas há em cada ano
empresas_por_ano = data.drop_duplicates(subset=["ano", "cd_cvm"])["ano"].value_counts().sort_index()
print(empresas_por_ano)

fig, eixo = plt.subplots(figsize=(6, 4))
empresas_por_ano.plot.bar(ax=eixo, color="#2a78d6")
eixo.set_title("Empresas por ano (contas.csv)")
eixo.set_ylabel("Empresas")

plt.show()
