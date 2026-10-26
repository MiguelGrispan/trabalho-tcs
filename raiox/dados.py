"""Acesso aos dados do catálogo SQLite."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "catalogo.db"


def conectar() -> sqlite3.Connection:
    """Abre uma conexão com o catálogo."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def buscar_empresas(texto: str) -> list[dict[str, Any]]:
    """Busca empresas com receita de venda positiva no exercício mais recente."""
    if not DB_PATH.exists():
        return []

    termo = texto.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    consulta = """
        SELECT c.cd_cvm, c.nome, c.setor
        FROM contas AS c
        WHERE c.ano = (SELECT MAX(ano) FROM contas)
          AND c.cd_conta = '3.01'
          AND c.valor > 0
          AND c.ds_conta LIKE '%receita de venda%' COLLATE NOCASE
          AND c.nome LIKE ? ESCAPE '\\'
        GROUP BY c.cd_cvm, c.nome, c.setor
        ORDER BY c.nome COLLATE NOCASE
        LIMIT 20
    """
    with closing(conectar()) as conn:
        rows = conn.execute(consulta, (f"%{termo}%",)).fetchall()

    return [
        {
            "cd_cvm": str(codigo).strip().lstrip("0") or "0",
            "nome": str(nome),
            "setor": str(setor) if setor is not None else "Não Informado",
        }
        for codigo, nome, setor in rows
    ]


def registrar_consulta(registro: dict[str, Any]) -> None:
    """Persiste o registro de consulta em formato JSON."""
    if not isinstance(registro, dict):
        raise TypeError("registro deve ser um dicionário.")

    payload = json.dumps(registro, ensure_ascii=False, allow_nan=False)
    criado_em = datetime.now(timezone.utc).isoformat()
    with closing(conectar()) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consultas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    criado_em TEXT NOT NULL,
                    registro_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT INTO consultas (criado_em, registro_json) VALUES (?, ?)",
                (criado_em, payload),
            )
