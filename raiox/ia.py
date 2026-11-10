"""
ia.py · Eduardo · contrato C3 (passo 6 do fluxo)

    preparar_raio_x(cd_cvm, produto, objetivo) -> dict no formato do contrato C3

O LLM escreve o texto usando marcadores como {margem_ebit}; nunca escreve números.
O validador remove qualquer trecho com número fora de marcador (dígito, ½, ² ou por extenso, como "dez por cento"),
e o código troca os marcadores pelos valores da tabela.

Rodar um exemplo (na raiz do repositório):
    python -m raiox.ia --cvm 90001 --produto "software de gestão de frota" --objetivo "primeira conversa com operações"
    python -m raiox.ia --cvm 90001 --produto "..." --objetivo "..." --sem-ia     # texto montado sem IA (não gasta crédito)
"""
import argparse
import json
import re
import sys
import time
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from raiox import fontes, segmentos

ARQ_REGRAS = Path(__file__).resolve().parent.parent / "avaliacao" / "regras_prompt.md"   # da Náthally
MODELO = "gemini-3.1-flash-lite"
PRECO_US_POR_MILHAO = {"entrada": 0.25, "saida": 1.50}  # página oficial de preços do Google, 20/10/2026
# Sem estes limites, a biblioteca espera a resposta sem limite de tempo e faz até 6 tentativas.
# Um raio-x leva uns 2 s (ED7); se a API travar, o erro chega em até uns 30 s e a tela pode cair no modo sem IA.
TEMPO_LIMITE_S = 15
TENTATIVAS = 2      # contando a primeira: o pedido e mais uma tentativa (ex.: erro 429 de limite por minuto)

# id: (nome na tela, nome dentro do texto, tipo de formatação, fonte)
INDICADORES = {
    "receita":        ("Receita líquida", "receita líquida", "dinheiro", "DRE {d} · conta 3.01"),
    "cresc_2a":       ("Crescimento em dois anos", "crescimento em dois anos", "variacao",
                       "DRE {d} · conta 3.01 ({ano} e {ano2})"),
    "margem_ebit":    ("Margem EBIT", "margem EBIT", "pct", "DRE {d} · contas 3.05 ÷ 3.01"),
    "margem_liquida": ("Margem líquida", "margem líquida", "pct", "DRE {d} · contas 3.11 ÷ 3.01"),
    "endividamento":  ("Endividamento", "endividamento", "pct", "balanço {b} · contas 2.03 e 1"),
    "ativo_total":    ("Ativo total", "ativo total", "dinheiro", "balanço {b} · conta 1"),
}
# {d} concorda com "DRE" (consolidada) e {b} com "balanço" (consolidado).
# Os nomes não têm dígitos de propósito: o LLM copia o nome, e o validador derrubaria a frase.
# O "dois" de "crescimento em dois anos" é a exceção: o validador ignora os nomes dos indicadores.


# ------------------------------------------------------------------ dados
def _base() -> pd.DataFrame:
    """A tabela do raio-x, guardada na memória enquanto a fonte não muda (issue #43).
    A chave muda quando a fonte troca (falsos → CVM real) ou o data/indicadores.csv é refeito: sem ela, a tela aberta
    antes de carregar a CVM guardava a tabela falsa até ser reiniciada ("Empresa ... não está na tabela de indicadores")."""
    falsos = segmentos.usando_falsos()
    versao = None if falsos else segmentos.ARQ_INDICADORES.stat().st_mtime_ns   # data e hora em que o arquivo mudou
    return _base_em_cache(falsos, versao)


@lru_cache(maxsize=1)
def _base_em_cache(falsos: bool, versao: int | None) -> pd.DataFrame:
    df, _ = segmentos.carregar_indicadores()
    return segmentos.carregar_segmentos(df)


_base.cache_clear = _base_em_cache.cache_clear   # os testes limpam a memória por aqui (tests/conftest.py)


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
    individual = str(emp.get("origem", "con")) == "ind"
    dre, balanco = ("individual", "individual") if individual else ("consolidada", "consolidado")
    ano = int(emp["ano"])

    indicadores_c3, para_llm = [], {}
    valores = {"empresa": emp["nome"], "setor": emp["setor"], "ano": str(ano), "produto": produto}
    for i, (nome, nome_no_texto, tipo, fonte) in INDICADORES.items():
        v, med = emp[i], do_grupo[i].median()
        if pd.isna(v):
            posicao = "sem dado"
        elif fmt(v, tipo) == fmt(med, tipo) or abs(v - med) <= 0.03 * abs(med):   # diferença pequena
            posicao = "em linha"
        else:
            posicao = "acima" if v > med else "abaixo"
        indicadores_c3.append({
            "id": i, "nome": nome, "valor": fmt(v, tipo), "grupo": fmt(med, tipo), "posicao": posicao,
            "fonte": f"DFP {ano} · " + fonte.format(d=dre, b=balanco, ano=ano, ano2=ano - 2),
            "valor_num": num(v, tipo), "grupo_num": num(med, tipo),
            "unidade": "R$ milhões" if tipo == "dinheiro" else "%"})
        para_llm[i] = {"nome": nome_no_texto, "valor": fmt(v, tipo), "grupo": fmt(med, tipo), "posicao": posicao}
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
    texto: str = Field(description="Pergunta aberta, começando com Como, Quais, O que ou Onde. Sem números; "
                                   "use marcadores.")
    base: str = Field(description="id do indicador que fundamenta a pergunta.")


class RaioX(BaseModel):
    resumo: str = Field(description="Três frases sobre a empresa em relação ao grupo. Sem números; use marcadores.")
    perguntas: list[Pergunta] = Field(description="De 3 a 5 perguntas.")
    lacunas: list[str] = Field(description="De 2 a 4 frases afirmativas curtas, sem ponto de interrogação, "
                                           "sobre o que ainda precisa ser descoberto.")
# As descrições acima também vão para o Gemini (formato da resposta): precisam dizer o mesmo que as regras da Náthally.


# O texto das regras é da Náthally (avaliacao/regras_prompt.md, v2 de 29/10). O prompt lê o arquivo dela, sem cópia,
# para o que ela escreve e o que o Gemini recebe nunca ficarem diferentes. As notas abaixo são do código (Eduardo):
# dizem o que os dados são de verdade. Se ela concordar, elas vão para a v3 dela e saem daqui.
NOTAS_DO_CODIGO = """## Notas do código

- O grupo é formado por empresas com receita, crescimento, margens e endividamento parecidos, não pelo setor. \
Chame-o de "o grupo"; nunca de "o setor", "a média do setor" ou "o mercado".
- Escreva o nome do indicador antes do marcador da empresa, como no exemplo "Certo" acima. \
Nunca use o marcador sozinho no lugar do nome do indicador.
- A lista de marcadores que você pode usar vem na mensagem, junto com a entrada."""

PEDIDO = "Marcadores permitidos: {marcadores}\n\nEntrada:\n{entrada}"


def regras() -> str:
    """O prompt de sistema: as regras da Náthally e as notas do código. Só é lido quando a IA é usada,
    para o modo sem IA (plano B da demo) funcionar mesmo sem o arquivo."""
    return ARQ_REGRAS.read_text(encoding="utf-8").strip() + "\n\n" + NOTAS_DO_CODIGO


def _prompt():
    from langchain_core.messages import SystemMessage
    from langchain_core.prompts import ChatPromptTemplate

    # SystemMessage, e não ("system", texto): no ChatPromptTemplate, {x} é variável, e as regras têm {margem_ebit}.
    # Assim as chaves chegam ao Gemini como estão. Só o PEDIDO tem variáveis: {marcadores} e {entrada}.
    return ChatPromptTemplate.from_messages([SystemMessage(content=regras()), ("human", PEDIDO)])


def _llm():
    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv()
    return ChatGoogleGenerativeAI(model=MODELO, temperature=0.2, timeout=TEMPO_LIMITE_S, max_retries=TENTATIVAS)


@lru_cache(maxsize=1)
def _chain():
    return _prompt() | _llm().with_structured_output(RaioX, include_raw=True)   # include_raw: para ler os tokens


def marcadores_do_llm(valores: dict) -> list[str]:
    """Os marcadores que o Gemini pode usar (regras v2): só {id} e {id_grupo}, e só os que têm valor.
    {empresa}, {setor}, {ano} e {produto} ficam de fora; o validador ainda os aceita, porque o normalizar() os cria."""
    return [m for i in INDICADORES for m in (i, f"{i}_grupo") if valores[m] != "sem dado"]


def gerar_llm(entrada: dict, marcadores: list[str]) -> tuple[RaioX, dict]:
    r = _chain().invoke({"marcadores": ", ".join("{" + m + "}" for m in marcadores),
                         "entrada": json.dumps(entrada, ensure_ascii=False, indent=1)})
    if r.get("parsed") is None:
        # Só o tipo do erro vai para a tela: a mensagem do Pydantic copia o texto do Gemini, com os números dele,
        # e apareceria em "Detalhes técnicos" sem passar pelo validador (revisão de 09/11). O texto inteiro fica no log.
        erro = r.get("parsing_error")
        print(f"Formato inesperado do Gemini: {erro}", file=sys.stderr)
        raise RuntimeError(f"O modelo não devolveu o formato esperado ({type(erro).__name__ if erro else 'vazio'}).")
    uso = getattr(r["raw"], "usage_metadata", None) or {}
    t_in, t_out = uso.get("input_tokens") or 0, uso.get("output_tokens") or 0
    custo = (t_in * PRECO_US_POR_MILHAO["entrada"] + t_out * PRECO_US_POR_MILHAO["saida"]) / 1_000_000
    return r["parsed"], {"tokens_entrada": t_in, "tokens_saida": t_out, "custo_usd": round(custo, 6)}


def texto_sem_ia(entrada: dict) -> RaioX:
    """Texto montado por modelo fixo, também com marcadores e nas mesmas regras do Gemini (v2 da Náthally):
    resumo de três frases, perguntas que começam com Como/Quais/O que/Onde e lacunas afirmativas.
    Serve para testar sem gastar crédito e é o plano B da demo."""
    def sem_dado(i):
        return entrada["indicadores"][i]["posicao"] == "sem dado"

    def frase(i):
        nome, posicao = INDICADORES[i][1], entrada["indicadores"][i]["posicao"]
        if posicao == "sem dado":
            return f"{nome} sem dado"
        if posicao == "em linha":
            return f"{nome} ({{{i}}}) em linha com o grupo"
        return f"{nome} ({{{i}}}) {posicao} do grupo ({{{i}_grupo}})"

    def nome_e_valor(i):   # sem valor, a pergunta cita só o nome (regra v2: nada de pergunta sobre valor que não há)
        return INDICADORES[i][1] if sem_dado(i) else f"{INDICADORES[i][1]} ({{{i}}})"

    return RaioX(
        resumo=(f"Em {{ano}}, a {{empresa}} tem {frase('receita')} e {frase('cresc_2a')}. "
                f"Na rentabilidade, tem {frase('margem_ebit')} e {frase('margem_liquida')}. "
                f"No balanço, tem {frase('endividamento')} e {frase('ativo_total')}."),
        perguntas=[Pergunta(texto=f"Onde a solução de {{produto}} poderia reduzir os custos que pesam na "
                                  f"{nome_e_valor('margem_ebit')}?", base="margem_ebit"),
                   Pergunta(texto=f"Quais são as prioridades da área para o próximo ano, considerando o "
                                  f"{nome_e_valor('cresc_2a')}?", base="cresc_2a"),
                   Pergunta(texto=f"Quais áreas da operação mais usariam a solução de {{produto}}, considerando a "
                                  f"{nome_e_valor('receita')}?", base="receita")],
        lacunas=["Pessoas que decidem a compra", "Fornecedor atual", "Orçamento disponível para o próximo ciclo"])


# ------------------------------------------------------------------ validar e preencher
MARCADOR = re.compile(r"\{([a-z0-9_]+)\}")
# Números por extenso e palavras de quantidade ("o dobro", "metade"), como na regra 1 da Náthally (v1).
# Ficam de fora "um/uma" e os ordinais ("primeira reunião", "segundo o grupo"): aparecem em texto sem número.
POR_EXTENSO = re.compile(
    r"\b(zero|dois|duas|tr[êe]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quatorze|quinze"
    r"|dez[ea]sseis|dez[ea]ssete|dezoito|dez[ea]nove|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa"
    r"|cem|cento|(?:duz|trez|quatroc|quinh|seisc|setec|oitoc|novec)ent[oa]s|mil|milhão|milhões|bilhão|bilhões"
    r"|trilhão|trilhões|dezenas?|centenas?|milhar|milhares|dúzias?|dobro|triplo|metade|terços?|por cento"
    # quantidade em verbo ou fração (issue #50): "a receita dobrou", "triplicou", "um quarto da receita".
    # "quarto" sozinho fica de fora: é ordinal em "quarto trimestre". "duplicata" e "duplicidade" ficam: não são quantidade.
    r"|dobr(?:a|am|e|em|ou|aram|ar|ará|arão|aria|ariam|ando|ad[oa]s?)|duplic(?!at|id)\w*|triplic\w*|quadruplic\w*"
    r"|qu[aá]drupl[oa]s?|um\s+(?:quarto|quinto|sexto|sétimo|oitavo|nono|décimo)|meio\s+(?:ponto|por\s+cento)"
    # revisão de 09/11: "empresa bilionária" e "cresceu uma vez e meia" passavam. "às vezes" e "uma vez que" ficam.
    r"|(?:m|b|tr)ilion\w*|vez(?:es)?\s+e\s+meia)\b",
    re.IGNORECASE)
NOMES_DOS_INDICADORES = re.compile("|".join(re.escape(v[1]) for v in INDICADORES.values()), re.IGNORECASE)


def checar(texto: str, permitidos: set[str]):
    desconhecidos = [m for m in MARCADOR.findall(texto) if m not in permitidos]
    if desconhecidos:
        return f"marcador desconhecido: {desconhecidos}"
    sem_marcadores = MARCADOR.sub("", texto)
    # Categoria N do Unicode: algarismos (também os de outras escritas, como ２) e símbolos como ½, ² e Ⅲ.
    if any(unicodedata.category(c).startswith("N") for c in sem_marcadores):
        return "dígito fora de marcador"
    if (achado := POR_EXTENSO.search(NOMES_DOS_INDICADORES.sub("", sem_marcadores))):
        return f"número por extenso: {achado.group(0)}"
    return None


def tem_letra(nome: str) -> bool:
    """True se o nome tem letra fora de número por extenso: "ERP 360" sim; "10%" e "dez" não."""
    return any(c.isalpha() for c in POR_EXTENSO.sub("", nome))


def validar_e_preencher(rx: RaioX, valores: dict) -> dict:
    permitidos, removidos = set(valores), []

    def preencher(t: str) -> str:
        return MARCADOR.sub(lambda m: valores[m.group(1)], t)

    def normalizar(t: str) -> str:
        # Se o LLM escreveu o nome da empresa, o produto ou o setor por extenso, volta para o marcador.
        # Assim um nome com dígito (ex.: "3R PETROLEUM") não derruba a frase no validador.
        # Só vale para nome com letra: um produto "10%" faria "margem de 10%" passar escondido como {produto}.
        for chave in ("empresa", "produto", "setor"):
            if valores.get(chave) and tem_letra(valores[chave]):
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
    base = _base()
    entrada, valores, raio_x = montar(base, int(cd_cvm), produto, objetivo)
    versao = base.loc[base["cd_cvm"] == int(cd_cvm)].iloc[0].get("versao")   # a tabela falsa também tem; None se faltar
    fontes.anexar(raio_x["indicadores"], int(cd_cvm), raio_x["ano"], None if pd.isna(versao) else versao,
                  segmentos.usando_falsos())   # campo `conferir` do C3: vem do banco, nunca do LLM
    if usar_ia:
        rx, uso = gerar_llm(entrada, marcadores_do_llm(valores))
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
