"""
Testes automáticos do Raio-X. Rodar na pasta do projeto:  python -m pytest -q
Nenhum teste chama a API do Gemini (não gasta crédito).
"""
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA))

import checar_indicadores as checador  # noqa: E402
import ia  # noqa: E402
import segmentos  # noqa: E402

VALORES = {"empresa": "3R PETROLEUM S.A.", "produto": "ERP 360", "setor": "Petróleo", "ano": "2025",
           "margem_ebit": "6,2%", "margem_ebit_grupo": "11,8%"}


def rx(resumo="ok", perguntas=(), lacunas=()):
    return ia.RaioX(resumo=resumo, perguntas=list(perguntas), lacunas=list(lacunas))


# ---------------------------------------------------------------- validador
def test_validador_remove_digito_escrito_pela_ia():
    r = ia.validar_e_preencher(rx(resumo="A margem caiu 3 pontos."), VALORES)
    assert r["resumo"] == ""
    assert r["removidos"][0]["motivo"] == "dígito fora de marcador"


def test_validador_troca_marcador_pelo_valor():
    r = ia.validar_e_preencher(rx(resumo="A margem EBIT ({margem_ebit}) está abaixo do grupo ({margem_ebit_grupo})."),
                               VALORES)
    assert r["resumo"] == "A margem EBIT (6,2%) está abaixo do grupo (11,8%)."
    assert r["removidos"] == []


def test_validador_aceita_nome_de_empresa_e_produto_com_numero():
    r = ia.validar_e_preencher(rx(resumo="A 3R PETROLEUM S.A. avalia a solução de ERP 360."), VALORES)
    assert r["resumo"] == "A 3R PETROLEUM S.A. avalia a solução de ERP 360."


def test_validador_remove_marcador_desconhecido():
    r = ia.validar_e_preencher(rx(resumo="Lucro de {lucro_inventado}."), VALORES)
    assert r["resumo"] == ""
    assert "marcador desconhecido" in r["removidos"][0]["motivo"]


def test_validador_remove_pergunta_com_base_invalida():
    p = ia.Pergunta(texto="Como está a operação?", base="indicador_que_nao_existe")
    r = ia.validar_e_preencher(rx(perguntas=[p]), VALORES)
    assert r["perguntas"] == []


# ---------------------------------------------------------------- contrato C3
def test_preparar_raio_x_segue_o_contrato_c3():
    r = ia.preparar_raio_x(90001, "software de gestão de frota", "conhecer a operação", usar_ia=False)
    for chave in ["empresa", "setor", "ano", "indicadores", "grupo", "parecidas",
                  "resumo", "perguntas", "lacunas", "removidos", "uso"]:
        assert chave in r, chave
    assert len(r["indicadores"]) == 6
    for i in r["indicadores"]:
        assert set(i) == {"id", "nome", "valor", "grupo", "posicao", "fonte", "valor_num", "grupo_num", "unidade"}
        assert i["posicao"] in {"acima", "abaixo", "em linha", "sem dado"}
    assert len(r["parecidas"]) == 5
    assert r["removidos"] == []


# ---------------------------------------------------------------- segmentos
def test_segmentar_aguenta_receita_zero():
    df, _ = segmentos.carregar_indicadores()
    df.loc[0, "receita"] = 0
    seg, _, _ = segmentos.segmentar(df)
    assert seg["grupo"].notna().all()
    assert all(len(p) == 5 for p in seg["parecidas"])


# ---------------------------------------------------------------- checador de dados
def test_checador_pega_os_erros_plantados():
    ind = pd.read_csv(PASTA / "falsos" / "indicadores_com_erros.csv")
    contas = pd.read_csv(PASTA / "falsos" / "contas_falsas.csv", dtype={"cd_conta": str})
    alertas, _ = checador.checar(ind, contas)
    assert set(alertas["cd_cvm"]) == {90004, 90008, 90015, 90020, 90023}
