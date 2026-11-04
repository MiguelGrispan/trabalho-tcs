"""
Raio-X Comercial · tela em Streamlit · versão 0 (Miguel)

Rodar (o tema em .streamlit/config.toml só vale rodando de dentro de app/):
    pip install -r requirements.txt
    cd app && streamlit run streamlit_app.py

Contratos que a tela usa:
  C1 · buscar_empresas, registrar_consulta  → raiox/dados.py do Marcos (PostgreSQL)
  C3 · preparar_raio_x                       → raiox/ia.py do Eduardo
Dados: com a data/indicadores.csv real, a busca e o registro de cada consulta usam o PostgreSQL (raiox/dados.py).
Com RAIOX_DADOS=falsos, ou sem a data/, tudo vem dos arquivos FALSOS (pasta falsos/), com o mesmo formato.
IA: com RAIOX_IA_REAL=1 o texto é escrito pelo Gemini (o aprender/atalhos/rodar_tela_com_ia.command faz isso).
Se o Gemini não responder, a tela monta o texto sem IA, avisa em uma frase e guarda o erro em "Detalhes técnicos".
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

# A raiz do repositório entra no caminho do Python para achar raiox/ e falsos/ (o Streamlit só põe app/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from raiox.ia import preparar_raio_x  # noqa: E402
from raiox.segmentos import usando_falsos  # noqa: E402

# A mesma regra do raiox/segmentos.py: assim a busca e o raio-x olham sempre a mesma tabela.
DADOS_FALSOS = usando_falsos()
# IA de verdade (Gemini, gasta crédito) só quando a variável RAIOX_IA_REAL=1 estiver definida:
# o rodar_tela_com_ia.command faz isso. Sem ela, o texto é montado sem IA.
USAR_IA_REAL = os.getenv("RAIOX_IA_REAL") == "1"

if DADOS_FALSOS:
    from falsos.falso_dados import buscar_empresas, registrar_consulta
else:
    from raiox.banco import catalogo_existe
    from raiox.dados import buscar_empresas, registrar_consulta

st.set_page_config(page_title="Raio-X Comercial", layout="wide")

def md(texto: str) -> str:
    """O Streamlit lê '$...$' como fórmula matemática. Escapamos o $ para 'R$' aparecer certo."""
    return str(texto).replace("$", "\\$")


def gerar_raio_x(cd_cvm: int, produto: str, objetivo: str) -> tuple[dict, str | None]:
    """Devolve (raio-x, erro da IA). Se a IA falhar, monta o texto sem IA: os números são os mesmos (plano B da demo)."""
    if USAR_IA_REAL:
        try:
            return preparar_raio_x(cd_cvm, produto, objetivo, usar_ia=True), None
        except Exception as erro:  # API fora do ar, limite de uso, chave errada...
            # o erro técnico vai para o log (docker compose logs tela) e para "Detalhes técnicos", nunca para o aviso
            print(f"A IA não respondeu; o texto foi montado sem IA. Erro: {erro}", file=sys.stderr)
            return preparar_raio_x(cd_cvm, produto, objetivo, usar_ia=False), str(erro)
    return preparar_raio_x(cd_cvm, produto, objetivo, usar_ia=False), None


POSICAO = {"acima": "▲ acima do grupo", "abaixo": "▼ abaixo do grupo",
           "em linha": "● em linha com o grupo", "sem dado": "sem dado"}

# ------------------------------------------------------------------ cabeçalho
st.title("Raio-X Comercial")
st.caption("Prepare a primeira reunião com uma companhia aberta: números da CVM, comparação com "
           "empresas parecidas e perguntas para a conversa.")
if DADOS_FALSOS:
    st.warning("Versão de teste: empresas e números inventados.")
else:
    st.caption("Empresas e números da CVM (DFP), buscados no banco PostgreSQL.")
# Quem escreveu o texto (Gemini ou sem IA) só se sabe depois de gerar: o espaço fica aqui e é preenchido mais abaixo.
origem_do_texto = st.empty()

# ------------------------------------------------------------------ entrada (barra lateral)
with st.sidebar:
    st.header("1. Empresa")
    texto = st.text_input("Digite parte do nome", key="busca", placeholder="ex.: alfa")
    opcoes = []
    escolha = None
    if len(texto.strip()) >= 2:
        try:
            opcoes = buscar_empresas(texto)
            if not opcoes and not DADOS_FALSOS and not catalogo_existe():
                st.warning("O banco está vazio: carregue os dados da CVM (comandos no topo do docker-compose.yml, "
                           "ou do infra/main.tf se você subiu pelo Terraform).")
            elif not opcoes:
                st.info("Nenhuma empresa encontrada com esse nome.")
        except Exception as erro:  # banco desligado, senha errada...
            st.error("Não consegui falar com o banco de dados. Ele está ligado? (`docker compose up -d banco`, "
                     f"ou `terraform apply` dentro de `infra/`). Detalhe: {erro}")
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
    cd_cvm = int(escolha["cd_cvm"])   # o contrato C1 pede número; desde o #46 o banco já devolve int, o int() fica por garantia
    with st.spinner("Montando o raio-x..."):
        t0 = time.time()
        try:
            rx, erro_ia = gerar_raio_x(cd_cvm, produto.strip(), objetivo.strip())
        except Exception as erro:  # mesmo sem IA não deu: empresa sem dados...
            st.error("Não foi possível gerar o raio-x agora. Tente de novo em um minuto. "
                     f"Se continuar, avise o grupo com este detalhe: {erro}")
            st.stop()
    st.session_state["rx"] = rx
    st.session_state["erro_ia"] = erro_ia
    uso = rx.get("uso", {})
    # try separado: se o banco falhar aqui, o raio-x já está pronto e aparece do mesmo jeito
    try:
        registrar_consulta({"cd_cvm": cd_cvm, "produto": produto.strip(), "objetivo": objetivo.strip(),
                            "tempo_s": round(time.time() - t0, 1), "tokens_entrada": uso.get("tokens_entrada"),
                            "tokens_saida": uso.get("tokens_saida"), "custo_usd": uso.get("custo_usd")})
    except Exception as erro:
        st.warning(f"O raio-x está abaixo, mas a consulta não foi registrada no banco. Detalhe: {erro}")

rx = st.session_state.get("rx")
erro_ia = st.session_state.get("erro_ia")
# Só diz "escrito pelo Gemini" quando ele respondeu de verdade nesta consulta (issue #39)
texto_do_gemini = USAR_IA_REAL and not erro_ia
if not USAR_IA_REAL:
    origem_do_texto.caption("Texto montado sem IA (modo de teste, sem custo).")
elif not rx:
    origem_do_texto.caption("IA ligada: o texto será escrito pelo Gemini.")
elif texto_do_gemini:
    origem_do_texto.caption("Texto escrito pelo Gemini.")
else:
    origem_do_texto.caption("Texto montado sem IA: o Gemini não respondeu.")
if not rx:
    st.info("Na barra à esquerda, escolha a empresa, diga o que você vende e o objetivo da reunião. "
            "Depois clique em **Gerar raio-x**.")
    st.stop()
if erro_ia:
    # uma frase só (issue #38): o erro técnico do Google fica em "Detalhes técnicos", lá embaixo
    st.warning("A IA não respondeu agora. O texto abaixo foi montado sem IA; os números são os mesmos.")

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
    if erro_ia:
        st.write("A IA não respondeu. O erro que ela devolveu:")
        st.code(erro_ia, language=None, wrap_lines=True)

st.caption("Confira antes de usar. Os números vêm das demonstrações entregues à CVM no último exercício; "
           + ("o texto é escrito por IA, que não escreve números. " if texto_do_gemini else "o texto foi montado sem IA. ")
           + "Não é recomendação de investimento.")
