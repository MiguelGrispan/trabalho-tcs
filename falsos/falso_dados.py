"""
Falso do contrato C1 (dados.py do Marcos). Mesmas funções, dados inventados.
Quando o dados.py real existir, a tela troca este arquivo por ele sem mudar mais nada.
"""
from falsos.dados_exemplo import DADOS


def buscar_empresas(texto: str) -> list[dict]:
    """Só companhias ativas e com indicadores, ordenadas por nome."""
    t = texto.strip().upper()
    achadas = [{"cd_cvm": cd, "nome": d["empresa"], "setor": d["setor"]}
               for cd, d in DADOS.items() if t in d["empresa"]]
    return sorted(achadas, key=lambda e: e["nome"])


def registrar_consulta(registro: dict) -> None:
    """No real, grava uma linha na tabela consultas do catalogo.db. Aqui só mostra no terminal."""
    print("[consulta registrada]", registro)
