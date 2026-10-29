"""Banco PostgreSQL separado para os testes (não mexe no catálogo de verdade)."""
import os
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, text

from raiox import banco

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/raiox_teste"
)


def banco_disponivel():
    """Tenta conectar no banco de testes; sem PostgreSQL, os testes são pulados."""
    try:
        engine = create_engine(TEST_DATABASE_URL)
        engine.connect().close()
        engine.dispose()
        return True
    except Exception:
        return False


precisa_do_banco = unittest.skipUnless(
    banco_disponivel(), f"PostgreSQL de testes indisponível ({TEST_DATABASE_URL})"
)


class TesteComBanco(unittest.TestCase):
    """Cada teste começa com o banco de testes vazio e o código apontando para ele."""

    def setUp(self):
        self.engine = create_engine(TEST_DATABASE_URL)
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS contas, empresas, consultas"))

        apontar = patch.object(banco, "DATABASE_URL", TEST_DATABASE_URL)
        apontar.start()
        self.addCleanup(apontar.stop)
        self.addCleanup(self.engine.dispose)
