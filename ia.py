"""
ia.py · Eduardo · contrato C3 (passo 6 do fluxo)

    preparar_raio_x(cd_cvm, produto, objetivo) -> dict no formato do contrato C3

O LLM escreve o texto usando marcadores como {margem_ebit}; nunca escreve números.
O validador remove qualquer trecho com dígito, e o código troca os marcadores pelos valores da tabela.

Rodar um exemplo:
    python ia.py --cvm 90001 --produto "software de gestão de frota" --objetivo "primeira conversa com operações"
    python ia.py --cvm 90001 --produto "..." --objetivo "..." --sem-ia     # texto montado sem IA (não gasta crédito)
"""
import argparse
import json
import re
import time
from functools import lru_cache

import pandas as pd
from pydantic import BaseModel, Field

import segmentos

MODELO = "gemini-3.1-flash-lite"
PRECO_US_POR_MILHAO = {"entrada": 0.25, "saida": 1.50}  # página oficial de preços do Google, 20/10/2026

# id: (nome na tela, nome dentro do texto, tipo de formatação, fonte)
INDICADORES = {
    "receita":        ("Receita líquida", "receita líquida", "dinheiro", "DRE {d} · conta 3.01"),
    "cresc_2a":       ("Crescimento em dois anos", "crescimento em dois anos", "variacao",
                       "DRE {d} · conta 3.01 ({ano} e {ano2})"),
    "margem_ebit":    ("Margem EBIT", "margem EBIT", "pct", "DRE {d} · contas 3.05 ÷ 3.01"),
    "margem_liquida": ("Margem líquida", "margem líquida", "pct", "DRE {d} · contas 3.11 ÷ 3.01"),
    "endividamento":  ("Endividamento", "endividamento", "pct", "balanço {d} · contas 2.03 e 1"),
    "ativo_total":    ("Ativo total", "ativo total", "dinheiro", "balanço {d} · conta 1"),
}
# Os nomes não têm dígitos de propósito: o LLM copia o nome, e o validador derrubaria a frase.


# ------------------------------------------------------------------ dados
@lru_cache(maxsize=1)
def _base() -> pd.DataFrame:
    df, _ = segmentos.carregar_indicadores()
    return segmentos.carregar_segmentos(df)


def fmt(v, tipo: str) -> str:
    if v is None or pd.isna(v):
        return "sem dado"
    if tipo == "dinheiro":
        return f"R$ {v / 1e9:.1f} bi".replace(".", ",") if abs(v) >= 1e9 else f"R$ {v / 1e6:.0f} mi"
    if tipo == "variacao":
        return f"{v * 100:+.0f}%"
    return f"{v * 100:.1f}%".replace(".", ",")


def num(v, tipo: str):
    """Valor numérico para o gráfico da tela: R$ milhões ou %."""
    if v is None or pd.isna(v):
        return None
    return round(float(v) / 1e6, 1) if tipo == "dinheiro" else round(float(v) * 100, 1)


def montar(seg: pd.DataFrame, cd_cvm: int, produto: str, objetivo: str):
    linhas = seg.loc[seg["cd_cvm"] == cd_cvm]
    if linhas.empty:
        raise ValueError(f"Empresa {cd_cvm} não está na tabela de indicadores.")
    emp = linhas.iloc[0]
    do_grupo = seg[seg["grupo"] == emp["grupo"]]
    demonstracao = "individual" if str(emp.get("origem", "con")) == "ind" else "consolidada"
    ano = int(emp["ano"])

    indicadores_c3, para_llm = [], {}
    valores = {"empresa": emp["nome"], "setor": emp["setor"], "ano": str(ano), "produto": produto}
    for i, (nome, _, tipo, fonte) in INDICADORES.items():
        v, med = emp[i], do_grupo[i].median()
        if pd.isna(v):
            posicao = "sem dado"
        elif fmt(v, tipo) == fmt(med, tipo) or abs(v - med) <= 0.03 * abs(med):   # diferença pequena
            posicao = "em linha"
        else:
            posicao = "acima" if v > med else "abaixo"
        indicadores_c3.append({
            "id": i, "nome": nome, "valor": fmt(v, tipo), "grupo": fmt(med, tipo), "posicao": posicao,
            "fonte": f"DFP {ano} · " + fonte.format(d=demonstracao, ano=ano, ano2=ano - 2),
            "valor_num": num(v, tipo), "grupo_num": num(med, tipo),
            "unidade": "R$ milhões" if tipo == "dinheiro" else "%"})
        para_llm[i] = {"nome": nome, "valor": fmt(v, tipo), "grupo": fmt(med, tipo), "posicao": posicao}
        valores[i], valores[f"{i}_grupo"] = fmt(v, tipo), fmt(med, tipo)

    entrada = {"setor": emp["setor"], "produto": produto, "objetivo": objetivo,
               "indicadores": para_llm, "tamanho_do_grupo": int(len(do_grupo))}
    por_cd = seg.set_index("cd_cvm")
    parecidas = [{"cd_cvm": int(c), "nome": por_cd.loc[c, "nome"], "setor": por_cd.loc[c, "setor"]}
                 for c in emp["parecidas"] if c in por_cd.index]
    extra = {"empresa": emp["nome"], "setor": emp["setor"], "ano": ano, "indicadores": indicadores_c3,
             "grupo": {"numero": int(emp["grupo"]), "tamanho": int(len(do_grupo))}, "parecidas": parecidas}
    return entrada, valores, extra   # 'valores' nunca vai para o LLM: serve só para trocar os marcadores


# ------------------------------------------------------------------ LLM
class Pergunta(BaseModel):
    texto: str = Field(description="Pergunta aberta para a reunião. Sem dígitos; use marcadores.")
    base: str = Field(description="id do indicador que motivou a pergunta, ou 'lacuna'.")


class RaioX(BaseModel):
    resumo: str = Field(description="2 ou 3 frases sobre a empresa contra o grupo. Sem dígitos; use marcadores.")
    perguntas: list[Pergunta] = Field(description="De 3 a 5 perguntas.")
    lacunas: list[str] = Field(description="De 2 a 4 coisas úteis para a venda que os números não mostram.")


# Regras v3. A Náthally é dona do texto das regras (prompts/regras_prompt.md); quando ela mandar a versão dela,
# troque aqui. ATENÇÃO: no ChatPromptTemplate, {x} é variável. Marcadores precisam de chave dupla: {{margem_ebit}}.
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


@lru_cache(maxsize=1)
def _chain():
    from dotenv import load_dotenv
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv()
    prompt = ChatPromptTemplate.from_messages([("system", REGRAS), ("human", PEDIDO)])
    llm = ChatGoogleGenerativeAI(model=MODELO, temperature=0.2)
    return prompt | llm.with_structured_output(RaioX, include_raw=True)   # include_raw: para ler os tokens


def gerar_llm(entrada: dict, marcadores: list[str]) -> tuple[RaioX, dict]:
    r = _chain().invoke({"marcadores": ", ".join("{" + m + "}" for m in marcadores),
                         "entrada": json.dumps(entrada, ensure_ascii=False, indent=1)})
    if r.get("parsed") is None:
        raise RuntimeError(f"O modelo não devolveu o formato esperado: {r.get('parsing_error')}")
    uso = getattr(r["raw"], "usage_metadata", None) or {}
    t_in, t_out = uso.get("input_tokens") or 0, uso.get("output_tokens") or 0
    custo = (t_in * PRECO_US_POR_MILHAO["entrada"] + t_out * PRECO_US_POR_MILHAO["saida"]) / 1_000_000
    return r["parsed"], {"tokens_entrada": t_in, "tokens_saida": t_out, "custo_usd": round(custo, 6)}


def texto_sem_ia(entrada: dict) -> RaioX:
    """Texto montado por modelo fixo, também com marcadores. Serve para testar sem gastar crédito."""
    def frase(i):
        nome, posicao = INDICADORES[i][1], entrada["indicadores"][i]["posicao"]
        if posicao == "sem dado":
            return f"{nome} sem dado"
        if posicao == "em linha":
            return f"{nome} ({{{i}}}) em linha com o grupo"
        return f"{nome} ({{{i}}}) {posicao} do grupo ({{{i}_grupo}})"
    return RaioX(
        resumo=f"Em {{ano}}, a {{empresa}} tem {frase('receita')}, {frase('cresc_2a')} e {frase('margem_ebit')}.",
        perguntas=[Pergunta(texto=f"Com a {frase('margem_ebit')}, quais custos da operação mais pesam hoje, "
                                  "e onde a solução de {produto} poderia ajudar?", base="margem_ebit"),
                   Pergunta(texto=f"Com o {frase('cresc_2a')}, quais são as prioridades da área para o próximo ano?",
                            base="cresc_2a"),
                   Pergunta(texto="Quem participa da decisão de compra de uma solução como esta?", base="lacuna")],
        lacunas=["Quem decide a compra", "Fornecedor atual", "Orçamento disponível para o próximo ciclo"])


# ------------------------------------------------------------------ validar e preencher
MARCADOR = re.compile(r"\{([a-z0-9_]+)\}")


def checar(texto: str, permitidos: set[str]):
    desconhecidos = [m for m in MARCADOR.findall(texto) if m not in permitidos]
    if desconhecidos:
        return f"marcador desconhecido: {desconhecidos}"
    if re.search(r"\d", MARCADOR.sub("", texto)):
        return "dígito fora de marcador"
    return None


def validar_e_preencher(rx: RaioX, valores: dict) -> dict:
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
        texto = normalizar(p.texto)
        if (motivo := checar(texto, permitidos)) or (p.base not in INDICADORES and p.base != "lacuna"):
            removidos.append({"texto": texto, "motivo": motivo or f"base inválida: {p.base}"})
        else:
            perguntas.append({"texto": preencher(texto), "base": p.base})
    lacunas = []
    for l in rx.lacunas:
        l = normalizar(l)
        if (motivo := checar(l, permitidos)):
            removidos.append({"texto": l, "motivo": motivo})
        else:
            lacunas.append(preencher(l))
    return {"resumo": preencher(resumo), "perguntas": perguntas, "lacunas": lacunas, "removidos": removidos}


# ------------------------------------------------------------------ função do contrato C3
def preparar_raio_x(cd_cvm: int, produto: str, objetivo: str, usar_ia: bool = True) -> dict:
    t0 = time.time()
    entrada, valores, raio_x = montar(_base(), int(cd_cvm), produto, objetivo)
    if usar_ia:
        rx, uso = gerar_llm(entrada, list(valores))
    else:
        rx, uso = texto_sem_ia(entrada), {"tokens_entrada": 0, "tokens_saida": 0, "custo_usd": 0.0}
    raio_x.update(validar_e_preencher(rx, valores))
    raio_x["uso"] = {**uso, "tempo_s": round(time.time() - t0, 1)}
    return raio_x


if __name__ == "__main__":
    a = argparse.ArgumentParser(description="Gera o raio-x de uma empresa (contrato C3).")
    a.add_argument("--cvm", type=int, required=True)
    a.add_argument("--produto", required=True)
    a.add_argument("--objetivo", required=True)
    a.add_argument("--sem-ia", action="store_true", help="texto montado sem IA (não gasta crédito)")
    args = a.parse_args()
    r = preparar_raio_x(args.cvm, args.produto, args.objetivo, usar_ia=not args.sem_ia)
    print(json.dumps(r, ensure_ascii=False, indent=2))
