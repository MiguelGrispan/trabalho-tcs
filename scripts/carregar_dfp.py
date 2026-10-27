"""
Tutorial: Pipeline de Carga de Dados

Este é o script principal de extração. Ele baixa os dados de três anos,
aplica as regras de limpeza de raiox/limpeza.py para remover a "sujeira"
que vem da CVM, cruza com o cadastro de setores e salva tudo
em um arquivo CSV e em um banco de dados SQLite.
"""
import io
import sqlite3
import sys
import zipfile
import time
from contextlib import closing
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Permite rodar direto com "python scripts/carregar_dfp.py".
    sys.path.insert(0, str(ROOT))

from raiox.limpeza import (  # noqa: E402
    CHAVES_CONTA,
    COLUNAS_CONTA,
    encontrar_conflitos,
    filtrar_empresas_com_receita,
    limpar_demo,
    preferir_consolidado,
    preparar_empresas,
    resolver_conflitos,
)

ANOS = [2023, 2024, 2025]
DEMOS = ["DRE", "BPA", "BPP"]
ORIGENS = ["con", "ind"]
BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA"

DATA_DIR = ROOT / "data"


def ler_demo(z, demo, origem, ano):
    """Lê uma demonstração do ZIP anual da CVM e aplica a limpeza."""
    nome_arquivo = f"dfp_cia_aberta_{demo}_{origem}_{ano}.csv"
    if nome_arquivo not in z.namelist():
        return pd.DataFrame(columns=COLUNAS_CONTA)

    df = pd.read_csv(
        z.open(nome_arquivo),
        sep=";",
        encoding="latin-1",
        decimal=",",
        dtype={"CD_CVM": str, "CD_CONTA": str, "ESCALA_MOEDA": str},
    )
    return limpar_demo(df, demo, origem, ano)


def baixar_com_retry(url, tentativas=3):
    """Caso a internet caia, o script tenta baixar novamente."""
    if tentativas < 1:
        raise ValueError("tentativas deve ser pelo menos 1.")
    for i in range(tentativas):
        try:
            resposta = requests.get(url, timeout=300)
            resposta.raise_for_status()
            return resposta.content
        except requests.exceptions.RequestException:
            if i < tentativas - 1:
                time.sleep(2)
            else:
                raise


def main():
    print("Iniciando o download e processamento...")
    partes = []

    # Baixa o cadastro: vira a tabela empresas e dá o setor de cada empresa
    url_cad = f"{BASE_URL}/CAD/DADOS/cad_cia_aberta.csv"
    cadastro = pd.read_csv(io.BytesIO(baixar_com_retry(url_cad)), sep=";", encoding="latin-1", dtype=str)
    print(f"Colunas do cadastro: {', '.join(cadastro.columns)}")
    empresas = preparar_empresas(cadastro)
    mapa_setor = dict(zip(empresas["cd_cvm"], empresas["setor"]))

    for ano in ANOS:
        print(f"Baixando dados do ano {ano}...")
        url = f"{BASE_URL}/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
        conteudo = baixar_com_retry(url)

        with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
            for demo in DEMOS:
                for origem in ORIGENS:
                    partes.append(ler_demo(z, demo, origem, ano))

    # Pedaços vazios (arquivo ausente no ZIP) transformariam valor em texto no concat.
    partes = [parte for parte in partes if not parte.empty]
    if not partes:
        raise ValueError("Nenhuma demonstração DFP foi encontrada nos arquivos baixados.")
    contas = pd.concat(partes, ignore_index=True)

    # Adiciona o setor
    contas["setor"] = contas["cd_cvm"].map(mapa_setor).fillna("Não Informado")

    contas = preferir_consolidado(contas)

    # Avisa sobre contas repetidas antes de resolver (divergentes ficam ausentes)
    conflitos = encontrar_conflitos(contas)
    if not conflitos.empty:
        chaves = conflitos[CHAVES_CONTA].drop_duplicates()
        print(
            f"Aviso: {len(chaves)} contas aparecem repetidas na mesma "
            f"empresa/ano/demonstração; valores divergentes ficam ausentes. "
            f"Exemplos:\n{chaves.head(5).to_string(index=False)}"
        )
    contas = resolver_conflitos(contas)
    contas = filtrar_empresas_com_receita(contas)

    # Salva os arquivos
    DATA_DIR.mkdir(exist_ok=True)
    caminho_csv = DATA_DIR / "contas.csv"
    contas.to_csv(caminho_csv, sep=";", index=False, encoding="utf-8-sig", decimal=",")
    print(f"Arquivo contas.csv salvo com {len(contas)} linhas.")

    caminho_db = DATA_DIR / "catalogo.db"
    with closing(sqlite3.connect(caminho_db)) as conn:
        with conn:
            contas.to_sql("contas", conn, if_exists="replace", index=False)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cd_cvm ON contas(cd_cvm);")
            # Garante a regra de raiox/limpeza.py: uma linha por conta.
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_contas_chave "
                "ON contas(ano, cd_cvm, demonstracao, cd_conta);"
            )
            empresas.to_sql("empresas", conn, if_exists="replace", index=False)
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_empresas_cd_cvm ON empresas(cd_cvm);"
            )
    ativas = int(empresas["situacao"].str.upper().eq("ATIVO").sum())
    print(
        f"Banco de dados catalogo.db atualizado "
        f"(tabela empresas: {len(empresas)} empresas, {ativas} ativas)."
    )

if __name__ == "__main__":
    main()
