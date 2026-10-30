# %% [markdown]
# ## Avaliar o corte de receita do Eduardo
#
# `RECEITA_MINIMA` em raiox/segmentos.py. Pergunta: abaixo de R$ 10 mi só ficam
# empresas "estranhas" (holdings, securitizadoras, paradas)? E o corte separa
# bem ou é arbitrário?
#
# Importando as bibliotecas:

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CORTE = 10e6  # R$ 10 mi, o valor proposto

# %% [markdown]
# Carregando o `indicadores.csv`:

# %%
indicadores = pd.read_csv('data/indicadores.csv', dtype={"cd_cvm": str})

# log de zero não existe
indicadores = indicadores[indicadores["receita"] > 0]

print(indicadores.info())

# %% [markdown]
# Tipo de empresa pelo setor da CVM (holding = "Emp. Adm. Part."):

# %%
# Função personalizada para transformar o setor em tipo
def transform_tipo(value: str):
    if value.startswith("Securitiza"):
        return "securitizadora"

    elif value.startswith("Emp. Adm. Part"):
        return "holding"

    return "operacional"

indicadores["tipo"] = indicadores["setor"].apply(transform_tipo)

print(indicadores["tipo"].value_counts())

# %%
TIPOS = ["operacional", "holding", "securitizadora"]
CORES = {"operacional": "#2a78d6", "holding": "#eb6834", "securitizadora": "#1baf7a"}

# Eixo x em escala log, mas com rótulos em reais (mais fácil de ler que 10^7)
MARCAS = [1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11]
ROTULOS = ["100 mil", "1 mi", "10 mi", "100 mi", "1 bi", "10 bi", "100 bi"]

def eixo_receita(eixo):
    eixo.set_xscale("log")
    eixo.set_xticks(MARCAS, ROTULOS)
    eixo.axvline(CORTE, color="#52514e", linestyle="--", linewidth=1)
    eixo.spines[["top", "right"]].set_visible(False)

# %% [markdown]
# 1) Histograma da receita, empilhado por tipo de empresa:

# %%
# Separa a receita de cada tipo numa lista
receitas_por_tipo = []
cores = []
for tipo in TIPOS:
    receitas_por_tipo.append(indicadores[indicadores["tipo"] == tipo]["receita"])
    cores.append(CORES[tipo])

# Faixas do histograma igualmente espaçadas na escala log
bins = np.logspace(np.log10(indicadores["receita"].min()), np.log10(indicadores["receita"].max()), 40)

fig, eixo = plt.subplots(figsize=(9, 4.5))
eixo.hist(receitas_por_tipo, bins=bins, stacked=True, label=TIPOS, color=cores,
          edgecolor="white", linewidth=0.5)
eixo_receita(eixo)

abaixo = (indicadores["receita"] < CORTE).sum()
eixo.set_title(f"Receita das empresas: {abaixo} de {len(indicadores)} ficam abaixo de R$ 10 mi (linha tracejada)")
eixo.set_xlabel("Receita líquida (R$, escala log)")
eixo.set_ylabel("Empresas")
eixo.legend(frameon=False)
fig.tight_layout()

# %% [markdown]
# 2) Quantas empresas saem do treino para cada corte possível.
# Se a curva tiver um "degrau" perto de 10 mi, o corte é natural; se for lisa, é uma escolha.

# %%
cortes = np.logspace(5, 9, 200)  # de R$ 100 mil a R$ 1 bi

fig, eixo = plt.subplots(figsize=(9, 4.5))
for tipo in TIPOS:
    receitas = indicadores[indicadores["tipo"] == tipo]["receita"]

    # Para cada corte, conta quantas empresas ficam abaixo dele
    abaixo_do_corte = []
    for corte in cortes:
        abaixo_do_corte.append((receitas < corte).sum())

    eixo.plot(cortes, abaixo_do_corte, color=CORES[tipo], linewidth=2, label=tipo)

eixo_receita(eixo)
eixo.set_xlim(1e5, 1e9)
eixo.set_title("Empresas que ficam fora do treino, conforme o corte")
eixo.set_xlabel("Corte de receita (R$)")
eixo.set_ylabel("Empresas abaixo do corte")
eixo.legend(frameon=False)
fig.tight_layout()

# %% [markdown]
# 3) Receita x margem EBIT: abaixo do corte as margens são absurdas?

# %%
fig, eixo = plt.subplots(figsize=(9, 5))
for tipo in TIPOS:
    parte = indicadores[indicadores["tipo"] == tipo]
    # clip: margens fora de [-1, 1] vão para a borda (ficam empilhadas em cima e embaixo)
    eixo.scatter(parte["receita"], parte["margem_ebit"].clip(-1, 1), s=14, alpha=0.7,
                 color=CORES[tipo], label=tipo)

eixo_receita(eixo)
eixo.axhline(0, color="#52514e", linewidth=0.8)
eixo.set_title("Receita x margem EBIT (pontos em -1 e +1 são margens absurdas, cortadas na borda)")
eixo.set_xlabel("Receita líquida (R$, escala log)")
eixo.set_ylabel("Margem EBIT")
eixo.legend(frameon=False)
fig.tight_layout()

# %% [markdown]
# Resumo em texto: % de margens absurdas abaixo e acima do corte

# %%
indicadores["margem_absurda"] = indicadores["margem_ebit"].abs() > 1

abaixo = indicadores[indicadores["receita"] < CORTE]
acima = indicadores[indicadores["receita"] >= CORTE]

print(f"abaixo do corte: {len(abaixo)} empresas, {abaixo['margem_absurda'].mean():.0%} com |margem EBIT| > 100%")
print(f"acima do corte: {len(acima)} empresas, {acima['margem_absurda'].mean():.0%} com |margem EBIT| > 100%")

plt.show()
