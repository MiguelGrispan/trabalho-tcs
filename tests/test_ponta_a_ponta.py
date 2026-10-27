"""
Teste de ponta a ponta com os dados reais (data/indicadores.csv, gerado pelos scripts do Marcos).
Pula sozinho quando os dados não existem: no CI e em quem ainda não baixou a pasta data/ do Drive.

Rodar só este arquivo:  python -m pytest -q tests/test_ponta_a_ponta.py
"""
import pandas as pd
import pytest

from raiox import ia, segmentos

pytestmark = pytest.mark.skipif(not segmentos.ARQ_INDICADORES.exists(),
                                reason="sem data/indicadores.csv (dados reais)")

COLUNAS_C2 = ["cd_cvm", "nome", "setor", "ano", "receita", "receita_2a_antes", "cresc_2a", "margem_ebit",
              "margem_liquida", "ativo_total", "endividamento", "origem", "versao"]


@pytest.fixture(autouse=True)
def dados_reais(monkeypatch):
    monkeypatch.setenv("RAIOX_DADOS", "real")
    ia._base.cache_clear()
    yield
    ia._base.cache_clear()


def test_tabela_real_segue_o_c2():
    df = pd.read_csv(segmentos.ARQ_INDICADORES)               # CSV padrão: sem parâmetros (contrato C2)
    assert set(COLUNAS_C2) <= set(df.columns), set(COLUNAS_C2) - set(df.columns)
    assert pd.api.types.is_integer_dtype(df["cd_cvm"]) and df["cd_cvm"].is_unique
    assert len(df) >= 200                                       # menos que isso: algo falhou na carga
    assert (df["receita"] > 0).all()


def test_raio_x_sem_ia_de_tres_setores():
    df, falso = segmentos.carregar_indicadores()
    assert not falso
    for cd in df.drop_duplicates("setor")["cd_cvm"].head(3):
        r = ia.preparar_raio_x(int(cd), "software de gestão", "primeira reunião", usar_ia=False)
        assert len(r["indicadores"]) == 6 and len(r["parecidas"]) == 5, cd
        assert r["removidos"] == [], cd
        assert all(i["fonte"].startswith("DFP ") for i in r["indicadores"]), cd


def test_casos_de_avaliacao_existem_na_tabela_real():
    from avaliacao import avaliar
    if not avaliar.ARQ_CASOS.exists():
        pytest.skip("avaliacao/casos_avaliacao.csv ainda não está na main")
    casos = pd.read_csv(avaliar.ARQ_CASOS, dtype={"cd_cvm": str})
    preenchidos = casos["cd_cvm"].dropna().str.strip()
    preenchidos = preenchidos[preenchidos != ""].astype(int)
    df, _ = segmentos.carregar_indicadores()
    faltando = set(preenchidos) - set(df["cd_cvm"])
    assert not faltando, f"cd_cvm dos casos que não estão no indicadores.csv: {sorted(faltando)}"
