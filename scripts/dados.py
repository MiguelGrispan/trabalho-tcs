"""Funções de acesso aos dados usadas pela interface do projeto."""
from sqlalchemy import text

from raiox.banco import catalogo_existe, conectar
from raiox.dados import buscar_empresas, registrar_consulta  # noqa: F401 (reexporta C1)
from raiox.limpeza import codigo_cvm


def obter_indicadores(cd_cvm):
    """Calcula os indicadores da empresa no último exercício, direto do catálogo."""
    if not catalogo_existe():
        return {}

    codigo = codigo_cvm(cd_cvm)
    conn = conectar()

    ano = conn.execute(text("SELECT MAX(ano) FROM contas")).fetchone()[0]
    if ano is None:
        conn.close()
        return {}

    registros = conn.execute(
        text(
            """
            SELECT ano, cd_conta, valor
            FROM contas
            WHERE cd_cvm = :cd_cvm
              AND ano IN (:ano, :ano_anterior)
              AND (
                  (demonstracao = 'DRE' AND cd_conta IN ('3.01', '3.05', '3.11'))
                  OR (demonstracao = 'BPA' AND cd_conta = '1')
                  OR (demonstracao = 'BPP' AND cd_conta = '2.03')
              )
            """
        ),
        {"cd_cvm": codigo, "ano": ano, "ano_anterior": ano - 2},
    ).fetchall()
    conn.close()

    # Dicionário (ano, conta) -> valor
    valores = {}
    for exercicio, conta, valor in registros:
        valores[(exercicio, conta)] = valor

    # Empresa fora do catálogo
    if (ano, "3.01") not in valores:
        return {}

    receita = valores.get((ano, "3.01"))
    receita_anterior = valores.get((ano - 2, "3.01"))
    ebit = valores.get((ano, "3.05"))
    lucro = valores.get((ano, "3.11"))
    ativo = valores.get((ano, "1"))
    patrimonio_liquido = valores.get((ano, "2.03"))

    # Regra 7: sem dado ou divisão por zero, o indicador fica vazio (None)
    cresc_2a = None
    if receita is not None and receita_anterior is not None and receita_anterior > 0:
        cresc_2a = receita / receita_anterior - 1

    margem_ebit = None
    if ebit is not None and receita is not None and receita > 0:
        margem_ebit = ebit / receita

    margem_liquida = None
    if lucro is not None and receita is not None and receita > 0:
        margem_liquida = lucro / receita

    endividamento = None
    if patrimonio_liquido is not None and ativo is not None and ativo > 0:
        endividamento = 1 - patrimonio_liquido / ativo

    return {
        "receita": receita,
        "cresc_2a": cresc_2a,
        "margem_ebit": margem_ebit,
        "margem_liquida": margem_liquida,
        "ativo_total": ativo,
        "endividamento": endividamento,
    }
