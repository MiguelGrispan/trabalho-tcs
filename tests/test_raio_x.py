"""
Testes automáticos do Raio-X. Rodar na raiz do repositório:  python -m pytest -q
Nenhum teste chama a API do Gemini (não gasta crédito).
"""
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA))

from raiox import checagem as checador  # noqa: E402
from raiox import ia  # noqa: E402
from raiox import segmentos  # noqa: E402

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
    assert set(r["grupo"]) == {"numero", "tamanho"}
    assert all(set(p) == {"cd_cvm", "nome", "setor"} for p in r["parecidas"])
    assert set(r["uso"]) == {"tokens_entrada", "tokens_saida", "custo_usd", "tempo_s"}


def test_fonte_concorda_com_dre_e_balanco():
    r = ia.preparar_raio_x(90001, "software de gestão de frota", "conhecer a operação", usar_ia=False)
    fontes = {i["id"]: i["fonte"] for i in r["indicadores"]}
    assert "DRE consolidada" in fontes["margem_ebit"]
    assert "balanço consolidado" in fontes["ativo_total"]
    assert "balanço consolidado" in fontes["endividamento"]


def test_modo_sem_ia_funciona_para_todas_as_empresas_falsas():
    # plano B da demo: sem a API, todo raio-x sai inteiro e sem nada barrado pelo validador
    df, falso = segmentos.carregar_indicadores()
    assert falso
    for cd in df["cd_cvm"]:
        r = ia.preparar_raio_x(int(cd), "software de gestão", "primeira reunião", usar_ia=False)
        assert r["removidos"] == [], cd
        assert r["resumo"] and len(r["perguntas"]) >= 3 and len(r["lacunas"]) >= 2, cd


# ---------------------------------------------------------------- dados reais × falsos
def test_raiox_dados_falsos_ignora_tabela_real(tmp_path, monkeypatch):
    real = tmp_path / "indicadores.csv"
    pd.read_csv(PASTA / "falsos" / "tabela_falsa.csv").head(3).to_csv(real, index=False)
    monkeypatch.setattr(segmentos, "ARQ_INDICADORES", real)
    df, falso = segmentos.carregar_indicadores()          # RAIOX_DADOS=falsos (conftest.py)
    assert falso and len(df) == 30
    monkeypatch.setenv("RAIOX_DADOS", "real")
    df, falso = segmentos.carregar_indicadores()
    assert not falso and len(df) == 3


def test_com_dados_falsos_nada_e_gravado_em_data(tmp_path, monkeypatch):
    arq = tmp_path / "segmentos.csv"
    monkeypatch.setattr(segmentos, "ARQ_SEGMENTOS", arq)
    ia.preparar_raio_x(90001, "software", "reunião", usar_ia=False)
    assert not arq.exists()


# ---------------------------------------------------------------- segmentos
def test_segmentar_aguenta_receita_zero():
    df, _ = segmentos.carregar_indicadores()
    df.loc[0, "receita"] = 0
    seg, _, _ = segmentos.segmentar(df)
    assert seg["grupo"].notna().all()
    assert all(len(p) == 5 for p in seg["parecidas"])


def test_segmentar_acha_os_tres_perfis_da_tabela_falsa():
    # a tabela falsa foi gerada com 3 perfis; o K-means deve achar k = 3 e acertar quase todas as empresas
    # (hoje 29 de 30: uma "pequena_endividada" cai no grupo de "cresce_margem_baixa")
    df, _ = segmentos.carregar_indicadores()
    seg, silhuetas, k = segmentos.segmentar(df)
    assert k == 3 and silhuetas[3] == max(silhuetas.values())
    tabela = pd.crosstab(seg["perfil_real"], seg["grupo"])
    assert tabela.max(axis=1).sum() / len(seg) >= 0.9            # cada perfil fica quase todo num grupo só
    assert tabela.idxmax(axis=1).is_unique                       # e cada perfil tem um grupo diferente


def test_graficos_sao_gravados(tmp_path):
    df, _ = segmentos.carregar_indicadores()
    seg, silhuetas, k = segmentos.segmentar(df)
    segmentos.grafico_silhueta(silhuetas, k, tmp_path / "silhueta.png")
    segmentos.grafico_grupos(seg, tmp_path / "grupos.png")
    assert (tmp_path / "silhueta.png").stat().st_size > 0
    assert (tmp_path / "grupos.png").stat().st_size > 0


# ---------------------------------------------------------------- checador de dados
def test_checador_pega_os_erros_plantados():
    ind = pd.read_csv(PASTA / "falsos" / "indicadores_com_erros.csv")
    contas = pd.read_csv(PASTA / "falsos" / "contas_falsas.csv", dtype={"cd_conta": str})
    alertas, _ = checador.checar(ind, contas)
    assert set(alertas["cd_cvm"]) == {90004, 90008, 90015, 90020, 90023}
