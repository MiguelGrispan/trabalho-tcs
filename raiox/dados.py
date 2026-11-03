"""Acesso aos dados do catálogo PostgreSQL (contrato C1, usado pela tela do Miguel)."""
import json
from datetime import datetime, timezone

from sqlalchemy import text

from raiox.banco import catalogo_existe, conectar


def buscar_empresas(texto):
    """Busca até 20 companhias ativas com indicadores, ordenadas por nome."""
    # Sem as tabelas contas e indicadores, volta vazia: a tela mostra
    # "O banco está vazio", com os comandos para carregar os dados
    if not catalogo_existe():
        return []

    # No LIKE do SQL, "%" e "_" são curingas. Coloca uma "\" antes deles
    # para buscar o texto exatamente como foi digitado
    termo = texto.strip()
    termo = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    # ILIKE é o LIKE do PostgreSQL que ignora maiúsculas e minúsculas
    consulta = """
        SELECT i.cd_cvm, i.nome, i.setor
        FROM indicadores AS i
        JOIN empresas AS e ON e.cd_cvm = CAST(i.cd_cvm AS TEXT)
        WHERE e.situacao = 'ATIVO'
          AND i.nome ILIKE :termo ESCAPE '\\'
        ORDER BY LOWER(i.nome), i.cd_cvm
        LIMIT 20
    """
    with conectar() as conn:
        linhas = conn.execute(text(consulta), {"termo": f"%{termo}%"}).fetchall()

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
