"""Fontes dos números (ED17): para cada indicador, as contas do DFP usadas e o link do documento na CVM (campo `conferir`, contrato C3).

Tudo vem do banco (tabela `contas`) e do arquivo de links (C5); o LLM não escreve nada daqui (regra de ouro).
Se o banco está fora do ar, a tabela não existe ou a empresa não tem link, o campo vem vazio e o raio-x sai igual ao da v1.0.1.
Com RAIOX_DADOS=falsos, lê falsos/contas_falsas.csv e não devolve link (os falsos não são documentos da CVM).
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from raiox.banco import conectar

RAIZ = Path(__file__).resolve().parent.parent
ARQ_CONTAS_FALSAS = RAIZ / "falsos" / "contas_falsas.csv"
ARQ_LINKS = RAIZ / "data" / "links_dfp.csv"

# indicador -> contas que entram na fórmula, na ordem; o 2º número é quantos anos antes do exercício (cresc_2a usa ano e ano-2)
# (as mesmas contas de scripts/indicadores.py: 3.01 receita, 3.05 EBIT, 3.11 lucro, 1 ativo, 2.03 patrimônio líquido)
CONTAS_DO_INDICADOR = {
    "receita": [("3.01", 0)],
    "cresc_2a": [("3.01", 0), ("3.01", 2)],
    "margem_ebit": [("3.05", 0), ("3.01", 0)],
    "margem_liquida": [("3.11", 0), ("3.01", 0)],
    "endividamento": [("2.03", 0), ("1", 0)],
    "ativo_total": [("1", 0)],
}


def reais(valor: float) -> str:
    """R$ com pontos de milhar e sem abreviar (R$ 37.158.908.000), para o usuário bater com o DFP."""
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


@lru_cache(maxsize=1)
def _contas_falsas() -> pd.DataFrame:
    return pd.read_csv(ARQ_CONTAS_FALSAS, dtype={"cd_conta": str})


def _contas(cd_cvm: int, ano: int, falsos: bool) -> dict:
    """{(conta, ano): (descrição, valor)} do exercício e de dois anos antes; vazio se não achar ou se o banco falhar."""
    anos = (ano, ano - 2)
    if falsos:
        c = _contas_falsas()
        c = c[(c["cd_cvm"] == cd_cvm) & c["ano"].isin(anos)]
        linhas = zip(c["cd_conta"], c["ano"], c["ds_conta"], c["valor"])
    else:
        consulta = text("SELECT cd_conta, ano, ds_conta, valor FROM contas "
                        "WHERE CAST(cd_cvm AS TEXT) = :cd AND ano IN (:a, :b)")
        try:
            with conectar() as conn:
                linhas = conn.execute(consulta, {"cd": str(cd_cvm), "a": anos[0], "b": anos[1]}).fetchall()
        except SQLAlchemyError:   # banco desligado ou sem a tabela contas: a demo segue sem o campo
            return {}
    return {(str(conta), int(a)): (desc, float(v)) for conta, a, desc, v in linhas if pd.notna(v)}


@lru_cache(maxsize=1)
def _links_csv(versao_do_arquivo: int | None) -> pd.DataFrame:
    if versao_do_arquivo is None:
        return pd.DataFrame(columns=["cd_cvm", "ano", "versao", "link_doc"])
    return pd.read_csv(ARQ_LINKS)


def _link(cd_cvm: int, ano: int, versao, falsos: bool):
    """Link do DFP na CVM (C5): tabela links_dfp; se ela não existir, o data/links_dfp.csv. None se não achar."""
    if falsos or versao is None:
        return None
    chave = {"cd": cd_cvm, "ano": ano, "v": int(versao)}
    try:
        with conectar() as conn:
            achou = conn.execute(text("SELECT link_doc FROM links_dfp "
                                      "WHERE cd_cvm = :cd AND ano = :ano AND versao = :v LIMIT 1"), chave).fetchone()
        return achou[0] if achou else None
    except SQLAlchemyError:
        pass
    versao_do_arquivo = ARQ_LINKS.stat().st_mtime_ns if ARQ_LINKS.exists() else None   # arquivo refeito = memória nova
    t = _links_csv(versao_do_arquivo)
    t = t[(t["cd_cvm"] == cd_cvm) & (t["ano"] == ano) & (t["versao"] == int(versao))]
    return None if t.empty else str(t.iloc[0]["link_doc"])


def anexar(indicadores: list, cd_cvm: int, ano: int, versao, falsos: bool) -> None:
    """Põe `conferir` em cada indicador do C3 (muda a lista no lugar). Nunca levanta erro por falta de dado."""
    contas = _contas(int(cd_cvm), int(ano), falsos)
    link = _link(int(cd_cvm), int(ano), versao, falsos)
    for ind in indicadores:
        linhas = []
        for conta, antes in CONTAS_DO_INDICADOR.get(ind["id"], []):
            achou = contas.get((conta, ano - antes))
            if achou:
                linhas.append({"conta": conta, "descricao": achou[0], "ano": ano - antes, "valor": reais(achou[1])})
        ind["conferir"] = {"contas": linhas, "link": link}
