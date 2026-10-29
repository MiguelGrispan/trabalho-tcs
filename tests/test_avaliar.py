"""
Testes do avaliacao/avaliar.py (contrato C4). Sem IA: não gasta crédito.
"""
import json

import pandas as pd
import pytest

from avaliacao import avaliar

CASOS = pd.DataFrame({
    "caso_id": [1, 2, 3, 4],
    "cd_cvm": ["90001", "90002", "", "12345"],
    "empresa": ["ALFA NORTE S.A.", "BETA NORTE S.A.", "sem código", "não existe"],
    "produto": ["software de gestão de frota", "eficiência energética", "x", "y"],
    "objetivo": ["conhecer a operação", "reduzir custo de energia", "z", "w"],
})


def test_resultados_tem_as_colunas_do_c4():
    res = avaliar.avaliar(CASOS)
    assert list(res.columns) == ["caso_id", "raio_x_json", "n_removidos", "tokens_entrada", "tokens_saida",
                                 "custo_usd", "tempo_s"]
    assert list(res["caso_id"]) == [1, 2, 3, 4]


def test_casos_validos_geram_raio_x_completo():
    res = avaliar.avaliar(CASOS).iloc[:2]
    assert (res["n_removidos"] == 0).all()
    assert (res["custo_usd"] == 0).all()                    # sem IA não gasta nada
    r = json.loads(res.iloc[0]["raio_x_json"])
    assert r["empresa"] == "ALFA NORTE S.A." and len(r["indicadores"]) == 6


def test_caso_com_erro_nao_para_a_rodada():
    res = avaliar.avaliar(CASOS).iloc[2:]
    assert res["n_removidos"].isna().all()
    assert "sem cd_cvm" in json.loads(res.iloc[0]["raio_x_json"])["erro"]
    assert "12345" in json.loads(res.iloc[1]["raio_x_json"])["erro"]


def test_casos_avaliacao_do_repositorio_segue_o_c4():
    if not avaliar.ARQ_CASOS.exists():
        pytest.skip("avaliacao/casos_avaliacao.csv ainda não está na main")
    casos = pd.read_csv(avaliar.ARQ_CASOS)                   # sem parâmetros, como o C2
    assert list(casos.columns) == ["caso_id", "cd_cvm", "empresa", "produto", "objetivo"]
    assert casos["caso_id"].is_unique
    assert pd.api.types.is_integer_dtype(casos["cd_cvm"])    # todos preenchidos e sem texto (NA2)
    assert casos[["empresa", "produto", "objetivo"]].notna().all().all()
