"""
Testes da tela (app/streamlit_app.py) com o AppTest do Streamlit: roda a tela de verdade, sem navegador.

Nenhum teste chama o Gemini: o RAIOX_IA_REAL é apagado antes de cada teste.
"Dados reais" aqui é a tabela falsa no lugar da data/indicadores.csv (o padrão do tests/test_raio_x.py):
assim a tela usa o PostgreSQL sem depender de quem já baixou a CVM, e nada é gravado em data/.
"""
import json
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from streamlit.testing.v1 import AppTest

from falsos import falso_dados
from raiox import banco, ia, segmentos
from tests.banco_teste import TEST_DATABASE_URL, banco_disponivel

TELA = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"


@pytest.fixture(autouse=True)
def sem_ia(monkeypatch):
    monkeypatch.delenv("RAIOX_IA_REAL", raising=False)


@pytest.fixture
def dados_reais(tmp_path, monkeypatch):
    monkeypatch.setenv("RAIOX_DADOS", "real")
    monkeypatch.setattr(segmentos, "ARQ_INDICADORES", segmentos.ARQ_FALSO)
    monkeypatch.setattr(segmentos, "ARQ_SEGMENTOS", tmp_path / "segmentos.csv")


def abrir():
    at = AppTest.from_file(str(TELA), default_timeout=60)   # a 1ª vez treina o K-means: passa dos 3 s padrão
    return at.run()


def gerar(at, busca="alfa norte"):
    """Faz o que o vendedor faz: busca, escolhe a 1ª empresa, preenche a reunião e clica em Gerar."""
    at.text_input(key="busca").input(busca).run()
    at.selectbox(key="empresa").select_index(0).run()
    at.text_input(key="produto").input("software de gestão de frota").run()
    at.text_area(key="objetivo").input("primeira conversa com a diretoria").run()
    return at.button[0].click().run()


def textos(elementos):
    return " ".join(str(e.value) for e in elementos)


def test_tela_abre_com_dados_falsos_e_avisa():
    at = abrir()
    assert not at.exception
    assert "empresas e números inventados" in textos(at.warning)


def test_tela_gera_raio_x_com_dados_falsos():
    at = gerar(abrir())
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."
    assert len(at.metric) == 6                                   # os 6 indicadores


def test_tela_volta_para_sem_ia_quando_a_ia_falha(monkeypatch):
    chamadas = []

    def ia_fora_do_ar(*args):                                    # no lugar do Gemini: nunca chama a API
        chamadas.append(args)
        raise RuntimeError("API fora do ar")
    monkeypatch.setenv("RAIOX_IA_REAL", "1")
    monkeypatch.setattr(ia, "gerar_llm", ia_fora_do_ar)

    at = gerar(abrir())
    assert len(chamadas) == 1                                    # tentou a IA uma vez
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."
    assert "montado sem IA" in textos(at.warning)


def test_tela_mostra_o_raio_x_mesmo_se_o_registro_falhar(monkeypatch):
    def banco_caiu(registro):
        raise ConnectionError("banco caiu")
    monkeypatch.setattr(falso_dados, "registrar_consulta", banco_caiu)

    at = gerar(abrir())
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."
    assert "não foi registrada" in textos(at.warning)


def test_tela_avisa_quando_o_banco_nao_responde(dados_reais, monkeypatch):
    monkeypatch.setattr(banco, "DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:1/raiox")   # porta fechada
    at = abrir()
    assert "inventados" not in textos(at.warning)
    at.text_input(key="busca").input("alfa").run()
    assert not at.exception
    assert "Não consegui falar com o banco" in textos(at.error)


@pytest.mark.skipif(not banco_disponivel(), reason=f"PostgreSQL de testes indisponível ({TEST_DATABASE_URL})")
def test_tela_busca_no_banco_e_registra_a_consulta(dados_reais, monkeypatch):
    engine = create_engine(TEST_DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS contas, empresas, consultas"))
        # o catálogo como sai do carregar_dfp.py, só com a empresa 90001 da tabela falsa
        pd.DataFrame([["90001", "ALFA NORTE S.A.", "Transporte e logística", "3.01", "Receita de Venda",
                       100.0, 2025, "DRE", "con"]],
                     columns=["cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor", "ano", "demonstracao",
                              "origem"]).to_sql("contas", conn, index=False)
    monkeypatch.setattr(banco, "DATABASE_URL", TEST_DATABASE_URL)

    at = gerar(abrir())
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."

    with engine.begin() as conn:
        linhas = conn.execute(text("SELECT registro_json FROM consultas")).fetchall()
    engine.dispose()
    assert len(linhas) == 1
    registro = json.loads(linhas[0][0])
    assert registro["cd_cvm"] == 90001                           # número, como pede o C1 (o banco devolve texto)
    assert registro["produto"] == "software de gestão de frota"
