"""raiox/banco.py: de onde vem o endereço do PostgreSQL (não precisa de banco ligado)."""
import importlib

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
