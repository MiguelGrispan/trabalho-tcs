"""
Falso do contrato C3 (ia.py do Eduardo). Mesma função, mesmo formato de resposta.
O texto aqui é montado por um modelo fixo (sem IA), só para a tela ter algo realista para mostrar.
"""
import copy
import time

from falsos.dados_exemplo import DADOS

NOME_NO_TEXTO = {"receita": "receita líquida", "cresc_2a": "crescimento em dois anos", "margem_ebit": "margem EBIT",
                 "margem_liquida": "margem líquida", "endividamento": "endividamento", "ativo_total": "ativo total"}


def _frase(i: dict) -> str:
    nome = NOME_NO_TEXTO[i["id"]]
    if i["posicao"] == "em linha":
        return f"{nome} ({i['valor']}) em linha com o grupo"
    if i["posicao"] == "sem dado":
        return f"{nome} sem dado"
    return f"{nome} ({i['valor']}) {i['posicao']} do grupo ({i['grupo']})"


def preparar_raio_x(cd_cvm: int, produto: str, objetivo: str) -> dict:
    time.sleep(1.2)  # simula o tempo da chamada à IA
    rx = copy.deepcopy(DADOS[cd_cvm])
    ind = {i["id"]: i for i in rx["indicadores"]}
    rx["resumo"] = (f"Em {rx['ano']}, a {rx['empresa']} tem {_frase(ind['receita'])}, "
                    f"{_frase(ind['cresc_2a'])} e {_frase(ind['margem_ebit'])}.")
    rx["perguntas"] = [
        {"texto": f"Com a {_frase(ind['margem_ebit'])}, quais custos da operação mais pesam hoje, "
                  f"e onde a solução de {produto} poderia ajudar?", "base": "margem_ebit"},
        {"texto": f"Com o {_frase(ind['cresc_2a'])}, quais são as prioridades da área para o próximo ano?",
         "base": "cresc_2a"},
        {"texto": "Quem participa da decisão de compra de uma solução como esta?", "base": "lacuna"},
    ]
    rx["lacunas"] = ["Quem decide a compra", "Fornecedor atual", "Orçamento disponível para o próximo ciclo"]
    rx["removidos"] = []
    rx["uso"] = {"tokens_entrada": 905, "tokens_saida": 410, "custo_usd": 0.0008, "tempo_s": 1.2}
    return rx
