"""Funções de acesso aos dados usadas pela interface do projeto."""
import sqlite3
from contextlib import closing
from pathlib import Path

from raiox.dados import buscar_empresas, registrar_consulta  # noqa: F401 (reexporta C1)
from raiox.limpeza import codigo_cvm

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "catalogo.db"


def obter_indicadores(cd_cvm: str) -> dict:
    """Calcula os indicadores disponíveis para a empresa no último exercício."""
    if not DB_PATH.exists():
        return {}

    codigo = codigo_cvm(cd_cvm)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        linha_ano = conn.execute("SELECT MAX(ano) FROM contas").fetchone()
        if linha_ano is None or linha_ano[0] is None:
            return {}
        ano = int(linha_ano[0])

        registros = conn.execute(
            """
            SELECT ano, cd_conta, valor
            FROM contas
            WHERE cd_cvm = ?
              AND ano IN (?, ?)
              AND (
                  (demonstracao = 'DRE' AND cd_conta IN ('3.01', '3.05', '3.11'))
                  OR (demonstracao = 'BPA' AND cd_conta = '1')
                  OR (demonstracao = 'BPP' AND cd_conta = '2.03')
              )
            """,
            (codigo, ano, ano - 2),
        ).fetchall()

    # O catálogo já vem limpo de carregar_dfp.py (regras em raiox/limpeza.py):
    # uma linha por conta e só empresas com receita de venda positiva.
    valores = {(exercicio, conta): valor for exercicio, conta, valor in registros}
    if (ano, "3.01") not in valores:
        return {}

    receita = valores.get((ano, "3.01"))
    receita_anterior = valores.get((ano - 2, "3.01"))
    ebit = valores.get((ano, "3.05"))
    lucro = valores.get((ano, "3.11"))
    ativo = valores.get((ano, "1"))
    patrimonio_liquido = valores.get((ano, "2.03"))

    return {
        "receita": receita,
        "cresc_2a": (
            receita / receita_anterior - 1
            if receita is not None and receita_anterior is not None and receita_anterior > 0
            else None
        ),
        "margem_ebit": (
            ebit / receita
            if ebit is not None and receita is not None and receita > 0
            else None
        ),
        "margem_liquida": (
            lucro / receita
            if lucro is not None and receita is not None and receita > 0
            else None
        ),
        "ativo_total": ativo,
        "endividamento": (
            1 - patrimonio_liquido / ativo
            if patrimonio_liquido is not None and ativo is not None and ativo > 0
            else None
        ),
    }
