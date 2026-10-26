"""
Checar e auditar a tabela de indicadores · Marcos (com apoio da IA)

Etapa do fluxo de dados que roda DEPOIS do indicadores.py e ANTES de entregar o indicadores.csv ao Eduardo.

  1. Regras automáticas (código) marcam empresas suspeitas.      → anomalias.csv
     "erro" = bug no código de limpeza (corrija direto). "atenção" = pode ser real ou erro; precisa de olho.
  2. Só as "atenções" vão para o Gemini, com as contas originais. → auditoria_ia.csv
     A IA diz a causa provável e sugere uma ação. ELA NÃO ALTERA NENHUM NÚMERO.
  3. O Marcos lê auditoria_ia.csv e decide o que corrigir no código ou excluir.

Como rodar:
  python checar_indicadores.py indicadores.csv contas.csv            # só as regras (sem IA, sem custo)
  python checar_indicadores.py indicadores.csv contas.csv --com-ia   # regras + auditoria pelo Gemini
  python checar_indicadores.py --teste                               # usa os arquivos falsos com erros de propósito

Formato esperado:
  indicadores.csv = contrato C2 (cd_cvm, nome, setor, ano, receita, receita_2a_antes, cresc_2a,
                    margem_ebit, margem_liquida, ativo_total, endividamento, origem, versao)
  contas.csv      = saída do carregar_dfp.py (cd_cvm, nome, ano, demonstracao, cd_conta, ds_conta, valor)
"""
import json
import sys
import time
from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

MODELO = "gemini-3.1-flash-lite"
MAX_EMPRESAS_IA = 40          # limite de chamadas por rodada (custo e limite da API)
PAUSA_ENTRE_CHAMADAS_S = 1.0

# Limites das regras. São escolhas da equipe: ajuste se fizer sentido e anote o porquê.
MIN_EMPRESAS = 200            # menos que isso, provavelmente a leitura perdeu empresas
RECEITA_MINIMA = 1_000_000    # receita anual abaixo de R$ 1 milhão: suspeita de escala (MIL não convertido)
MARGEM_MIN, MARGEM_MAX = -1.0, 1.0
CRESC_MIN, CRESC_MAX = -0.8, 3.0
ATIVO_SOBRE_RECEITA_MAX = 50  # ativo 50 vezes maior que a receita: holding, banco ou escala trocada


# ------------------------------------------------------------------ 1. regras automáticas
def checar(ind: pd.DataFrame, contas: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[str]]:
    alertas, gerais = [], []

    def marca(linha, regra, gravidade):
        alertas.append({"cd_cvm": linha["cd_cvm"], "nome": linha["nome"], "regra": regra, "gravidade": gravidade})

    if len(ind) < MIN_EMPRESAS:
        gerais.append(f"Só {len(ind)} empresas na tabela (esperado ao menos {MIN_EMPRESAS}). "
                      "Confira se o individual (_ind) foi usado quando falta o consolidado.")
    repetidas = ind[ind.duplicated("cd_cvm", keep=False)]
    for _, l in repetidas.drop_duplicates("cd_cvm").iterrows():
        marca(l, "empresa repetida (mesmo cd_cvm em mais de uma linha)", "erro")

    for _, l in ind.iterrows():
        r = l["receita"]
        if pd.isna(r) or r <= 0:
            marca(l, f"receita vazia, zero ou negativa ({r})", "erro")
        elif r < RECEITA_MINIMA:
            marca(l, f"receita muito pequena (R$ {r:,.0f}): escala MIL não convertida?", "atenção")
        for col in ("margem_ebit", "margem_liquida"):
            v = l[col]
            if pd.notna(v) and not (MARGEM_MIN <= v <= MARGEM_MAX):
                marca(l, f"{col} fora de -100% a +100% ({v:.0%})", "atenção")
        e = l["endividamento"]
        if pd.notna(e) and e > 1:
            marca(l, f"endividamento acima de 100% ({e:.0%}): patrimônio líquido negativo?", "atenção")
        elif pd.notna(e) and e < 0:
            marca(l, f"endividamento negativo ({e:.0%})", "erro")
        c = l["cresc_2a"]
        if pd.notna(c) and not (CRESC_MIN <= c <= CRESC_MAX):
            marca(l, f"crescimento em dois anos fora do esperado ({c:+.0%})", "atenção")
        if pd.notna(r) and r > 0 and pd.notna(l["ativo_total"]) and l["ativo_total"] / r > ATIVO_SOBRE_RECEITA_MAX:
            marca(l, f"ativo {l['ativo_total'] / r:.0f} vezes a receita: banco, holding ou escala?", "atenção")
        if pd.isna(l.get("setor")) or str(l.get("setor")).strip() == "":
            marca(l, "setor vazio", "atenção")
    if contas is not None:  # a conta 3.01 de quem vende produto/serviço se chama "Receita de Venda..."
        rec = contas[(contas["cd_conta"].astype(str) == "3.01") & (contas["cd_cvm"].isin(ind["cd_cvm"]))]
        estranhas = rec[~rec["ds_conta"].str.contains("Venda", case=False, na=False)].drop_duplicates("cd_cvm")
        for _, l in estranhas.iterrows():
            marca(l, f"conta 3.01 não é receita de venda ('{l['ds_conta']}'): banco ou seguradora?", "atenção")
    return pd.DataFrame(alertas, columns=["cd_cvm", "nome", "regra", "gravidade"]), gerais


# ------------------------------------------------------------------ 2. auditoria pela IA
class Auditoria(BaseModel):
    causa_provavel: Literal["erro_de_escala", "banco_ou_seguradora", "holding_ou_sem_operacao",
                            "patrimonio_negativo", "valor_plausivel", "dado_faltando", "outro"]
    acao_sugerida: Literal["excluir_da_base", "corrigir_no_codigo", "conferir_no_site_de_RI", "manter"]
    confianca: Literal["baixa", "media", "alta"]
    explicacao: str = Field(description="No máximo 2 frases. Cite só números que aparecem na entrada.")


REGRAS_AUDITOR = """Você audita uma base de indicadores financeiros calculados por código a partir das
demonstrações financeiras entregues à CVM. Uma regra automática marcou esta empresa como suspeita.
Diga a causa mais provável e sugira uma ação. Regras:
1. Não corrija nem recalcule valores. Não invente números: cite só os que aparecem na entrada.
2. Bancos e seguradoras costumam ter a conta 3.01 com nome de receita da intermediação financeira ou de prêmios.
3. Erro de escala aparece como valores mil vezes menores ou maiores que o esperado para o porte da empresa.
4. Patrimônio líquido negativo faz o endividamento passar de 100%; isso pode ser real.
5. Holdings podem ter receita quase zero e lucro vindo de participações em outras empresas.
6. Se a entrada não permitir concluir, use causa 'outro' e confiança 'baixa'."""

PEDIDO_AUDITOR = "Alertas:\n{alertas}\n\nIndicadores calculados:\n{indicadores}\n\nContas originais (principais):\n{contas}"


def contas_principais(contas: pd.DataFrame | None, cd: int) -> str:
    if contas is None:
        return "(contas.csv não fornecido)"
    c = contas[contas["cd_cvm"] == cd].copy()
    c = c[c["cd_conta"].astype(str).str.count(r"\.") <= 1]          # só os dois primeiros níveis (1, 1.01, 3.05...)
    if c.empty:
        return "(sem linhas)"
    return c[["ano", "demonstracao", "cd_conta", "ds_conta", "valor"]].head(60).to_string(
        index=False, float_format=lambda x: f"{x:,.0f}")


def auditar(ind, alertas, contas, chamar=None) -> pd.DataFrame:
    if chamar is None:
        from dotenv import load_dotenv
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
        load_dotenv()
        prompt = ChatPromptTemplate.from_messages([("system", REGRAS_AUDITOR), ("human", PEDIDO_AUDITOR)])
        chain = prompt | ChatGoogleGenerativeAI(model=MODELO, temperature=0).with_structured_output(Auditoria, include_raw=True)

        def chamar(variaveis):
            r = chain.invoke(variaveis)
            uso = getattr(r["raw"], "usage_metadata", None) or {}
            return r["parsed"], uso.get("input_tokens"), uso.get("output_tokens")

    # "erro" (repetida, receita zero...) é bug do código: corrige direto. A IA só ajuda a entender as "atenções".
    suspeitas = alertas.loc[alertas["gravidade"] == "atenção", "cd_cvm"].drop_duplicates().tolist()
    if len(suspeitas) > MAX_EMPRESAS_IA:
        print(f"{len(suspeitas)} empresas suspeitas; a IA vai olhar só as {MAX_EMPRESAS_IA} primeiras.")
        suspeitas = suspeitas[:MAX_EMPRESAS_IA]
    linhas = []
    for n, cd in enumerate(suspeitas, 1):
        emp = ind[ind["cd_cvm"] == cd].iloc[0]
        regras = alertas[alertas["cd_cvm"] == cd]["regra"].tolist()
        variaveis = {"alertas": "\n".join(f"- {r}" for r in regras),
                     "indicadores": json.dumps(emp.drop(labels=["perfil_real"], errors="ignore").to_dict(),
                                               ensure_ascii=False, default=str, indent=1),
                     "contas": contas_principais(contas, cd)}
        try:
            a, t_in, t_out = chamar(variaveis)
            linhas.append({"cd_cvm": cd, "nome": emp["nome"], "alertas": " | ".join(regras),
                           "causa_provavel": a.causa_provavel, "acao_sugerida": a.acao_sugerida,
                           "confianca": a.confianca, "explicacao": a.explicacao,
                           "tokens_entrada": t_in, "tokens_saida": t_out})
        except Exception as erro:  # API fora, limite, resposta inválida: registra e segue
            linhas.append({"cd_cvm": cd, "nome": emp["nome"], "alertas": " | ".join(regras),
                           "causa_provavel": "erro_na_chamada", "acao_sugerida": "conferir_no_site_de_RI",
                           "confianca": "baixa", "explicacao": str(erro)[:200],
                           "tokens_entrada": None, "tokens_saida": None})
        print(f"  [{n}/{len(suspeitas)}] {emp['nome']}: {linhas[-1]['causa_provavel']} → {linhas[-1]['acao_sugerida']}")
        time.sleep(PAUSA_ENTRE_CHAMADAS_S)
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ rodar
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    com_ia = "--com-ia" in sys.argv
    if "--teste" in sys.argv:
        pasta = Path(__file__).parent / "falsos"
        args = [str(pasta / "indicadores_com_erros.csv"), str(pasta / "contas_falsas.csv")]
    if not args:
        print(__doc__)
        sys.exit(1)

    ind = pd.read_csv(args[0])
    contas = pd.read_csv(args[1], dtype={"cd_conta": str}) if len(args) > 1 else None

    alertas, gerais = checar(ind, contas)
    alertas.to_csv("anomalias.csv", index=False)
    print("=" * 70)
    for g in gerais:
        print("AVISO GERAL:", g)
    print(f"{len(ind)} empresas · {alertas['cd_cvm'].nunique()} suspeitas · "
          f"{(alertas['gravidade'] == 'erro').sum()} erros e {(alertas['gravidade'] == 'atenção').sum()} atenções")
    print(alertas.to_string(index=False) if len(alertas) else "Nenhuma anomalia pelas regras.")
    print("Salvo em anomalias.csv")

    if com_ia and len(alertas):
        print("=" * 70, "\nAuditoria pela IA (só lê e sugere; não altera números):")
        aud = auditar(ind, alertas, contas)
        aud.to_csv("auditoria_ia.csv", index=False)
        print("Salvo em auditoria_ia.csv. Próximo passo: ler cada linha e decidir o que fazer.")
