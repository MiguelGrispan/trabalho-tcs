"""Acesso aos dados do catálogo PostgreSQL (contrato C1, usado pela tela do Miguel)."""
import json
from datetime import datetime, timezone

from sqlalchemy import text

from raiox.banco import catalogo_existe, conectar


def buscar_empresas(texto):
    """Busca empresas pelo nome: até 20, ordenadas pelo nome.

    O catálogo já vem limpo de carregar_dfp.py: só tem empresas com receita
    de venda positiva e uma linha por conta, então a conta 3.01 do último
    ano dá uma linha por empresa.
    """
    if not catalogo_existe():
        return []

    # No LIKE do SQL, "%" e "_" são curingas. Coloca uma "\" antes deles
    # para buscar o texto exatamente como foi digitado
    termo = texto.strip()
    termo = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    # ILIKE é o LIKE do PostgreSQL que ignora maiúsculas e minúsculas
    consulta = """
        SELECT cd_cvm, nome, setor
        FROM contas
        WHERE ano = (SELECT MAX(ano) FROM contas)
          AND cd_conta = '3.01'
          AND nome ILIKE :termo ESCAPE '\\'
        ORDER BY LOWER(nome)
        LIMIT 20
    """
    conn = conectar()
    linhas = conn.execute(text(consulta), {"termo": f"%{termo}%"}).fetchall()
    conn.close()

    # Transforma cada linha do banco num dicionário
    empresas = []
    for cd_cvm, nome, setor in linhas:
        empresas.append({"cd_cvm": cd_cvm, "nome": nome, "setor": setor})

    return empresas


def registrar_consulta(registro):
    """Guarda cada consulta na tabela consultas, em formato JSON."""
    texto_json = json.dumps(registro, ensure_ascii=False)
    criado_em = datetime.now(timezone.utc).isoformat()

    conn = conectar()
    # SERIAL: o PostgreSQL numera o id sozinho (1, 2, 3...)
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS consultas (
                id SERIAL PRIMARY KEY,
                criado_em TEXT NOT NULL,
                registro_json TEXT NOT NULL
            )
            """
        )
    )
    conn.execute(
        text("INSERT INTO consultas (criado_em, registro_json) VALUES (:criado_em, :registro_json)"),
        {"criado_em": criado_em, "registro_json": texto_json},
    )
    conn.commit()
    conn.close()
