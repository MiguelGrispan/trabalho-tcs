"""
Tabela FALSA de 30 empresas no formato do contrato C2 (veio da prova_ia.py da semana 1, sem mudanças).
O raiox/segmentos.py usa esta função só se falsos/tabela_falsa.csv não existir.
"""
import numpy as np
import pandas as pd

SEMENTE = 42

# Três perfis inventados, para os grupos terem algo a encontrar.
PERFIS = {
    "grande_estavel":   dict(receita=(9.6, 0.3), cresc=(0.06, 0.04), ebit=(0.14, 0.03), liq=(0.08, 0.02), divida=(0.55, 0.06)),
    "cresce_margem_baixa": dict(receita=(9.2, 0.3), cresc=(0.25, 0.08), ebit=(0.05, 0.02), liq=(0.01, 0.02), divida=(0.70, 0.06)),
    "pequena_endividada": dict(receita=(8.4, 0.3), cresc=(-0.05, 0.06), ebit=(0.08, 0.03), liq=(-0.02, 0.03), divida=(0.82, 0.05)),
}
SETORES = ["Transporte e logística", "Energia elétrica", "Varejo", "Saúde", "Construção", "Alimentos"]
PREFIXOS = ["ALFA", "BETA", "DELTA", "GAMA", "SIGMA", "OMEGA"]   # nomes inventados: 6 × 5 = 30 empresas
SUFIXOS = ["NORTE", "SUL", "LESTE", "OESTE", "CENTRO"]


def tabela_falsa(n_por_perfil: int = 10) -> pd.DataFrame:
    rng = np.random.default_rng(SEMENTE)
    linhas, cd = [], 90001
    for perfil, p in PERFIS.items():
        for i in range(n_por_perfil):
            receita = 10 ** rng.normal(*p["receita"])
            cresc = rng.normal(*p["cresc"])
            ativo = receita * rng.uniform(0.9, 1.8)
            linhas.append(dict(
                cd_cvm=cd, nome=f"{PREFIXOS[len(linhas) % 6]} {SUFIXOS[len(linhas) // 6]} S.A.",
                setor=SETORES[len(linhas) % len(SETORES)], ano=2025,
                receita=receita, receita_2a_antes=receita / (1 + cresc), cresc_2a=cresc,
                margem_ebit=rng.normal(*p["ebit"]), margem_liquida=rng.normal(*p["liq"]),
                ativo_total=ativo, endividamento=float(np.clip(rng.normal(*p["divida"]), 0.05, 0.98)),
                origem="con", versao=1, perfil_real=perfil,  # perfil_real só existe na tabela falsa
            ))
            cd += 1
    df = pd.DataFrame(linhas)
    df.loc[3, "cresc_2a"] = np.nan  # um nulo de propósito, como vai acontecer nos dados reais
    df.loc[3, "receita_2a_antes"] = np.nan
    return df
