"""Conexão com o banco PostgreSQL do catálogo (usada por todos os scripts)."""
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool

# Endereço do banco: postgresql://usuario:senha@servidor:porta/nome_do_banco
# Cada um coloca a própria senha na variável de ambiente DATABASE_URL
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/raiox"
)


def conectar():
    """Abre uma conexão com o catálogo."""
    # NullPool: quando o script chama conn.close(), a conexão fecha de verdade
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
    return engine.connect()


def catalogo_existe():
    """Diz se o carregar_dfp.py já criou a tabela contas no banco."""
    engine = create_engine(DATABASE_URL)
    existe = inspect(engine).has_table("contas")
    engine.dispose()
    return existe
