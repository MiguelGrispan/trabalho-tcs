"""
Testes automáticos do Raio-X. Rodar na raiz do repositório:  python -m pytest -q
Nenhum teste chama a API do Gemini (não gasta crédito).
"""
import os
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

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


# ---------------------------------------------------------------- regra de ouro: número que não é dígito
# Os nomes começam com "regra_de_ouro", e não com "validador": o notebook do aprender/ espera exatamente
# "5 passed" ao rodar "pytest -k validador".
@pytest.mark.parametrize("frase", [
    "A receita cresceu cerca de dez por cento.",
    "O lucro foi de vinte milhões de reais.",
    "A margem EBIT é quase o dobro do grupo.",
    "O endividamento caiu pela metade.",
    "A empresa tem três fábricas e mil funcionários.",
])
def test_regra_de_ouro_remove_numero_por_extenso(frase):
    r = ia.validar_e_preencher(rx(resumo=frase), VALORES)
    assert r["resumo"] == "", frase
    assert r["removidos"][0]["motivo"].startswith("número por extenso"), frase


@pytest.mark.parametrize("frase", [                       # issue #50: passavam pelo validador até 05/11
    "A receita dobrou no período.",
    "A margem triplicou.",
    "Um quarto da receita vem de fora.",
    "O lucro duplicou desde o último exercício.",
    "A dívida quadruplicou.",
    "A receita dobra a cada ciclo.",
])
def test_regra_de_ouro_remove_quantidade_sem_algarismo(frase):
    r = ia.validar_e_preencher(rx(resumo=frase), VALORES)
    assert r["resumo"] == "", frase
    assert r["removidos"][0]["motivo"].startswith("número por extenso"), frase


@pytest.mark.parametrize("frase", ["Crescimento de ½ do grupo.", "A margem subiu ² pontos.",
                                   "Receita de R$ ２０ bi.", "Fase Ⅲ da expansão."])
def test_regra_de_ouro_remove_simbolo_numerico(frase):
    r = ia.validar_e_preencher(rx(resumo=frase), VALORES)
    assert r["resumo"] == "", frase
    assert r["removidos"][0]["motivo"] == "dígito fora de marcador", frase


def test_regra_de_ouro_vale_para_perguntas_e_lacunas():
    p = ia.Pergunta(texto="Os dez maiores clientes concentram a receita?", base="receita")
    r = ia.validar_e_preencher(rx(perguntas=[p], lacunas=["Orçamento de cem mil reais"]), VALORES)
    assert r["perguntas"] == [] and r["lacunas"] == [] and len(r["removidos"]) == 2


def test_regra_de_ouro_aceita_texto_sem_numero():
    # nome do indicador com "dois", ordinais, "um/uma" e palavras que contêm um número ("dezembro")
    frase = ("O crescimento em dois anos ficou acima do grupo; em dezembro, a primeira reunião "
             "pode mostrar um caminho para o segundo semestre e para o quarto trimestre.")
    r = ia.validar_e_preencher(rx(resumo=frase), VALORES)
    assert r["resumo"] == frase and r["removidos"] == []


@pytest.mark.parametrize("produto", ["10%", "dez por cento"])
def test_regra_de_ouro_produto_numerico_nao_esconde_numero(produto):
    # sem a trava do normalizar(), o número do LLM virava {produto} e voltava igual depois do validador
    r = ia.validar_e_preencher(rx(resumo=f"A margem EBIT é de {produto}."), {**VALORES, "produto": produto})
    assert r["resumo"] == ""


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


# ---------------------------------------------------------------- prompt: regras v2 da Náthally (ED3)
def test_prompt_usa_as_regras_da_nathally():
    # o Gemini recebe o arquivo dela inteiro, sem cópia, mais as notas do código
    texto = ia.ARQ_REGRAS.read_text(encoding="utf-8").strip()
    assert ia.regras().startswith(texto) and ia.regras().endswith(ia.NOTAS_DO_CODIGO)
    assert "números por extenso" in texto            # pendência de 27/10: o prompt também proíbe "dez por cento"


def test_prompt_mantem_os_marcadores_com_chave():
    # no LangChain, {x} é variável: as chaves das regras precisam chegar ao Gemini como estão
    sistema, pedido = ia._prompt().format_messages(marcadores="{receita}", entrada="{}")
    assert "{margem_ebit}" in sistema.content and "{cresc_2a_grupo}" in sistema.content
    assert pedido.content == "Marcadores permitidos: {receita}\n\nEntrada:\n{}"


def test_prompt_so_oferece_marcadores_de_indicador_com_valor(monkeypatch):
    valores = {**{m: "6,2%" for i in ia.INDICADORES for m in (i, f"{i}_grupo")}, **VALORES, "cresc_2a": "sem dado"}
    assert ia.marcadores_do_llm(valores) == [m for i in ia.INDICADORES for m in (i, f"{i}_grupo")
                                             if m != "cresc_2a"]          # sem empresa, setor, ano e produto
    pedidos = []

    def gemini_falso(entrada, marcadores):
        pedidos.append(marcadores)
        return ia.texto_sem_ia(entrada), {"tokens_entrada": 0, "tokens_saida": 0, "custo_usd": 0.0}
    monkeypatch.setattr(ia, "gerar_llm", gemini_falso)
    ia.preparar_raio_x(90001, "software de gestão", "primeira reunião")
    assert "empresa" not in pedidos[0] and "margem_ebit_grupo" in pedidos[0]


def test_texto_sem_ia_segue_as_regras_v2():
    # plano B da demo: o texto fixo segue a mesma forma que as regras pedem ao Gemini
    seg = ia._base()
    for cd in seg["cd_cvm"]:
        rx = ia.texto_sem_ia(ia.montar(seg, int(cd), "software de gestão", "primeira reunião")[0])
        assert len(re.findall(r"[.!?](?:\s|$)", rx.resumo)) == 3, cd                       # três frases
        assert all(p.texto.startswith(("Como", "Quais", "O que", "Onde")) for p in rx.perguntas), cd
        assert all(p.base in ia.INDICADORES for p in rx.perguntas), cd
        assert all("?" not in l and not l.startswith(("Quem", "Qual", "Como")) for l in rx.lacunas), cd


def test_gemini_desiste_rapido_se_a_api_travar(monkeypatch):
    # sem limite, a biblioteca espera para sempre e tenta 6 vezes: na banca, a tela ficaria girando
    # em vez de mostrar o erro e cair no modo sem IA. Só monta o cliente: não chama a API.
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-falsa-do-teste")
    llm = ia._llm()
    assert llm.timeout == ia.TEMPO_LIMITE_S and ia.TEMPO_LIMITE_S <= 20
    assert llm.max_retries == ia.TENTATIVAS and ia.TENTATIVAS <= 2


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


def test_tela_aberta_antes_da_cvm_acha_a_empresa_depois(tmp_path, monkeypatch):
    # issue #43: a tela gerou um raio-x com os falsos e depois a CVM foi carregada (e mais tarde recarregada).
    # Antes, o raio-x seguia com a tabela guardada na memória: "Empresa ... não está na tabela de indicadores".
    ind = tmp_path / "indicadores.csv"
    monkeypatch.setattr(segmentos, "ARQ_INDICADORES", ind)
    monkeypatch.setattr(segmentos, "ARQ_SEGMENTOS", tmp_path / "segmentos.csv")
    ia.preparar_raio_x(90001, "software", "reunião", usar_ia=False)    # 1. ainda sem a CVM: tabela falsa

    real = pd.read_csv(segmentos.ARQ_FALSO)
    real["cd_cvm"] += 1000                                               # 2. a "CVM" chega, com outros códigos
    real.to_csv(ind, index=False)
    monkeypatch.setenv("RAIOX_DADOS", "real")
    assert ia.preparar_raio_x(91001, "software", "reunião", usar_ia=False)["empresa"] == real.loc[0, "nome"]

    real.loc[0, "nome"] = "NOME NOVO S.A."                               # 3. o indicadores.csv é refeito
    real.to_csv(ind, index=False)
    depois = ind.stat().st_mtime + 10
    os.utime(ind, (depois, depois))
    assert ia.preparar_raio_x(91001, "software", "reunião", usar_ia=False)["empresa"] == "NOME NOVO S.A."


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


def test_escolher_k_ignora_k_com_grupo_pequeno():
    # com os dados reais (ED1), k = 4 tinha a maior silhueta (0,77) só porque separava 9 empresas extremas
    assert segmentos.escolher_k({3: 0.30, 4: 0.77}, {3: 0.15, 4: 0.015}) == 3
    assert segmentos.escolher_k({3: 0.30, 4: 0.77}, {3: 0.01, 4: 0.015}) == 4   # nenhum vale: fica a maior silhueta


def test_segmentar_nao_deixa_grupo_com_menos_de_5_por_cento():
    # uma empresa extrema (margem de -10.000%, como as do ED1) não pode virar um grupo só dela
    df, _ = segmentos.carregar_indicadores()
    extrema = df.iloc[[0]].assign(cd_cvm=99999, margem_ebit=-100.0, margem_liquida=-100.0, endividamento=50.0)
    df = pd.concat([df, extrema], ignore_index=True)
    seg, _, _ = segmentos.segmentar(df)
    assert seg["grupo"].value_counts().min() / len(segmentos.treino(df)) >= segmentos.MENOR_GRUPO


def test_empresa_pequena_fica_fora_do_treino_mas_ganha_grupo_e_parecidas():
    df, _ = segmentos.carregar_indicadores()
    pequenas = df["cd_cvm"].iloc[:2].tolist()
    df.loc[:1, "receita"] = segmentos.RECEITA_MINIMA / 2
    seg, _, _ = segmentos.segmentar(df)
    assert len(segmentos.treino(df)) == len(df) - 2
    assert seg["grupo"].notna().all() and all(len(p) == 5 for p in seg["parecidas"])
    assert not any(c in p for p in seg["parecidas"] for c in pequenas)    # parecidas vêm só do treino


def test_segmentos_csv_e_refeito_quando_o_codigo_muda(tmp_path, monkeypatch):
    # o data/segmentos.csv gravado por uma versão velha do modelo não pode ser reaproveitado
    monkeypatch.setenv("RAIOX_DADOS", "real")
    ind, arq = tmp_path / "indicadores.csv", tmp_path / "segmentos.csv"
    df = pd.read_csv(segmentos.ARQ_FALSO)
    df.to_csv(ind, index=False)
    arq.write_text("cd_cvm,grupo,parecidas\n")                           # segmentos.csv velho e vazio
    antes = Path(segmentos.__file__).stat().st_mtime - 60
    os.utime(ind, (antes - 60, antes - 60))
    os.utime(arq, (antes, antes))                                         # mais novo que os dados, mais velho que o código
    monkeypatch.setattr(segmentos, "ARQ_INDICADORES", ind)
    monkeypatch.setattr(segmentos, "ARQ_SEGMENTOS", arq)
    seg = segmentos.carregar_segmentos(df)
    assert len(seg) == 30 and seg["grupo"].notna().all()


def test_segmentos_funciona_com_data_so_de_leitura(tmp_path, monkeypatch):
    # no Docker, a data/ pode vir montada só para leitura, e o segmentos.py da imagem é sempre mais novo que o
    # segmentos.csv: os grupos são refeitos e não dá para gravar. A tela não pode quebrar por isso.
    monkeypatch.setenv("RAIOX_DADOS", "real")
    ind = tmp_path / "indicadores.csv"
    df = pd.read_csv(segmentos.ARQ_FALSO)
    df.to_csv(ind, index=False)
    monkeypatch.setattr(segmentos, "ARQ_INDICADORES", ind)
    monkeypatch.setattr(segmentos, "ARQ_SEGMENTOS", tmp_path / "segmentos.csv")

    def sem_permissao(seg):
        raise OSError(30, "Read-only file system")
    monkeypatch.setattr(segmentos, "salvar", sem_permissao)
    seg = segmentos.carregar_segmentos(df)
    assert len(seg) == 30 and seg["grupo"].notna().all()

# ---------------------------------------------------------------- checador de dados
def test_checador_pega_os_erros_plantados():
    ind = pd.read_csv(PASTA / "falsos" / "indicadores_com_erros.csv")
    contas = pd.read_csv(PASTA / "falsos" / "contas_falsas.csv", dtype={"cd_conta": str})
    alertas, _ = checador.checar(ind, contas)
    assert set(alertas["cd_cvm"]) == {90004, 90008, 90015, 90020, 90023}
