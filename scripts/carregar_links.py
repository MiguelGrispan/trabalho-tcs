"""
Links dos documentos DFP na CVM (contrato C5, sessão MA7).

Lê o arquivo principal de cada zip anual da CVM (dfp_cia_aberta_AAAA.csv),
que traz o LINK_DOC de cada documento entregue, e grava data/links_dfp.csv
e a tabela links_dfp. Roda à parte do carregar_dfp.py: não altera o
contas.csv nem o indicadores.csv.
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
# Permite rodar direto com "python scripts/carregar_links.py"
sys.path.insert(0, str(ROOT))

from raiox.banco import conectar  # noqa: E402
from raiox.limpeza import ano_do_exercicio  # noqa: E402
from scripts.carregar_dfp import ANOS, BASE_URL, baixar_com_retry  # noqa: E402

DATA_DIR = ROOT / "data"
# Uma linha por documento: é a chave que o raiox/fontes.py procura
CHAVE = ["cd_cvm", "ano", "versao"]


def ler_principal(z, ano_arquivo):
    """Lê o arquivo principal do zip anual: uma linha por documento entregue."""
    return pd.read_csv(
        z.open(f"dfp_cia_aberta_{ano_arquivo}.csv"),
        sep=";",
        encoding="latin-1",
        usecols=["CD_CVM", "DT_REFER", "VERSAO", "ID_DOC", "LINK_DOC"],
    )


def montar_links(documentos):
    """Transforma os documentos da CVM na tabela do contrato C5."""
    links = pd.DataFrame({
        "cd_cvm": documentos["CD_CVM"].astype(int),
        # Ano do exercício, o mesmo do contas.csv, e não o ano do calendário:
        # o DFP da Camil com fim em fev./2026 é o exercício de 2025
        "ano": ano_do_exercicio(documentos["DT_REFER"]).astype(int),
        "versao": documentos["VERSAO"].astype(int),
        "id_doc": documentos["ID_DOC"].astype(int),
        "link_doc": documentos["LINK_DOC"].str.replace(r"^http://", "https://", regex=True),
    })

    # Documento sem link fica de fora: a tela mostra "sem link", nunca um link quebrado
    links = links.dropna(subset=["link_doc"])

    # O primeiro arquivo traz o exercício anterior de quem fecha fora de
    # dezembro: fica só com os exercícios usados no contas.csv
    links = links[links["ano"].isin(ANOS)]

    # Duas empresas (CD_CVM 26239 e 26824) têm dois documentos para a mesma
    # chave. O ID_DOC cresce com a data de entrega: fica o mais recente
    links = links.sort_values("id_doc").drop_duplicates(CHAVE, keep="last")

    return links.sort_values(CHAVE, ignore_index=True)


def sem_link(links, indicadores):
    """Empresas da tabela de indicadores cujo documento não tem link."""
    junto = indicadores.merge(links[CHAVE], on=CHAVE, how="left", indicator=True)
    return junto.loc[junto["_merge"] == "left_only", ["cd_cvm", "nome", "ano", "versao"]]


def main():
    partes = []
    # Um arquivo a mais que os exercícios: o exercício de 2025 de quem fecha
    # fora de dezembro (ex.: Camil) está no arquivo da CVM de 2026
    for ano_arquivo in ANOS + [ANOS[-1] + 1]:
        print(f"Baixando dados do ano {ano_arquivo}...")
        url = f"{BASE_URL}/DOC/DFP/DADOS/dfp_cia_aberta_{ano_arquivo}.zip"
        try:
            conteudo = baixar_com_retry(url)
        except requests.exceptions.HTTPError as erro:
            # Mesma regra do carregar_dfp.py: só o arquivo a mais pode faltar (404)
            nao_existe = erro.response is not None and erro.response.status_code == 404
            if ano_arquivo in ANOS or not nao_existe:
                raise
            print(f"Aviso: a CVM ainda não tem o arquivo de {ano_arquivo}; seguindo sem ele.")
            continue
        with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
            partes.append(ler_principal(z, ano_arquivo))

    links = montar_links(pd.concat(partes, ignore_index=True))

    # CSV padrão do contrato C5 (vírgula, UTF-8, cabeçalho)
    DATA_DIR.mkdir(exist_ok=True)
    links.to_csv(DATA_DIR / "links_dfp.csv", index=False)
    print(f"Arquivo links_dfp.csv salvo com {len(links)} linhas.")

    conn = conectar()
    links.to_sql("links_dfp", conn, if_exists="replace", index=False)
    # Índice único: o banco recusa dois links para o mesmo documento
    conn.execute(
        text("CREATE UNIQUE INDEX IF NOT EXISTS idx_links_dfp_chave ON links_dfp(cd_cvm, ano, versao);")
    )
    conn.commit()
    conn.close()
    print("Tabela links_dfp atualizada no PostgreSQL.")

    # Confere empresa por empresa: o documento que a tela vai pedir tem link?
    arquivo_indicadores = DATA_DIR / "indicadores.csv"
    if arquivo_indicadores.exists():
        indicadores = pd.read_csv(arquivo_indicadores)
        faltam = sem_link(links, indicadores)
        print(f"Cobertura: {len(indicadores) - len(faltam)} de {len(indicadores)} empresas com link.")
        if not faltam.empty:
            print(f"Empresas sem link:\n{faltam.to_string(index=False)}")


if __name__ == "__main__":
    main()
