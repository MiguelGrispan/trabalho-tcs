"""
Passo 1 do projeto: baixar e limpar os dados da CVM.

Baixa as DFP de 2023 a 2025 e o cadastro de empresas, aplica as regras
de limpeza de raiox/limpeza.py e salva tudo em data/contas.csv e no
banco PostgreSQL (endereço em raiox/banco.py).
"""
import io
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
# Permite rodar direto com "python scripts/carregar_dfp.py"
sys.path.insert(0, str(ROOT))

from raiox.banco import conectar  # noqa: E402
from raiox.limpeza import (  # noqa: E402
    CHAVES_CONTA,
    COLUNAS_CONTA,
    corrigir_escala,
    encontrar_conflitos,
    encontrar_escala_errada,
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

    # Se o arquivo não está no zip, devolve uma tabela vazia
    if nome_arquivo not in z.namelist():
        return pd.DataFrame(columns=COLUNAS_CONTA)

    # Regra 1: ler com sep=";", encoding="latin-1", decimal="," e CD_CONTA como texto
    df = pd.read_csv(
        z.open(nome_arquivo),
        sep=";",
        encoding="latin-1",
        decimal=",",
        dtype={"CD_CVM": str, "CD_CONTA": str, "ESCALA_MOEDA": str},
    )
    return limpar_demo(df, demo, origem, ano)


def baixar_com_retry(url):
    """Baixa o arquivo. Se a internet cair, tenta de novo (até 3 vezes)."""
    for tentativa in range(3):
        try:
            resposta = requests.get(url, timeout=300)
            resposta.raise_for_status()
            return resposta.content
        except requests.exceptions.RequestException:
            # Na terceira falha desiste e mostra o erro
            if tentativa == 2:
                raise
            time.sleep(2)


def main():
    print("Iniciando o download e processamento...")

    # Cadastro da CVM: vira a tabela empresas e dá o setor de cada empresa
    url_cadastro = f"{BASE_URL}/CAD/DADOS/cad_cia_aberta.csv"
    cadastro = pd.read_csv(
        io.BytesIO(baixar_com_retry(url_cadastro)), sep=";", encoding="latin-1", dtype=str
    )
    print(f"Colunas do cadastro: {', '.join(cadastro.columns)}")
    empresas = preparar_empresas(cadastro)

    # Baixa um zip por ano e lê cada demonstração (DRE, BPA, BPP) con e ind
    partes = []
    for ano in ANOS:
        print(f"Baixando dados do ano {ano}...")
        url = f"{BASE_URL}/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
        z = zipfile.ZipFile(io.BytesIO(baixar_com_retry(url)))

        for demo in DEMOS:
            for origem in ORIGENS:
                parte = ler_demo(z, demo, origem, ano)
                # Arquivo ausente no zip vem vazio e não entra na junção
                if not parte.empty:
                    partes.append(parte)

    if len(partes) == 0:
        raise ValueError("Nenhuma demonstração DFP foi encontrada nos arquivos baixados.")

    # Junta todos os pedaços numa tabela só
    contas = pd.concat(partes, ignore_index=True)

    # Junção com a tabela empresas para trazer o setor
    contas = contas.merge(empresas[["cd_cvm", "setor"]], on="cd_cvm", how="left")
    contas["setor"] = contas["setor"].fillna("Não Informado")

    # Regra 5: consolidado, ou individual quando não houver consolidado
    contas = preferir_consolidado(contas)

    # Avisa sobre contas repetidas antes de resolver (divergentes ficam vazias)
    conflitos = encontrar_conflitos(contas)
    if not conflitos.empty:
        chaves = conflitos[CHAVES_CONTA].drop_duplicates()
        print(
            f"Aviso: {len(chaves)} contas aparecem repetidas na mesma "
            f"empresa/ano/demonstração; valores divergentes ficam ausentes. "
            f"Exemplos:\n{chaves.head(5).to_string(index=False)}"
        )
    contas = resolver_conflitos(contas)

    # Avisa sobre empresas que mandaram milhares declarados como unidade
    escala_errada = encontrar_escala_errada(contas)
    if len(escala_errada) > 0:
        print(
            f"Aviso: {len(escala_errada)} empresa/ano com receita ~1000× menor "
            f"que no ano anterior; valores multiplicados por 1000: {escala_errada}"
        )
    contas = corrigir_escala(contas, escala_errada)

    # Regra 6: só empresas com receita de venda positiva no último ano
    contas = filtrar_empresas_com_receita(contas)

    # Salva o CSV no formato padrão do contrato C2 (vírgula e ponto decimal),
    # que o pd.read_csv lê sem nenhum parâmetro
    DATA_DIR.mkdir(exist_ok=True)
    contas.to_csv(DATA_DIR / "contas.csv", index=False)
    print(f"Arquivo contas.csv salvo com {len(contas)} linhas.")

    # Salva no banco PostgreSQL: tabelas contas e empresas
    conn = conectar()
    contas.to_sql("contas", conn, if_exists="replace", index=False)
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_cd_cvm ON contas(cd_cvm);"))
    # Índice único: o banco recusa duas linhas para a mesma conta
    conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_contas_chave "
            "ON contas(ano, cd_cvm, demonstracao, cd_conta);"
        )
    )
    empresas.to_sql("empresas", conn, if_exists="replace", index=False)
    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_empresas_cd_cvm ON empresas(cd_cvm);"))
    conn.commit()
    conn.close()

    ativas = (empresas["situacao"] == "ATIVO").sum()
    print(
        f"Banco de dados PostgreSQL atualizado "
        f"(tabela empresas: {len(empresas)} empresas, {ativas} ativas)."
    )


if __name__ == "__main__":
    main()
