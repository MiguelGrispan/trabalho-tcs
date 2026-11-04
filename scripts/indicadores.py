"""
Passo 2 do projeto: calcular os 6 indicadores.

Lê data/contas.csv (já limpo por carregar_dfp.py) e gera
data/indicadores.csv no formato do contrato C2: uma linha por empresa,
com os indicadores do último ano. A execução do script publica a mesma
tabela no PostgreSQL para a busca da aplicação.
"""
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from raiox.banco import conectar  # noqa: E402

DATA_DIR = ROOT / "data"

COLUNAS_SAIDA = [
    "cd_cvm", "nome", "setor", "ano", "receita", "receita_2a_antes",
    "cresc_2a", "margem_ebit", "margem_liquida", "ativo_total",
    "endividamento", "origem", "versao",
]
# Contas usadas nos indicadores: código da conta -> nome da coluna
CONTAS = {"3.01": "receita", "3.05": "ebit", "3.11": "lucro", "1": "ativo", "2.03": "pl"}


def _ler_e_calcular():
    """Calcula o C2 a partir das contas locais."""
    df = pd.read_csv(
        DATA_DIR / "contas.csv",
        dtype={"cd_cvm": str, "cd_conta": str},
    )

    df["cd_conta"] = df["cd_conta"].astype("string").str.strip()
    df["ano"] = pd.to_numeric(df["ano"], errors="raise").astype(int)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    # contas.csv já vem limpo de carregar_dfp.py (regras em raiox/limpeza.py):
    # uma linha por conta e só empresas com receita de venda positiva.
    # Fica só com as contas usadas nos indicadores
    df = df[df["cd_conta"].isin(list(CONTAS))]

    resultado = montar_indicadores(df)
    # Contrato C2: cd_cvm é número inteiro e o CSV é o padrão
    # (vírgula e ponto decimal), que o pd.read_csv lê sem nenhum parâmetro
    resultado["cd_cvm"] = resultado["cd_cvm"].astype(int)
    return resultado


def montar_indicadores(df):
    """Uma linha por empresa no ano mais recente, com os indicadores do C2."""
    # Uma linha por empresa e ano, uma coluna por conta.
    # pivot (e não pivot_table): se houver conta repetida ele dá erro
    # em vez de escolher um dos valores
    tabela = df.pivot(index=["ano", "cd_cvm", "nome"], columns="cd_conta", values="valor")
    tabela = tabela.rename(columns=CONTAS)
    tabela = tabela.reset_index()

    # Garante que todas as contas viram coluna, mesmo se faltarem nos dados
    for nome_coluna in CONTAS.values():
        if nome_coluna not in tabela.columns:
            tabela[nome_coluna] = None

    ano_atual = tabela["ano"].max()
    base = tabela[tabela["ano"] == ano_atual]

    # Junta a receita de 2 anos antes (regra 7: se faltar, fica vazia)
    receita_antes = tabela[tabela["ano"] == ano_atual - 2]
    receita_antes = receita_antes[["cd_cvm", "receita"]]
    receita_antes = receita_antes.rename(columns={"receita": "receita_2a_antes"})
    base = base.merge(receita_antes, on="cd_cvm", how="left")

    # Fórmulas da página "Os 6 indicadores"
    base["cresc_2a"] = base["receita"] / base["receita_2a_antes"] - 1
    base["margem_ebit"] = base["ebit"] / base["receita"]
    base["margem_liquida"] = base["lucro"] / base["receita"]
    base["ativo_total"] = base["ativo"]
    base["endividamento"] = 1 - base["pl"] / base["ativo"]

    # Regra 7: dividir por zero ou por valor negativo não vale;
    # o indicador fica vazio em vez de virar infinito
    base.loc[base["receita_2a_antes"] <= 0, "cresc_2a"] = None
    base.loc[base["receita"] <= 0, "margem_ebit"] = None
    base.loc[base["receita"] <= 0, "margem_liquida"] = None
    base.loc[base["ativo"] <= 0, "endividamento"] = None

    # Setor, origem (con/ind) e versão vêm da linha da receita no último ano
    receita = df[
        (df["demonstracao"] == "DRE")
        & (df["ano"] == ano_atual)
        & (df["cd_conta"] == "3.01")
    ]
    receita = receita[["cd_cvm", "setor", "origem", "versao"]]
    receita = receita.drop_duplicates(subset="cd_cvm")
    base = base.merge(receita, on="cd_cvm", how="left")
    base["setor"] = base["setor"].fillna("Não Informado")

    # Colunas na ordem do contrato C2
    base = base[COLUNAS_SAIDA]
    return base.sort_values("nome")


def calcular():
    """Gera o CSV para os consumidores que usam apenas o arquivo."""
    resultado = _ler_e_calcular()
    resultado.to_csv(DATA_DIR / "indicadores.csv", index=False)
    return resultado


def publicar():
    resultado = _ler_e_calcular()
    # Só troca o CSV depois de gravar a tabela com sucesso.
    with NamedTemporaryFile(dir=DATA_DIR, delete=False) as arquivo:
        temporario = Path(arquivo.name)
    try:
        resultado.to_csv(temporario, index=False)
        with conectar() as conn, conn.begin():
            resultado.to_sql("indicadores", conn, if_exists="replace", index=False)
            conn.execute(text("ALTER TABLE indicadores ADD PRIMARY KEY (cd_cvm)"))
        # O temporário nasce só para o dono (0600); a tela no Docker roda com
        # outro usuário e precisa ler o CSV (issue #48)
        temporario.chmod(0o644)
        temporario.replace(DATA_DIR / "indicadores.csv")
    finally:
        temporario.unlink(missing_ok=True)


if __name__ == "__main__":
    publicar()
