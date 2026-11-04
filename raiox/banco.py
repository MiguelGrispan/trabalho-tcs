"""Conexão com o banco PostgreSQL do catálogo (usada por todos os scripts)."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import NullPool

# Endereço do banco: postgresql://usuario:senha@servidor:porta/nome_do_banco
# Cada um coloca a própria senha no .env (DATABASE_URL), como a chave do Gemini.
# load_dotenv não troca uma variável que já existe no terminal.
load_dotenv()
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/raiox"
)
# Banco desligado: desiste em poucos segundos. Sem isso o psycopg espera 130 s,
# e no Windows a tela ficava parada esse tempo todo antes de mostrar o aviso
TEMPO_LIMITE_S = 5


def conectar():
    """Abre uma conexão com o catálogo."""
    # NullPool: quando o script chama conn.close(), a conexão fecha de verdade
    engine = create_engine(
        DATABASE_URL, poolclass=NullPool, connect_args={"connect_timeout": TEMPO_LIMITE_S}
    )
    return engine.connect()


def catalogo_existe():
    """Diz se o carregar_dfp.py e o indicadores.py já criaram as tabelas contas e indicadores."""
    engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": TEMPO_LIMITE_S})
    tabelas = inspect(engine)
    existe = tabelas.has_table("contas") and tabelas.has_table("indicadores")
    engine.dispose()
    return existe
