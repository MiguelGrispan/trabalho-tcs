"""
avaliar.py · Eduardo · contrato C4

Roda o raio-x para cada caso de avaliacao/casos_avaliacao.csv e grava avaliacao/resultados.csv.

Rodar (na raiz do repositório):
    python -m avaliacao.avaliar            → sem IA (não gasta crédito; serve para testar o caminho)
    python -m avaliacao.avaliar --com-ia   → com o Gemini (mais de 10 casos: avise o grupo antes)
"""
import argparse
import json
import time
from pathlib import Path

import pandas as pd

from raiox import ia

PASTA = Path(__file__).resolve().parent.parent   # raiz do repositório
ARQ_CASOS = PASTA / "avaliacao" / "casos_avaliacao.csv"
ARQ_RESULTADOS = PASTA / "avaliacao" / "resultados.csv"
COLUNAS = ["caso_id", "raio_x_json", "n_removidos", "tokens_entrada", "tokens_saida", "custo_usd", "tempo_s"]


def avaliar(casos: pd.DataFrame, usar_ia: bool = False, pausa_s: float = 1.0) -> pd.DataFrame:
    """Uma linha por caso, nas colunas do C4. Um caso com erro não para a rodada: o erro vai no raio_x_json."""
    linhas = []
    for n, caso in enumerate(casos.itertuples(index=False)):
        if usar_ia and n > 0:
            time.sleep(pausa_s)                       # respeita o limite de pedidos por minuto da API
        try:
            if pd.isna(caso.cd_cvm) or not str(caso.cd_cvm).strip():
                raise ValueError("caso sem cd_cvm")
            r = ia.preparar_raio_x(int(str(caso.cd_cvm).strip()), caso.produto, caso.objetivo, usar_ia=usar_ia)
            linhas.append({"caso_id": caso.caso_id, "raio_x_json": json.dumps(r, ensure_ascii=False),
                           "n_removidos": len(r["removidos"]), **r["uso"]})
        except Exception as erro:                     # API fora do ar, empresa sem dados, cd_cvm vazio...
            linhas.append({"caso_id": caso.caso_id, "raio_x_json": json.dumps({"erro": str(erro)}, ensure_ascii=False),
                           "n_removidos": None, "tokens_entrada": 0, "tokens_saida": 0, "custo_usd": 0.0,
                           "tempo_s": None})
    return pd.DataFrame(linhas, columns=COLUNAS)


if __name__ == "__main__":
    a = argparse.ArgumentParser(description="Roda os casos de avaliação e grava o resultados.csv (contrato C4).")
    a.add_argument("--com-ia", action="store_true", help="usa o Gemini (gasta crédito)")
    a.add_argument("--casos", type=Path, default=ARQ_CASOS)
    a.add_argument("--saida", type=Path, default=ARQ_RESULTADOS)
    args = a.parse_args()
    casos = pd.read_csv(args.casos, dtype={"cd_cvm": str})
    if args.com_ia and len(casos) > 10:
        print(f"Aviso: {len(casos)} chamadas ao Gemini. Combine com o grupo antes (REGRAS-IA.md).")
    res = avaliar(casos, usar_ia=args.com_ia)
    res.to_csv(args.saida, index=False)
    erros = int(res["n_removidos"].isna().sum())
    print(f"{len(res)} casos → {args.saida} · itens removidos pelo validador: {int(res['n_removidos'].sum())} · "
          f"casos com erro: {erros} · custo total: US$ {res['custo_usd'].sum():.4f}")
