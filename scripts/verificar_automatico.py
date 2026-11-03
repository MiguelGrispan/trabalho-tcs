"""Compara a receita, o EBIT e o lucro da CVM com os do Yahoo Finance."""
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
# Permite rodar direto com "python scripts/verificar_automatico.py"
sys.path.insert(0, str(ROOT))

from raiox.banco import catalogo_existe, conectar  # noqa: E402

CONFERENCIA_CSV = ROOT / "data" / "conferencia_s1.csv"
TOLERANCIA_PCT = 10
MOEDA_CVM = "BRL"

# Ticker -> código CVM (sem zeros à esquerda, como no catálogo)
EMPRESAS = {
    "VALE3.SA": "4170",
    "PETR4.SA": "9512",
    "WEGE3.SA": "5410",
    "MGLU3.SA": "22470",
}
# Conta da CVM -> nome para o relatório
CONTAS = {
    "3.01": "Receita",
    "3.05": "EBIT",
    "3.11": "Lucro líquido",
}
# Conta da CVM -> nome da mesma linha no Yahoo
LINHAS_YAHOO = {
    "3.01": "Total Revenue",
    "3.05": "EBIT",
    "3.11": "Net Income",
}


def buscar_dados_banco(conn, cd_cvm, ano):
    """Busca as contas da DRE da empresa no exercício: {conta: valor}."""
    linhas = conn.execute(
        text(
            """
            SELECT cd_conta, valor
            FROM contas
            WHERE cd_cvm = :cd_cvm
              AND ano = :ano
              AND demonstracao = 'DRE'
              AND cd_conta IN ('3.01', '3.05', '3.11')
            """
        ),
        {"cd_cvm": cd_cvm, "ano": ano},
    ).fetchall()
    return dict(linhas)


def buscar_ano_mais_recente(conn):
    ano = conn.execute(text("SELECT MAX(ano) FROM contas")).fetchone()[0]
    if ano is None:
        raise ValueError("O catálogo não contém dados anuais.")
    return int(ano)


def _valor_financeiro(dre, linha, ano):
    """Pega o valor de uma linha da DRE do Yahoo no ano pedido."""
    if linha not in dre.index:
        return None

    # As colunas do Yahoo são datas (ex.: 2025-12-31); procura a do ano
    for coluna in dre.columns:
        if pd.Timestamp(coluna).year == ano:
            valor = dre.loc[linha, coluna]
            if pd.isna(valor):
                return None
            return float(valor)

    return None


def _classificar(valor_cvm, valor_yahoo, moeda_yahoo):
    """Retorna (diferença em %, resultado)."""
    if valor_cvm is None or valor_yahoo is None:
        return None, "SEM DADO"

    if not moeda_yahoo:
        return None, "MOEDA DESCONHECIDA"

    if moeda_yahoo != MOEDA_CVM:
        return None, "MOEDA DIFERENTE"

    # Não dá para dividir por zero: só é compatível se os dois forem zero
    if valor_yahoo == 0:
        if valor_cvm == 0:
            return 0.0, "COMPATÍVEL"
        return None, "REVISAR"

    diferenca = round(abs(valor_cvm - valor_yahoo) / abs(valor_yahoo) * 100, 2)
    if diferenca <= TOLERANCIA_PCT:
        return diferenca, "COMPATÍVEL"

    return diferenca, "REVISAR"


def validar_empresa(conn, ticker, cd_cvm, ano):
    """Compara as contas do exercício e devolve uma linha por conta."""
    dados_cvm = buscar_dados_banco(conn, cd_cvm, ano)
    if not dados_cvm:
        raise ValueError(f"Sem dados da CVM para {ticker} no exercício {ano}.")

    ativo = yf.Ticker(ticker)
    moeda_yahoo = ativo.get_info().get("financialCurrency")
    dre = ativo.financials

    linhas = []
    for conta, descricao in CONTAS.items():
        valor_cvm = dados_cvm.get(conta)
        valor_yahoo = _valor_financeiro(dre, LINHAS_YAHOO[conta], ano)
        diferenca, resultado = _classificar(valor_cvm, valor_yahoo, moeda_yahoo)
        linhas.append({
            "ticker": ticker,
            "cd_cvm": cd_cvm,
            "exercicio": ano,
            "conta": descricao,
            "valor_cvm_brl": valor_cvm,
            "valor_yahoo": valor_yahoo,
            "moeda_yahoo": moeda_yahoo,
            "diferenca_pct": diferenca,
            "resultado": resultado,
        })

    return linhas


def linhas_com_erro(ticker, cd_cvm, ano):
    """Linhas do relatório para a empresa que não foi possível comparar."""
    linhas = []
    for descricao in CONTAS.values():
        linhas.append({
            "ticker": ticker,
            "cd_cvm": cd_cvm,
            "exercicio": ano,
            "conta": descricao,
            "valor_cvm_brl": None,
            "valor_yahoo": None,
            "moeda_yahoo": None,
            "diferenca_pct": None,
            "resultado": "ERRO",
        })

    return linhas


def main():
    print("Validação anual: CVM x Yahoo Finance")
    if not catalogo_existe():
        raise FileNotFoundError(
            "Tabelas contas e indicadores não encontradas no PostgreSQL. "
            "Execute scripts/carregar_dfp.py e scripts/indicadores.py primeiro."
        )

    conn = conectar()
    ano = buscar_ano_mais_recente(conn)

    resultados = []
    for ticker, cd_cvm in EMPRESAS.items():
        print(f"Verificando {ticker} — exercício {ano}...")
        # Falha de rede no Yahoo ou dado ausente não interrompe as outras empresas
        try:
            resultados.extend(validar_empresa(conn, ticker, cd_cvm, ano))
        except Exception as erro:
            print(f"  Erro em {ticker}: {erro}")
            resultados.extend(linhas_com_erro(ticker, cd_cvm, ano))

    conn.close()

    conferencia = pd.DataFrame(resultados)
    conferencia.to_csv(CONFERENCIA_CSV, index=False, encoding="utf-8-sig")

    print(f"\nTolerância: {TOLERANCIA_PCT}%")
    print(conferencia[["ticker", "conta", "diferenca_pct", "moeda_yahoo", "resultado"]].to_string(index=False))
    print(f"\nRelatório salvo em: {CONFERENCIA_CSV}")


if __name__ == "__main__":
    main()
