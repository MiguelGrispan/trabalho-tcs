"""Testes das fontes dos números (ED17): campo `conferir` do C3. Não usam o Gemini nem precisam do PostgreSQL."""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.exc import OperationalError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from raiox import fontes, ia  # noqa: E402

ALFA = 90001   # empresa dos falsos (RAIOX_DADOS=falsos vem do conftest)


def raio_x():
    return ia.preparar_raio_x(ALFA, "ERP", "primeira reunião", usar_ia=False)


def banco_fora(*_args, **_kw):
    raise OperationalError("SELECT", {}, Exception("banco desligado"))


def test_cada_indicador_traz_as_contas_da_formula_na_ordem():
    por_id = {i["id"]: i["conferir"] for i in raio_x()["indicadores"]}
    assert [c["conta"] for c in por_id["margem_ebit"]["contas"]] == ["3.05", "3.01"]
    assert [c["conta"] for c in por_id["margem_liquida"]["contas"]] == ["3.11", "3.01"]
    assert [c["conta"] for c in por_id["endividamento"]["contas"]] == ["2.03", "1"]
    assert [c["conta"] for c in por_id["ativo_total"]["contas"]] == ["1"]
    assert [c["conta"] for c in por_id["receita"]["contas"]] == ["3.01"]


def test_valor_vem_inteiro_em_reais_igual_ao_do_arquivo():
    c = pd.read_csv(fontes.ARQ_CONTAS_FALSAS, dtype={"cd_conta": str})
    esperado = float(c[(c.cd_cvm == ALFA) & (c.cd_conta == "3.01")].iloc[0]["valor"])
    receita = next(i for i in raio_x()["indicadores"] if i["id"] == "receita")["conferir"]["contas"][0]
    assert receita["valor"] == fontes.reais(esperado)
    assert receita["valor"] == "R$ 4.913.773.388"     # sem abreviar: o usuário confere no DFP (4913773387,88 arredonda)
    assert receita["ano"] == 2025 and "Receita" in receita["descricao"]


def test_conta_de_dois_anos_antes_que_nao_existe_simplesmente_nao_aparece():
    cresc = next(i for i in raio_x()["indicadores"] if i["id"] == "cresc_2a")["conferir"]["contas"]
    assert [(c["conta"], c["ano"]) for c in cresc] == [("3.01", 2025)]   # os falsos só têm 2025


def test_falsos_nao_devolvem_link():
    assert all(i["conferir"]["link"] is None for i in raio_x()["indicadores"])


def test_reais_formata_com_ponto_de_milhar():
    assert fontes.reais(37158908000.0) == "R$ 37.158.908.000"
    assert fontes.reais(-1500.4) == "R$ -1.500"


def test_banco_fora_do_ar_deixa_conferir_vazio_e_nao_levanta_erro(monkeypatch, tmp_path):
    monkeypatch.setattr(fontes, "conectar", banco_fora)
    monkeypatch.setattr(fontes, "ARQ_LINKS", tmp_path / "nao_existe.csv")
    fontes._links_csv.cache_clear()
    assert fontes._contas(ALFA, 2025, falsos=False) == {}
    inds = [{"id": "receita"}]
    fontes.anexar(inds, ALFA, 2025, 1, falsos=False)
    assert inds[0]["conferir"] == {"contas": [], "link": None}


def test_link_vem_do_csv_quando_a_tabela_nao_existe(monkeypatch, tmp_path):
    arq = tmp_path / "links_dfp.csv"
    arq.write_text("cd_cvm,ano,versao,id_doc,link_doc\n2437,2025,1,154939,https://exemplo.cvm/doc154939\n"
                   "2437,2025,2,155000,https://exemplo.cvm/doc155000\n")
    monkeypatch.setattr(fontes, "ARQ_LINKS", arq)
    monkeypatch.setattr(fontes, "conectar", banco_fora)
    fontes._links_csv.cache_clear()
    assert fontes._link(2437, 2025, 1, falsos=False) == "https://exemplo.cvm/doc154939"
    assert fontes._link(2437, 2025, 2, falsos=False) == "https://exemplo.cvm/doc155000"   # a versão conta
    assert fontes._link(2437, 2024, 1, falsos=False) is None                              # outro exercício, outro documento
    assert fontes._link(2437, 2025, None, falsos=False) is None


def test_conferir_nao_entra_no_texto_do_llm():
    entrada, _, _ = ia.montar(ia._base(), ALFA, "ERP", "reunião")
    assert "conferir" not in str(entrada)
