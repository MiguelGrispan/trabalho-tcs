"""
segmentos.py · Eduardo · ML (passo 4 do fluxo)

Lê a tabela de indicadores (contrato C2), separa as empresas em grupos de perfil parecido (K-means)
e acha as 5 empresas mais parecidas com cada uma (vizinhos mais próximos).

Rodar (na raiz do repositório):
    python -m raiox.segmentos      → gera data/segmentos.csv, docs/graficos/silhueta.png e docs/graficos/grupos.png

Entrada: data/indicadores.csv (vem do Marcos). Enquanto ele não existir, usa falsos/tabela_falsa.csv.
RAIOX_DADOS=falsos força a tabela falsa mesmo com os dados reais presentes (testes e demo de reserva);
nesse caso o agrupamento é feito na memória e nada é gravado em data/.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

PASTA = Path(__file__).resolve().parent.parent   # raiz do repositório
ARQ_INDICADORES = PASTA / "data" / "indicadores.csv"
ARQ_FALSO = PASTA / "falsos" / "tabela_falsa.csv"
ARQ_SEGMENTOS = PASTA / "data" / "segmentos.csv"
ARQ_SILHUETA = PASTA / "docs" / "graficos" / "silhueta.png"
ARQ_GRUPOS = PASTA / "docs" / "graficos" / "grupos.png"

SEMENTE = 42
K_TESTADOS = range(3, 9)
N_PARECIDAS = 5
RECEITA_MINIMA = 10e6     # R$ 10 mi: abaixo disso ficam holdings e empresas sem operação, que distorcem os grupos (ED4)
CORTE = (0.05, 0.95)      # percentis dos extremos cortados
MENOR_GRUPO = 0.05        # um k só vale se o menor grupo tiver pelo menos 5% das empresas
VARIAVEIS = ["log_receita", "cresc_2a", "margem_ebit", "margem_liquida", "endividamento"]
INDICADORES_NUM = ["receita", "cresc_2a", "margem_ebit", "margem_liquida", "endividamento", "ativo_total"]


def usando_falsos() -> bool:
    """True quando RAIOX_DADOS=falsos ou quando data/indicadores.csv ainda não existe."""
    return os.getenv("RAIOX_DADOS", "").strip().lower() == "falsos" or not ARQ_INDICADORES.exists()


def carregar_indicadores() -> tuple[pd.DataFrame, bool]:
    """Devolve (tabela, usando_dados_falsos)."""
    if usando_falsos():
        return pd.read_csv(ARQ_FALSO), True
    return pd.read_csv(ARQ_INDICADORES), False


def treino(df: pd.DataFrame) -> pd.DataFrame:
    """As empresas com que o modelo aprende: receita a partir de RECEITA_MINIMA."""
    return df[df["receita"] >= RECEITA_MINIMA]


def variaveis_cruas(df: pd.DataFrame) -> pd.DataFrame:
    """As 5 variáveis do modelo antes de cortar e padronizar."""
    # receita zero ou negativa não tem log: vira vazio e recebe a mediana em matriz()
    return df.assign(log_receita=np.log10(df["receita"].where(df["receita"] > 0)))[VARIAVEIS]


def matriz(df: pd.DataFrame, base: pd.DataFrame | None = None) -> np.ndarray:
    """As 5 variáveis prontas para o modelo: log da receita, extremos cortados, nulos preenchidos, padronizadas.
    Os limites dos extremos, as medianas e a régua saem de `base` (se não vier, da própria df) e valem para toda a df."""
    B = variaveis_cruas(df if base is None else base)
    baixo, alto = B.quantile(CORTE[0]), B.quantile(CORTE[1])
    B = B.clip(baixo, alto, axis=1)                       # cortar extremos (percentis 5 e 95)
    mediana = B.median()                                  # nulos: mediana, só para o modelo
    regua = StandardScaler().fit(B.fillna(mediana))       # padronizar: todas as colunas na mesma régua
    return regua.transform(variaveis_cruas(df).clip(baixo, alto, axis=1).fillna(mediana))


def escolher_k(silhuetas: dict, menores: dict) -> int:
    """O k de maior silhueta entre os que têm o menor grupo com pelo menos MENOR_GRUPO das empresas.
    Sem isso, a silhueta premia separar 9 empresas extremas e deixar todas as outras num grupo só."""
    validos = [k for k in silhuetas if menores[k] >= MENOR_GRUPO] or list(silhuetas)
    return max(validos, key=silhuetas.get)


def segmentar(df: pd.DataFrame):
    """Devolve (tabela com grupo, percentis e parecidas; silhueta por k; k escolhido).
    O modelo aprende só com treino(df). As empresas menores entram no grupo mais perto e recebem parecidas do treino."""
    base = treino(df)
    Xb, Xs = matriz(base), matriz(df, base)

    silhuetas, menores = {}, {}
    for k in K_TESTADOS:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit(Xb)
        silhuetas[k] = float(silhouette_score(Xb, km.labels_))
        menores[k] = np.bincount(km.labels_).min() / len(base)
    k = escolher_k(silhuetas, menores)
    grupos = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit(Xb).predict(Xs)

    vizinhos = NearestNeighbors(n_neighbors=N_PARECIDAS + 1).fit(Xb)
    _, idx = vizinhos.kneighbors(Xs)
    cd_base = base["cd_cvm"].to_numpy()
    out = df.copy()
    out["grupo"] = grupos
    out["parecidas"] = [[c for c in cd_base[linha] if c != cd][:N_PARECIDAS]   # tira a própria empresa
                        for cd, linha in zip(df["cd_cvm"], idx)]
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
    """Junta indicadores + segmentos.csv. Refaz o agrupamento se o arquivo não existir ou estiver velho.
    Com a tabela falsa, agrupa na memória: o data/segmentos.csv é só dos dados reais."""
    if usando_falsos():
        return segmentar(df)[0]
    # velho: mais antigo que os dados ou que este código (mudou o modelo, refaz os grupos)
    velho = (not ARQ_SEGMENTOS.exists()) or ARQ_SEGMENTOS.stat().st_mtime < max(
        ARQ_INDICADORES.stat().st_mtime, Path(__file__).stat().st_mtime)
    if velho:
        seg, _, _ = segmentar(df)
        try:
            salvar(seg)
        except OSError as erro:   # data/ só de leitura (ex.: volume do Docker com :ro): os grupos ficam na memória
            print(f"Aviso: não deu para gravar {ARQ_SEGMENTOS.name} ({erro.strerror}); os grupos ficam só na memória.",
                  file=sys.stderr)
        return seg
    s = pd.read_csv(ARQ_SEGMENTOS)
    s["parecidas"] = s["parecidas"].fillna("").apply(lambda t: [int(x) for x in str(t).split(";") if x])
    return df.merge(s, on="cd_cvm", how="inner")


def _plt():
    import matplotlib
    matplotlib.use("Agg")                                 # grava em arquivo, sem abrir janela
    import matplotlib.pyplot as plt
    return plt


def grafico_grupos(seg: pd.DataFrame, caminho: Path = ARQ_GRUPOS) -> None:
    """Os grupos num gráfico 2D: as 5 variáveis resumidas em 2 eixos (PCA). Cada ponto é uma empresa."""
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=SEMENTE)
    pontos = pca.fit_transform(matriz(seg, treino(seg)))
    plt = _plt()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for g in sorted(seg["grupo"].unique()):
        dentro = (seg["grupo"] == g).to_numpy()
        ax.scatter(pontos[dentro, 0], pontos[dentro, 1], s=18, alpha=0.75, label=f"grupo {g} ({dentro.sum()})")
    v1, v2 = pca.explained_variance_ratio_ * 100
    ax.set_xlabel(f"Eixo 1 ({v1:.0f}% da variação)")
    ax.set_ylabel(f"Eixo 2 ({v2:.0f}% da variação)")
    ax.set_title("Empresas parecidas ficam perto: grupos do K-means")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def grafico_silhueta(silhuetas: dict, k: int, caminho: Path = ARQ_SILHUETA) -> None:
    plt = _plt()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    cores = ["#2563a8" if kk == k else "#b8c4d6" for kk in silhuetas]
    ax.bar([str(kk) for kk in silhuetas], list(silhuetas.values()), color=cores)
    ax.set_xlabel("Número de grupos (k)")
    ax.set_ylabel("Silhueta (maior é melhor)")
    ax.set_title(f"Escolha do número de grupos: k = {k}")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df, falso = carregar_indicadores()
    if falso:
        print("Aviso: data/indicadores.csv ainda não existe. Usando falsos/tabela_falsa.csv.")
    seg, silhuetas, k = segmentar(df)
    if not falso:
        salvar(seg)                                       # data/segmentos.csv é só dos dados reais
    grafico_silhueta(silhuetas, k)
    grafico_grupos(seg)
    print(f"Empresas no treino (receita a partir de R$ {RECEITA_MINIMA / 1e6:.0f} mi): {len(treino(df))} de {len(df)}")
    print("Silhueta por k:", {kk: round(v, 2) for kk, v in silhuetas.items()}, "→ k escolhido:", k)
    print("\nTamanho e perfil típico (mediana) de cada grupo:")
    resumo = seg.groupby("grupo").agg(empresas=("cd_cvm", "size"), receita_mi=("receita", "median"),
                                      cresc=("cresc_2a", "median"), margem_ebit=("margem_ebit", "median"),
                                      endividamento=("endividamento", "median"))
    resumo["receita_mi"] = (resumo["receita_mi"] / 1e6).round(0)
    print(resumo.round(3).to_string())
    salvos = [ARQ_SILHUETA, ARQ_GRUPOS] + ([] if falso else [ARQ_SEGMENTOS])
    print("\nSalvo em " + ", ".join(str(a.relative_to(PASTA)) for a in salvos))
