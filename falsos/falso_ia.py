"""
Falso do contrato C3: usa o raiox/ia.py de verdade, com o texto montado sem IA.
Mesma resposta no mesmo formato, sem chamar o Gemini (não gasta crédito).
"""
from raiox.ia import preparar_raio_x as _preparar_raio_x


def preparar_raio_x(cd_cvm: int, produto: str, objetivo: str) -> dict:
    return _preparar_raio_x(cd_cvm, produto, objetivo, usar_ia=False)
