"""
Raio-X Comercial · tela em Streamlit · versão 0 (Miguel)

Rodar:
    pip install streamlit pandas
    streamlit run app.py

Hoje a tela usa arquivos FALSOS (pasta falsos/) com o mesmo formato dos contratos:
  C1 · buscar_empresas, registrar_consulta  → dados.py do Marcos
  C3 · preparar_raio_x                       → ia.py do Eduardo
Quando o dados.py do Marcos existir, troque USAR_DADOS_FALSOS para False.
Para usar a IA de verdade (ia.py do Eduardo), rode com RAIOX_IA_REAL=1 (o rodar_tela_com_ia.command faz isso).
"""
import os
import time

import pandas as pd
import streamlit as st

# Troque para False quando o dados.py do Marcos existir.
USAR_DADOS_FALSOS = True
# IA de verdade (Gemini, gasta crédito) só quando a variável RAIOX_IA_REAL=1 estiver definida:
# o rodar_tela_com_ia.command faz isso. Sem ela, o texto é montado sem IA.
USAR_IA_REAL = os.getenv("RAIOX_IA_REAL") == "1"

if USAR_DADOS_FALSOS:
    from falsos.falso_dados import buscar_empresas, registrar_consulta
else:
    from dados import buscar_empresas, registrar_consulta

if USAR_IA_REAL:
    from ia import preparar_raio_x
else:
    from falsos.falso_ia import preparar_raio_x

st.set_page_config(page_title="Raio-X Comercial", layout="wide")

def md(texto: str) -> str:
    """O Streamlit lê '$...$' como fórmula matemática. Escapamos o $ para 'R$' aparecer certo."""
    return str(texto).replace("$", "\\$")


POSICAO = {"acima": "▲ acima do grupo", "abaixo": "▼ abaixo do grupo",
           "em linha": "● em linha com o grupo", "sem dado": "sem dado"}

# ------------------------------------------------------------------ cabeçalho
st.title("Raio-X Comercial")
st.caption("Prepare a primeira reunião com uma companhia aberta: números da CVM, comparação com "
           "empresas parecidas e perguntas para a conversa.")
if USAR_DADOS_FALSOS:
    st.warning("Versão de teste: empresas e números inventados.")
st.caption("Texto escrito pelo Gemini." if USAR_IA_REAL else "Texto montado sem IA (modo de teste, sem custo).")

# ------------------------------------------------------------------ entrada (barra lateral)
with st.sidebar:
    st.header("1. Empresa")
    texto = st.text_input("Digite parte do nome", key="busca", placeholder="ex.: alfa")
    opcoes = buscar_empresas(texto) if len(texto.strip()) >= 2 else []
    escolha = None
    if texto.strip() and not opcoes:
        st.info("Nenhuma empresa encontrada com esse nome.")
    if opcoes:
        escolha = st.selectbox("Escolha a empresa", opcoes, index=None, placeholder="Selecione",
                               format_func=lambda e: f"{e['nome']} · {e['setor']}", key="empresa")

    st.header("2. Sua reunião")
    produto = st.text_input("O que você vende", key="produto",
                            placeholder="ex.: software de gestão de frota")
    objetivo = st.text_area("Objetivo da reunião", key="objetivo", height=90,
                            placeholder="ex.: primeira conversa com a diretoria de operações")

    faltando = [n for n, ok in [("a empresa", escolha), ("o produto", produto.strip()),
                                ("o objetivo", objetivo.strip())] if not ok]
    gerar = st.button("Gerar raio-x", type="primary", disabled=bool(faltando))
    if faltando:
        st.caption("Falta preencher: " + ", ".join(faltando) + ".")

# ------------------------------------------------------------------ gerar
if gerar:
    with st.spinner("Montando o raio-x..."):
        t0 = time.time()
        try:
            rx = preparar_raio_x(escolha["cd_cvm"], produto.strip(), objetivo.strip())
        except Exception as erro:  # API fora do ar, limite de uso, empresa sem dados...
            st.error("Não foi possível gerar o raio-x agora. Tente de novo em um minuto. "
                     f"Se continuar, avise o grupo com este detalhe: {erro}")
            st.stop()
    st.session_state["rx"] = rx
    uso = rx.get("uso", {})
    registrar_consulta({"cd_cvm": escolha["cd_cvm"], "produto": produto.strip(), "objetivo": objetivo.strip(),
                        "tempo_s": round(time.time() - t0, 1), "tokens_entrada": uso.get("tokens_entrada"),
                        "tokens_saida": uso.get("tokens_saida"), "custo_usd": uso.get("custo_usd")})

rx = st.session_state.get("rx")
if not rx:
    st.info("Na barra à esquerda, escolha a empresa, diga o que você vende e o objetivo da reunião. "
            "Depois clique em **Gerar raio-x**.")
    st.stop()

# ------------------------------------------------------------------ resultado
st.subheader(rx["empresa"])
st.caption(f"{rx['setor']} · exercício {rx['ano']} · grupo {rx['grupo']['numero']} "
           f"({rx['grupo']['tamanho']} empresas de perfil parecido)")

colunas = st.columns(3)
for n, ind in enumerate(rx["indicadores"]):
    with colunas[n % 3]:
        st.metric(ind["nome"], ind["valor"])
        st.caption(md(f"{POSICAO.get(ind['posicao'], ind['posicao'])}: {ind['grupo']}"))

pct = [i for i in rx["indicadores"] if i.get("unidade") == "%" and i.get("valor_num") is not None]
if pct:
    st.markdown("**Empresa × grupo de empresas parecidas (%)**")
    grafico = pd.DataFrame({"Indicador": [i["nome"] for i in pct],
                            "Empresa": [i["valor_num"] for i in pct],
                            "Grupo": [i["grupo_num"] for i in pct]}).set_index("Indicador")
    try:
        st.bar_chart(grafico, stack=False)   # barras lado a lado (Streamlit recente)
    except TypeError:
        st.bar_chart(grafico)                # versões antigas não têm stack

nome_de = {i["id"]: i["nome"] for i in rx["indicadores"]}
esq, dir_ = st.columns([3, 2], gap="large")
with esq:
    st.markdown("#### Resumo")
    st.markdown(md(rx["resumo"]) if rx["resumo"] else "_O resumo foi removido pelo validador._")
    st.markdown("#### Perguntas para a reunião")
    for n, p in enumerate(rx["perguntas"], 1):
        base = "o que falta saber" if p["base"] == "lacuna" else nome_de.get(p["base"], p["base"])
        st.markdown(f"{n}. {md(p['texto'])}  \n:gray[base: {base}]")
with dir_:
    st.markdown("#### O que os números não dizem")
    for l in rx["lacunas"]:
        st.markdown(f"- {md(l)}")
    st.markdown("#### Empresas parecidas para prospectar")
    st.dataframe(pd.DataFrame(rx["parecidas"])[["nome", "setor"]].rename(columns={"nome": "Empresa", "setor": "Setor"}),
                 hide_index=True)

with st.expander("De onde vem cada número"):
    st.dataframe(pd.DataFrame([{"Indicador": i["nome"], "Empresa": i["valor"], "Grupo": i["grupo"],
                                "Fonte": i["fonte"]} for i in rx["indicadores"]]), hide_index=True)

with st.expander("Detalhes técnicos"):
    uso = rx.get("uso", {})
    st.write(f"Tokens: {uso.get('tokens_entrada')} de entrada e {uso.get('tokens_saida')} de saída · "
             f"custo US$ {uso.get('custo_usd', 0):.4f} · {uso.get('tempo_s')} s")
    if rx.get("removidos"):
        st.write("Trechos removidos pelo validador:")
        st.json(rx["removidos"])
    else:
        st.write("Nenhum trecho removido pelo validador.")

st.caption("Confira antes de usar. Os números vêm das demonstrações entregues à CVM no último exercício; "
           "o texto é escrito por IA, que não escreve números. Não é recomendação de investimento.")
