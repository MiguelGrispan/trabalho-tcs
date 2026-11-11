"""
Conferência manual: mostra a receita, o EBIT e o lucro de uma empresa
direto do banco, para comparar com o site de RI dela.
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
# Permite rodar direto com "python scripts/conferir_empresa.py"
sys.path.insert(0, str(ROOT))

from raiox.banco import catalogo_existe, conectar  # noqa: E402


# Função personalizada para mostrar o valor no padrão brasileiro
def formatar_reais(value):
    # 1,234.56 vira 1.234,56
    value = f"{value:,.2f}"
    value = value.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {value}"


def main():
    if not catalogo_existe():
        print("Catálogo não encontrado no PostgreSQL: rode scripts/carregar_dfp.py e scripts/indicadores.py.")
        return

    conn = conectar()
    ano = conn.execute(text("SELECT MAX(ano) FROM contas")).fetchone()[0]

    termo = input("Digite o nome da empresa (ex: VALE, WEG): ").strip()
    # ILIKE ignora maiúsculas e minúsculas ("vale" acha "VALE")
    empresas = pd.read_sql(
        text(
            """
            SELECT DISTINCT cd_cvm, nome
            FROM contas
            WHERE ano = :ano AND nome ILIKE :termo
            LIMIT 10
            """
        ),
        conn,
        params={"ano": ano, "termo": f"%{termo}%"},
    )
    if empresas.empty:
        print("Nenhuma empresa encontrada com esse termo.")
        conn.close()
        return

    print("\nEmpresas encontradas:")
    for cd_cvm, nome in zip(empresas["cd_cvm"], empresas["nome"]):
        print(f"[{cd_cvm}] - {nome}")

    codigo = input("\nDigite o código exato da empresa: ").strip()
    if not codigo.isdigit():
        print("Código CVM inválido.")
        conn.close()
        return

    # No catálogo o código fica sem zeros à esquerda (raiox/limpeza.py)
    codigo = codigo.lstrip("0")
    df = pd.read_sql(
        text(
            """
            SELECT cd_conta, valor
            FROM contas
            WHERE cd_cvm = :cd_cvm
              AND cd_conta IN ('3.01', '3.05', '3.11')
              AND ano = :ano
            ORDER BY cd_conta
            """
        ),
        conn,
        params={"cd_cvm": codigo, "ano": ano},
    )
    conn.close()

    if df.empty:
        print("Nenhum dado encontrado para este código.")
        return

    print(f"\n--- DEMONSTRATIVO {ano} ---")
    for cd_conta, valor in zip(df["cd_conta"], df["valor"]):
        print(f"Conta {cd_conta}: {formatar_reais(valor)}")


if __name__ == "__main__":
    main()
