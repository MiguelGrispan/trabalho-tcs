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


@pytest.fixture
def banco_vazio(dados_reais, monkeypatch):
    """O banco de testes sem tabelas, e o código apontando para ele (como o tests/banco_teste.py)."""
    if not banco_disponivel():
        pytest.skip(f"PostgreSQL de testes indisponível ({TEST_DATABASE_URL})")
    engine = create_engine(TEST_DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS contas, empresas, consultas, indicadores"))
    monkeypatch.setattr(banco, "DATABASE_URL", TEST_DATABASE_URL)
    yield engine
    engine.dispose()


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


def detalhes_tecnicos(at):
    """Tudo o que está escrito dentro do "Detalhes técnicos" (fechado na tela, mas está lá)."""
    bloco = next(e for e in at.expander if e.label == "Detalhes técnicos")
    return " ".join(textos(getattr(bloco, tipo)) for tipo in ("markdown", "text", "code", "caption"))


# O erro que o Google devolve com a chave errada (encurtado do que a tela mostrou em 03/11, issue #38).
ERRO_DO_GOOGLE = ("Error calling model 'gemini-3.1-flash-lite' (INVALID_ARGUMENT): 400 INVALID_ARGUMENT. "
                  "{'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', "
                  "'status': 'INVALID_ARGUMENT', 'details': [{'reason': 'API_KEY_INVALID'}]}}")


def ligar_ia(monkeypatch, gemini):
    """Liga a IA (RAIOX_IA_REAL=1), mas põe a função dada no lugar do Gemini: nunca chama a API."""
    monkeypatch.setenv("RAIOX_IA_REAL", "1")
    monkeypatch.setattr(ia, "gerar_llm", gemini)


def gemini_com_chave_errada(*args):
    raise RuntimeError(ERRO_DO_GOOGLE)


def gemini_que_responde(entrada, marcadores):
    # responde com o texto do modo sem IA, mas com tokens e custo, como uma resposta de verdade
    return ia.texto_sem_ia(entrada), {"tokens_entrada": 2262, "tokens_saida": 378, "custo_usd": 0.0011}


def test_tela_abre_com_dados_falsos_e_avisa():
    at = abrir()
    assert not at.exception
    assert "empresas e números inventados" in textos(at.warning)


def test_tela_gera_raio_x_com_dados_falsos():
    at = gerar(abrir())
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."
    assert len(at.metric) == 6                                   # os 6 indicadores
    assert "escrito por IA" not in textos(at.caption)            # sem IA, o rodapé não diz que a IA escreveu (#39)


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


def test_tela_avisa_a_falha_da_ia_sem_o_erro_tecnico(monkeypatch, capsys):       # issue #38
    ligar_ia(monkeypatch, gemini_com_chave_errada)
    at = gerar(abrir())
    assert not at.exception and not at.error
    aviso = textos(at.warning)
    assert "montado sem IA" in aviso
    assert "INVALID_ARGUMENT" not in aviso and "{" not in aviso  # o JSON do Google não vai para o telão
    assert "API_KEY_INVALID" in detalhes_tecnicos(at)           # mas não se perde: fica nos detalhes técnicos
    assert "API_KEY_INVALID" in capsys.readouterr().err         # e no log (docker compose logs tela)


def test_tela_nao_diz_que_o_texto_e_da_ia_quando_ela_falha(monkeypatch):          # issue #39
    ligar_ia(monkeypatch, gemini_com_chave_errada)
    at = gerar(abrir())
    legendas = textos(at.caption)                                # o topo e o rodapé são legendas (st.caption)
    assert "escrito pelo Gemini" not in legendas
    assert "escrito por IA" not in legendas
    assert "montado sem IA" in legendas


def test_tela_diz_que_o_texto_e_do_gemini_quando_ele_responde(monkeypatch):       # issue #39, o outro lado
    ligar_ia(monkeypatch, gemini_que_responde)
    at = gerar(abrir())
    assert not at.exception and not at.error
    assert "não respondeu" not in textos(at.warning)
    legendas = textos(at.caption)
    assert "escrito pelo Gemini" in legendas
    assert "escrito por IA" in legendas                          # o rodapé
    assert "montado sem IA" not in legendas


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
    assert "terraform apply" in textos(at.error)                 # quem subiu pelo Terraform também sabe o que fazer


def test_tela_mostra_erro_quando_nem_o_modo_sem_ia_funciona(monkeypatch):
    # uma empresa que a busca acha, mas que não está na tabela de indicadores: o raio-x falha com e sem IA
    monkeypatch.setattr(falso_dados, "buscar_empresas",
                        lambda texto: [{"cd_cvm": 12345, "nome": "SEM DADOS S.A.", "setor": "Outros"}])
    at = gerar(abrir(), busca="sem dados")
    assert not at.exception
    assert "Não foi possível gerar o raio-x" in textos(at.error)
    assert not at.subheader                                      # nenhum raio-x na tela


def test_tela_avisa_quando_o_banco_esta_vazio(banco_vazio):
    at = abrir()
    at.text_input(key="busca").input("alfa").run()
    assert not at.exception and not at.error
    assert "O banco está vazio" in textos(at.warning)
    assert "infra/main.tf" in textos(at.warning)                 # os comandos de carga de quem subiu pelo Terraform


def test_tela_busca_no_banco_e_registra_a_consulta(banco_vazio):
    with banco_vazio.begin() as conn:
        # o catálogo como sai do carregar_dfp.py, só com a empresa 90001 da tabela falsa
        pd.DataFrame([["90001", "ALFA NORTE S.A.", "Transporte e logística", "3.01", "Receita de Venda",
                       100.0, 2025, "DRE", "con"]],
                     columns=["cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor", "ano", "demonstracao",
                              "origem"]).to_sql("contas", conn, index=False)
        pd.DataFrame([{"cd_cvm": "90001", "situacao": "ATIVO"}]).to_sql("empresas", conn, index=False)
        pd.DataFrame([{"cd_cvm": 90001, "nome": "ALFA NORTE S.A.", "setor": "Transporte e logística"}]).to_sql(
            "indicadores", conn, index=False)

    at = gerar(abrir())
    assert not at.exception and not at.error
    assert at.subheader[0].value == "ALFA NORTE S.A."

    with banco_vazio.begin() as conn:
        linhas = conn.execute(text("SELECT registro_json FROM consultas")).fetchall()
    assert len(linhas) == 1
    registro = json.loads(linhas[0][0])
    assert registro["cd_cvm"] == 90001                           # número, como pede o C1
    assert registro["produto"] == "software de gestão de frota"
