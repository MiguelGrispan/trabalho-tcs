"""
Prova da IA · S1 · Eduardo · Raio-X Comercial

O que este script prova, com uma tabela FALSA de 30 empresas:
  A. tabela no formato do contrato C2 (o mesmo que o Marcos vai entregar)
  B. ML: K-means com k escolhido pela silhueta + 5 empresas parecidas
  C. entrada do LLM: valores formatados + posição contra o grupo (calculada por código)
  D. LLM com saída estruturada (Gemini via LangChain), escrevendo marcadores no lugar de números
  E. validador que rejeita dígitos + troca dos marcadores pelos valores reais

Como rodar:
  pip install pandas numpy scikit-learn pydantic python-dotenv langchain-google-genai
  python prova_ia.py --sem-llm      # testa A, B, C e E com uma resposta de exemplo (sem internet)
  python prova_ia.py                # usa o Gemini de verdade (precisa de GOOGLE_API_KEY no .env)
  python prova_ia.py --teste-digito # injeta um dígito de propósito para ver o validador rejeitar

Pronto quando (sex 23/10): 3 raio-x gerados e o --teste-digito mostrando o item rejeitado.
"""

import json
import re
import sys
import time

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

MODELO = "gemini-3.1-flash-lite"  # confira o nome exato no Google AI Studio
SEMENTE = 42

# ----------------------------------------------------------------- A. tabela falsa
# Três perfis inventados, para os grupos terem algo a encontrar.
PERFIS = {
    "grande_estavel":   dict(receita=(9.6, 0.3), cresc=(0.06, 0.04), ebit=(0.14, 0.03), liq=(0.08, 0.02), divida=(0.55, 0.06)),
    "cresce_margem_baixa": dict(receita=(9.2, 0.3), cresc=(0.25, 0.08), ebit=(0.05, 0.02), liq=(0.01, 0.02), divida=(0.70, 0.06)),
    "pequena_endividada": dict(receita=(8.4, 0.3), cresc=(-0.05, 0.06), ebit=(0.08, 0.03), liq=(-0.02, 0.03), divida=(0.82, 0.05)),
}
SETORES = ["Transporte e logística", "Energia elétrica", "Varejo", "Saúde", "Construção", "Alimentos"]
PREFIXOS = ["ALFA", "BETA", "DELTA", "GAMA", "SIGMA", "OMEGA"]   # nomes inventados: 6 × 5 = 30 empresas
SUFIXOS = ["NORTE", "SUL", "LESTE", "OESTE", "CENTRO"]


def tabela_falsa(n_por_perfil: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(SEMENTE)
    linhas, cd = [], 90001
    for perfil, p in PERFIS.items():
        for i in range(n_por_perfil):
            receita = 10 ** rng.normal(*p["receita"])
            cresc = rng.normal(*p["cresc"])
            ativo = receita * rng.uniform(0.9, 1.8)
            linhas.append(dict(
                cd_cvm=cd, nome=f"{PREFIXOS[len(linhas) % 6]} {SUFIXOS[len(linhas) // 6]} S.A.",
                setor=SETORES[len(linhas) % len(SETORES)], ano=2025,
                receita=receita, receita_2a_antes=receita / (1 + cresc), cresc_2a=cresc,
                margem_ebit=rng.normal(*p["ebit"]), margem_liquida=rng.normal(*p["liq"]),
                ativo_total=ativo, endividamento=float(np.clip(rng.normal(*p["divida"]), 0.05, 0.98)),
                origem="con", versao=1, perfil_real=perfil,  # perfil_real só existe na tabela falsa
            ))
            cd += 1
    df = pd.DataFrame(linhas)
    df.loc[3, "cresc_2a"] = np.nan  # um nulo de propósito, como vai acontecer nos dados reais
    df.loc[3, "receita_2a_antes"] = np.nan
    return df


# ----------------------------------------------------------------- B. ML
VARIAVEIS = ["log_receita", "cresc_2a", "margem_ebit", "margem_liquida", "endividamento"]


def segmentar(df: pd.DataFrame):
    X = df.assign(log_receita=np.log10(df["receita"]))[VARIAVEIS].copy()
    for c in VARIAVEIS:                                   # cortar extremos (percentis 1 e 99)
        X[c] = X[c].clip(X[c].quantile(0.01), X[c].quantile(0.99))
    X = X.fillna(X.median())                              # nulos: mediana, só para o modelo
    Xs = StandardScaler().fit_transform(X)                # padronizar

    silhuetas = {}
    for k in range(3, 9):
        km = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit(Xs)
        silhuetas[k] = silhouette_score(Xs, km.labels_)
    k = max(silhuetas, key=silhuetas.get)
    grupos = KMeans(n_clusters=k, n_init=10, random_state=SEMENTE).fit_predict(Xs)

    vizinhos = NearestNeighbors(n_neighbors=6).fit(Xs)
    _, idx = vizinhos.kneighbors(Xs)                      # a 1ª vizinha é a própria empresa
    parecidas = [list(df["cd_cvm"].iloc[linha[1:]]) for linha in idx]

    out = df.copy()
    out["grupo"] = grupos
    out["parecidas"] = parecidas
    return out, silhuetas, k


# ----------------------------------------------------------------- C. entrada do LLM
INDICADORES = {  # id: (nome, tipo de formatação)
    "receita": ("Receita líquida", "dinheiro"),
    "cresc_2a": ("Crescimento em dois anos", "variacao"),  # sem dígito no nome: o LLM copia o nome
    "margem_ebit": ("Margem EBIT", "pct"),
    "margem_liquida": ("Margem líquida", "pct"),
    "endividamento": ("Endividamento", "pct"),
    "ativo_total": ("Ativo total", "dinheiro"),
}


def fmt(v, tipo: str) -> str:
    if v is None or pd.isna(v):
        return "sem dado"
    if tipo == "dinheiro":
        return f"R$ {v / 1e9:.1f} bi".replace(".", ",") if abs(v) >= 1e9 else f"R$ {v / 1e6:.0f} mi"
    if tipo == "variacao":
        return f"{v * 100:+.0f}%"
    return f"{v * 100:.1f}%".replace(".", ",")


def montar_entrada(seg: pd.DataFrame, cd_cvm: int, produto: str, objetivo: str):
    emp = seg.loc[seg["cd_cvm"] == cd_cvm].iloc[0]
    do_grupo = seg[seg["grupo"] == emp["grupo"]]
    indicadores, valores = {}, {"empresa": emp["nome"], "setor": emp["setor"],
                                "ano": str(emp["ano"]), "produto": produto}
    for i, (nome, tipo) in INDICADORES.items():
        v, med = emp[i], do_grupo[i].median()
        if pd.isna(v):
            posicao = "sem dado"
        elif fmt(v, tipo) == fmt(med, tipo) or abs(v - med) <= 0.03 * abs(med):  # diferença pequena
            posicao = "em linha"
        else:
            posicao = "acima" if v > med else "abaixo"
        indicadores[i] = {"nome": nome, "valor": fmt(v, tipo), "grupo": fmt(med, tipo), "posicao": posicao}
        valores[i], valores[f"{i}_grupo"] = fmt(v, tipo), fmt(med, tipo)
    entrada = {"setor": emp["setor"], "produto": produto, "objetivo": objetivo, "indicadores": indicadores,
               "tamanho_do_grupo": int(len(do_grupo))}
    return entrada, valores  # 'valores' nunca vai para o LLM: é usado só para trocar os marcadores


# ----------------------------------------------------------------- D. LLM
class Pergunta(BaseModel):
    texto: str = Field(description="Pergunta aberta para a reunião. Sem dígitos; use marcadores.")
    base: str = Field(description="id do indicador que motivou a pergunta, ou 'lacuna'.")


class RaioX(BaseModel):
    resumo: str = Field(description="2 ou 3 frases sobre a empresa contra o grupo. Sem dígitos; use marcadores.")
    perguntas: list[Pergunta] = Field(description="De 3 a 5 perguntas.")
    lacunas: list[str] = Field(description="De 2 a 4 coisas úteis para a venda que os números não mostram.")


# Rascunho: a Náthally substitui pelas regras_prompt.md dela.
# ATENÇÃO: no ChatPromptTemplate, {x} é variável. Marcadores precisam de chave dupla: {{margem_ebit}}.
REGRAS = """Você prepara um raio-x para a primeira reunião comercial de um vendedor B2B.
Regras:
1. Nunca escreva números nem dígitos. Para citar um valor, use apenas os marcadores da lista, entre chaves.
2. Sempre escreva o nome do indicador e, depois, o marcador entre parênteses. Exemplo:
   "a margem EBIT ({{margem_ebit}}) está acima do grupo ({{margem_ebit_grupo}})".
   Nunca use o marcador sozinho no lugar do nome do indicador.
3. Os marcadores terminados em _grupo são o valor típico do grupo de empresas parecidas, não da empresa.
   Compare sempre com "o grupo de empresas parecidas". Nunca diga "o setor", "a média do setor" ou "o mercado".
4. Use a posição de cada indicador exatamente como veio: acima, abaixo, em linha ou sem dado.
5. Não afirme causa e efeito que os números não mostram (por exemplo, "a dívida pressiona a margem").
   Se quiser explorar uma possível causa, transforme em pergunta.
6. Para a empresa use {{empresa}}. Para o produto do vendedor escreva "a solução de {{produto}}".
   {{ano}} é o ano dos números: use só para situar os dados ("em {{ano}}"), nunca para falar de orçamento ou planos.
7. resumo: 2 ou 3 frases sobre o perfil financeiro da empresa em relação ao grupo.
8. perguntas: de 3 a 5 perguntas abertas, cada uma ligada a um único indicador e ao objetivo da reunião.
   Em base, informe o id desse indicador.
9. lacunas: de 2 a 4 coisas úteis para a venda que os números não mostram (quem decide, orçamento, fornecedor atual).
10. Não recomende investimento e não fale de ações na bolsa."""

PEDIDO = "Marcadores permitidos: {marcadores}\n\nEntrada:\n{entrada}"


def gerar_llm(entrada: dict, marcadores: list[str]):
    from dotenv import load_dotenv
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv()
    prompt = ChatPromptTemplate.from_messages([("system", REGRAS), ("human", PEDIDO)])
    llm = ChatGoogleGenerativeAI(model=MODELO, temperature=0.2)
    chain = prompt | llm.with_structured_output(RaioX, include_raw=True)  # include_raw: para ler os tokens
    t0 = time.time()
    r = chain.invoke({"marcadores": ", ".join("{" + m + "}" for m in marcadores),
                      "entrada": json.dumps(entrada, ensure_ascii=False, indent=1)})
    uso = getattr(r["raw"], "usage_metadata", None) or {}
    return r["parsed"], {"tokens_entrada": uso.get("input_tokens"), "tokens_saida": uso.get("output_tokens"),
                         "tempo_s": round(time.time() - t0, 1)}


def resposta_exemplo() -> RaioX:
    # Usada com --sem-llm, para testar o resto sem internet. É a MESMA resposta para todas as empresas,
    # então às vezes diz "acima" quando a empresa está abaixo. Esse é o tipo de erro que o validador
    # NÃO pega (ele só pega dígitos): por isso a Náthally revisa "comparação certa?" na avaliação.
    return RaioX(
        resumo="A {empresa} está acima do grupo em crescimento ({cresc_2a} contra {cresc_2a_grupo}), "
               "mas com margem operacional abaixo ({margem_ebit} contra {margem_ebit_grupo}).",
        perguntas=[Pergunta(texto="Quais custos mais pesaram na margem enquanto a receita crescia, "
                                  "e onde o {produto} poderia ajudar?", base="margem_ebit"),
                   Pergunta(texto="Como o endividamento ({endividamento}) afeta novos investimentos?",
                            base="endividamento"),
                   Pergunta(texto="Quem participa da decisão de compra de tecnologia?", base="lacuna")],
        lacunas=["Quem decide a compra de tecnologia", "Orçamento previsto para o próximo ano"],
    )


# ----------------------------------------------------------------- E. validar e preencher
MARCADOR = re.compile(r"\{([a-z0-9_]+)\}")


def checar(texto: str, permitidos: set[str]):
    desconhecidos = [m for m in MARCADOR.findall(texto) if m not in permitidos]
    if desconhecidos:
        return f"marcador desconhecido: {desconhecidos}"
    if re.search(r"\d", MARCADOR.sub("", texto)):
        return "dígito fora de marcador"
    return None


def validar_e_preencher(rx: RaioX, valores: dict):
    permitidos, removidos = set(valores), []

    def preencher(t: str) -> str:
        return MARCADOR.sub(lambda m: valores[m.group(1)], t)

    def normalizar(t: str) -> str:
        # Se o LLM escreveu o nome da empresa, o produto ou o setor por extenso, volta para o marcador.
        # Assim um nome com dígito (ex.: "3R PETROLEUM") não derruba a frase no validador.
        for chave in ("empresa", "produto", "setor"):
            if valores.get(chave):
                t = t.replace(valores[chave], "{" + chave + "}")
        return t

    resumo = normalizar(rx.resumo)
    if (motivo := checar(resumo, permitidos)):
        removidos.append({"texto": resumo, "motivo": motivo})
        resumo = ""
    perguntas = []
    for p in rx.perguntas:
        p.texto = normalizar(p.texto)
        if (motivo := checar(p.texto, permitidos)) or (p.base not in INDICADORES and p.base != "lacuna"):
            removidos.append({"texto": p.texto, "motivo": motivo or f"base inválida: {p.base}"})
        else:
            perguntas.append({"texto": preencher(p.texto), "base": p.base})
    lacunas = []
    for l in rx.lacunas:
        l = normalizar(l)
        if (motivo := checar(l, permitidos)):
            removidos.append({"texto": l, "motivo": motivo})
        else:
            lacunas.append(preencher(l))
    return {"resumo": preencher(resumo), "perguntas": perguntas, "lacunas": lacunas, "removidos": removidos}


# ----------------------------------------------------------------- rodar a prova
if __name__ == "__main__":
    sem_llm = "--sem-llm" in sys.argv
    teste_digito = "--teste-digito" in sys.argv

    df = tabela_falsa()
    df.to_csv("tabela_falsa.csv", index=False)
    seg, silhuetas, k = segmentar(df)
    print("Silhueta por k:", {kk: round(v, 3) for kk, v in silhuetas.items()}, "→ k escolhido:", k)
    print("Grupos × perfil real (deve ficar quase diagonal):")
    print(pd.crosstab(seg["grupo"], seg["perfil_real"]), "\n")

    casos = [
        (seg["cd_cvm"].iloc[0], "software de roteirização e telemetria para frotas", "primeira conversa com a diretoria de operações"),
        (seg["cd_cvm"].iloc[12], "consultoria de eficiência energética", "apresentar um diagnóstico gratuito"),
        (seg["cd_cvm"].iloc[25], "plataforma de gestão financeira", "entender prioridades do CFO para o próximo ano"),
    ]
    for cd, produto, objetivo in casos:
        entrada, valores = montar_entrada(seg, cd, produto, objetivo)
        marcadores = list(valores)
        if sem_llm or teste_digito:
            rx, uso = resposta_exemplo(), {"tokens_entrada": None, "tokens_saida": None, "tempo_s": 0}
        else:
            rx, uso = gerar_llm(entrada, marcadores)
        if teste_digito:
            rx.perguntas.append(Pergunta(texto="A margem caiu 3 pontos?", base="margem_ebit"))
        final = validar_e_preencher(rx, valores)
        nomes = seg.set_index("cd_cvm").loc[seg.set_index("cd_cvm").loc[cd, "parecidas"], "nome"].tolist()
        print("=" * 72)
        print(valores["empresa"], "· grupo", int(seg.set_index("cd_cvm").loc[cd, "grupo"]), "·", produto)
        print("Resumo:", final["resumo"])
        for p in final["perguntas"]:
            print(f"  ? {p['texto']}  [{p['base']}]")
        print("Lacunas:", "; ".join(final["lacunas"]))
        print("Parecidas:", ", ".join(nomes))
        print("Removidos:", final["removidos"] or "nenhum")
        print("Uso:", uso)
