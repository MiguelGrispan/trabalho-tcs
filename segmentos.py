"""
segmentos.py · Eduardo · ML (passo 4 do fluxo)

Lê a tabela de indicadores (contrato C2), separa as empresas em grupos de perfil parecido (K-means)
e acha as 5 empresas mais parecidas com cada uma (vizinhos mais próximos).

Rodar:
    python segmentos.py      → gera data/segmentos.csv e docs/graficos/silhueta.png

Entrada: data/indicadores.csv (vem do Marcos). Enquanto ele não existir, usa tabela_falsa.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

PASTA = Path(__file__).parent
ARQ_INDICADORES = PASTA / "data" / "indicadores.csv"
ARQ_FALSO = PASTA / "tabela_falsa.csv"
ARQ_SEGMENTOS = PASTA / "data" / "segmentos.csv"
ARQ_SILHUETA = PASTA / "docs" / "graficos" / "silhueta.png"

SEMENTE = 42
K_TESTADOS = range(3, 9)
N_PARECIDAS = 5
VARIAVEIS = ["log_receita", "cresc_2a", "margem_ebit", "margem_liquida", "endividamento"]
INDICADORES_NUM = ["receita", "cresc_2a", "margem_ebit", "margem_liquida", "endividamento", "ativo_total"]


def carregar_indicadores() -> tuple[pd.DataFrame, bool]:
    """Devolve (tabela, usando_dados_falsos)."""
    if ARQ_INDICADORES.exists():
        return pd.read_csv(ARQ_INDICADORES), False
    if not ARQ_FALSO.exists():
        from prova_ia import tabela_falsa
        tabela_falsa().to_csv(ARQ_FALSO, index=False)
    return pd.read_csv(ARQ_FALSO), True


def segmentar(df: pd.DataFrame):
    """Devolve (tabela com grupo, percentis e parecidas; silhueta por k; k escolhido)."""
    X = df.assign(log_receita=np.log10(df["receita"]))[VARIAVEIS].copy()
    for c in VARIAVEIS:                                   # cortar extremos (percentis 1 e 99)
        X[c] = X[c].clip(X[c].quantile(0.01), X[c].quantile(0.99))
    X = X.fillna(X.median())                              # nulos: mediana, só para o modelo
    Xs = StandardScaler().fit_transform(X)                # padronizar: todas as colunas na mesma régua

    silhuetas = {}
    for k in K_TESTADOS:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit(Xs)
        silhuetas[k] = float(silhouette_score(Xs, km.labels_))
    k = max(silhuetas, key=silhuetas.get)                # o número de grupos com a maior silhueta
    grupos = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit_predict(Xs)

    vizinhos = NearestNeighbors(n_neighbors=N_PARECIDAS + 1).fit(Xs)
    _, idx = vizinhos.kneighbors(Xs)                      # a 1ª vizinha é a própria empresa
    out = df.copy()
    out["grupo"] = grupos
    out["parecidas"] = [list(df["cd_cvm"].iloc[linha[1:]]) for linha in idx]
    for i in INDICADORES_NUM:                             # posição da empresa dentro do grupo (0 a 100)
        out[f"pct_{i}"] = (out.groupby("grupo")[i].rank(pct=True) * 100).round(0)
    return out, silhuetas, k


def salvar(seg: pd.DataFrame) -> None:
    ARQ_SEGMENTOS.parent.mkdir(parents=True, exist_ok=True)
    cols = ["cd_cvm", "grupo", "parecidas"] + [f"pct_{i}" for i in INDICADORES_NUM]
    s = seg[cols].copy()
    s["parecidas"] = s["parecidas"].apply(lambda l: ";".join(str(x) for x in l))
    s.to_csv(ARQ_SEGMENTOS, index=False)


def carregar_segmentos(df: pd.DataFrame) -> pd.DataFrame:
    """Junta indicadores + segmentos.csv. Refaz o agrupamento se o arquivo não existir ou estiver velho."""
    origem = ARQ_INDICADORES if ARQ_INDICADORES.exists() else ARQ_FALSO
    velho = (not ARQ_SEGMENTOS.exists()) or ARQ_SEGMENTOS.stat().st_mtime < origem.stat().st_mtime
    if velho:
        seg, _, _ = segmentar(df)
        salvar(seg)
        return seg
    s = pd.read_csv(ARQ_SEGMENTOS)
    s["parecidas"] = s["parecidas"].fillna("").apply(lambda t: [int(x) for x in str(t).split(";") if x])
    return df.merge(s, on="cd_cvm", how="inner")


def grafico_silhueta(silhuetas: dict, k: int) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado: gráfico da silhueta não gerado.")
        return
    ARQ_SILHUETA.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    cores = ["#2563a8" if kk == k else "#b8c4d6" for kk in silhuetas]
    ax.bar([str(kk) for kk in silhuetas], list(silhuetas.values()), color=cores)
    ax.set_xlabel("Número de grupos (k)")
    ax.set_ylabel("Silhueta (maior é melhor)")
    ax.set_title(f"Escolha do número de grupos: k = {k}")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ARQ_SILHUETA, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df, falso = carregar_indicadores()
    if falso:
        print("Aviso: data/indicadores.csv ainda não existe. Usando tabela_falsa.csv.")
    seg, silhuetas, k = segmentar(df)
    salvar(seg)
    grafico_silhueta(silhuetas, k)
    print("Silhueta por k:", {kk: round(v, 2) for kk, v in silhuetas.items()}, "→ k escolhido:", k)
    print("\nTamanho e perfil típico (mediana) de cada grupo:")
    resumo = seg.groupby("grupo").agg(empresas=("cd_cvm", "size"), receita_mi=("receita", "median"),
                                      cresc=("cresc_2a", "median"), margem_ebit=("margem_ebit", "median"),
                                      endividamento=("endividamento", "median"))
    resumo["receita_mi"] = (resumo["receita_mi"] / 1e6).round(0)
    print(resumo.round(3).to_string())
    print(f"\nSalvo em {ARQ_SEGMENTOS.relative_to(PASTA)} e {ARQ_SILHUETA.relative_to(PASTA)}")
