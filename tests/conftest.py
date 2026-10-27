"""
Configuração comum dos testes (pytest lê este arquivo sozinho).

Todo teste roda com a tabela falsa (RAIOX_DADOS=falsos), mesmo quando data/indicadores.csv real existe.
Assim o resultado não depende de quem já baixou os dados, e nenhum teste grava em data/.
O teste de ponta a ponta (tests/test_ponta_a_ponta.py) troca para os dados reais por conta própria.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from raiox import ia  # noqa: E402


@pytest.fixture(autouse=True)
def dados_falsos(monkeypatch):
    monkeypatch.setenv("RAIOX_DADOS", "falsos")
    ia._base.cache_clear()          # a tabela fica guardada na memória: limpa para cada teste começar do zero
    yield
    ia._base.cache_clear()
