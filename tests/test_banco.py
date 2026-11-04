"""raiox/banco.py: de onde vem o endereço do PostgreSQL (não precisa de banco ligado)."""
import importlib
import time

import pytest
from sqlalchemy.exc import OperationalError

from raiox import banco


def test_endereco_do_terminal_vale_mais_que_o_env(monkeypatch):
    # load_dotenv não troca uma variável que já existe, então o .env não atrapalha
    monkeypatch.setenv("DATABASE_URL", "postgresql://alguem:senha@servidor:5432/outro")
    try:
        importlib.reload(banco)
        assert banco.DATABASE_URL == "postgresql://alguem:senha@servidor:5432/outro"
    finally:
        monkeypatch.undo()
        importlib.reload(banco)


def test_desiste_rapido_se_o_banco_nao_responde(monkeypatch):
    # Porta fechada. No Linux a recusa vem na hora; no Windows, sem o limite,
    # o psycopg esperava 130 s e a tela ficava parada antes do aviso
    monkeypatch.setattr(banco, "DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:1/raiox")
    for abrir in (banco.conectar, banco.catalogo_existe):
        inicio = time.monotonic()
        with pytest.raises(OperationalError):
            abrir()
        assert time.monotonic() - inicio < 3 * banco.TEMPO_LIMITE_S
