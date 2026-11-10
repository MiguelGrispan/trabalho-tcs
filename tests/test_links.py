"""Testes do scripts/carregar_links.py (contrato C5): zips pequenos falsos, sem internet."""
import contextlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import requests
from sqlalchemy import text

from raiox import fontes
from scripts import carregar_links
from tests.banco_teste import TesteComBanco, precisa_do_banco

COLUNAS = ["CNPJ_CIA", "DT_REFER", "VERSAO", "DENOM_CIA", "CD_CVM", "CATEG_DOC", "ID_DOC", "DT_RECEB", "LINK_DOC"]
URL = "http://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento="


def documento(cd_cvm, fim, versao, id_doc, link="padrao"):
    """Uma linha do arquivo principal da CVM (o CD_CVM vem com zeros à esquerda)."""
    link = URL + str(id_doc) if link == "padrao" else link
    return ["00.000.000/0001-00", fim, versao, "Empresa", f"{cd_cvm:06d}", "DFP", id_doc, "2026-01-01", link]


def tabela(*linhas):
    return pd.DataFrame(list(linhas), columns=COLUNAS)


def zip_da_cvm(ano, *linhas):
    """Um zip igual ao da CVM: ';', latin-1 e o arquivo principal com o nome do ano."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr(f"dfp_cia_aberta_{ano}.csv", tabela(*linhas).to_csv(index=False, sep=";").encode("latin-1"))
    return buffer.getvalue()


def montar(*linhas):
    return carregar_links.montar_links(tabela(*linhas))


class MontarLinksTests(unittest.TestCase):
    def test_formato_do_contrato_c5(self):
        links = montar(documento(2437, "2025-12-31", 1, 154939))

        self.assertEqual(list(links.columns), ["cd_cvm", "ano", "versao", "id_doc", "link_doc"])
        self.assertEqual(links.iloc[0].to_dict(), {
            "cd_cvm": 2437, "ano": 2025, "versao": 1, "id_doc": 154939,
            "link_doc": "https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx"
                        "?CodigoInstituicao=1&NumeroSequencialDocumento=154939",
        })

    def test_camil_casa_pelo_ano_do_exercicio_e_nao_pelo_calendario(self):
        """O fim em fev./2026 é o exercício de 2025; casar pelo calendário traria o DFP errado."""
        links = montar(
            documento(24228, "2025-02-28", 1, 147180),
            documento(24228, "2026-02-28", 1, 156875),
        )

        self.assertEqual(links.set_index("ano")["id_doc"].to_dict(), {2024: 147180, 2025: 156875})

    def test_fica_so_com_os_exercicios_do_contas_csv(self):
        """Fim em fev./2023 é o exercício de 2022 e fim em dez./2026 ainda não entra na base."""
        links = montar(
            documento(24228, "2023-02-28", 1, 126052),
            documento(24228, "2024-02-28", 1, 136924),
            documento(5410, "2026-12-31", 1, 170000),
        )

        self.assertEqual(links["id_doc"].tolist(), [136924])

    def test_duplicata_fica_com_o_id_doc_mais_recente(self):
        """26239 e 26824 têm dois documentos para a mesma chave; vale o entregue por último."""
        links = montar(
            documento(26239, "2023-12-31", 1, 135670),
            documento(26239, "2023-12-31", 1, 135158),
            documento(26824, "2024-12-31", 1, 146055),
            documento(26824, "2024-12-31", 1, 151243),
        )

        self.assertEqual(links.set_index("cd_cvm")["id_doc"].to_dict(), {26239: 135670, 26824: 151243})

    def test_reapresentacao_nao_e_duplicata(self):
        """Versões diferentes do mesmo exercício ficam as duas: a tela escolhe pela versão."""
        links = montar(
            documento(2437, "2025-12-31", 1, 154939),
            documento(2437, "2025-12-31", 2, 155000),
        )

        self.assertEqual(links["versao"].tolist(), [1, 2])

    def test_documento_sem_link_fica_de_fora(self):
        """Sem isso o CSV teria um vazio e o fontes.py devolveria o texto "nan" como link."""
        links = montar(
            documento(2437, "2025-12-31", 1, 154939, link=None),
            documento(5410, "2025-12-31", 1, 154940),
        )

        self.assertEqual(links["cd_cvm"].tolist(), [5410])


class SemLinkTests(unittest.TestCase):
    def test_lista_so_quem_nao_tem_o_documento_da_tela(self):
        links = montar(
            documento(2437, "2025-12-31", 1, 154939),
            documento(5410, "2025-12-31", 1, 154940),
        )
        indicadores = pd.DataFrame({
            "cd_cvm": [2437, 5410, 24228],
            "nome": ["AXIA", "WEG", "CAMIL"],
            "ano": [2025, 2025, 2025],
            "versao": [1, 2, 1],   # a WEG tem link, mas de outra versão
        })

        faltam = carregar_links.sem_link(links, indicadores)

        self.assertEqual(faltam["nome"].tolist(), ["WEG", "CAMIL"])


@precisa_do_banco
class PipelineLinksTests(TesteComBanco):
    """Roda o main() inteiro com downloads falsos: nada de internet."""

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name)
        self.addCleanup(self.apagar_tabela)
        self.downloads = {
            "dfp_cia_aberta_2025.zip": zip_da_cvm(2025, documento(2437, "2025-12-31", 1, 154939)),
            "dfp_cia_aberta_2026.zip": zip_da_cvm(2026, documento(24228, "2026-02-28", 1, 156875)),
        }

    def apagar_tabela(self):
        """O banco de testes é de todos: outro teste não pode achar esta tabela."""
        with self.engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS links_dfp"))

    def rodar_main(self):
        def baixar_falso(url):
            nome = url.rsplit("/", 1)[-1]
            conteudo = self.downloads.get(nome, 404)  # como a CVM sem o arquivo
            if isinstance(conteudo, int):
                resposta = requests.Response()
                resposta.status_code = conteudo
                raise requests.exceptions.HTTPError(f"{conteudo}: {nome}", response=resposta)
            return conteudo

        saida = io.StringIO()
        with (
            patch.object(carregar_links, "DATA_DIR", self.data_dir),
            patch.object(carregar_links, "ANOS", [2025]),
            patch.object(carregar_links, "baixar_com_retry", side_effect=baixar_falso),
            contextlib.redirect_stdout(saida),
        ):
            carregar_links.main()
        return saida.getvalue()

    def test_main_salva_csv_padrao_e_tabela(self):
        self.rodar_main()

        csv = pd.read_csv(self.data_dir / "links_dfp.csv")
        self.assertEqual(csv.set_index("cd_cvm")["id_doc"].to_dict(), {2437: 154939, 24228: 156875})
        with self.engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM links_dfp")).scalar()
        self.assertEqual(total, 2)

    def test_fontes_acha_o_link_gravado_pelo_main(self):
        """A ponta que importa: o raiox/fontes.py lê esta tabela com cd_cvm inteiro."""
        self.rodar_main()

        link = fontes._link(24228, 2025, 1, falsos=False)

        self.assertTrue(link.endswith("NumeroSequencialDocumento=156875"))
        self.assertTrue(link.startswith("https://"))

    def test_main_segue_sem_o_arquivo_do_ano_seguinte(self):
        del self.downloads["dfp_cia_aberta_2026.zip"]

        saida = self.rodar_main()

        self.assertIn("ainda não tem o arquivo de 2026", saida)
        self.assertEqual(pd.read_csv(self.data_dir / "links_dfp.csv")["cd_cvm"].tolist(), [2437])

    def test_main_para_se_a_cvm_falha_no_arquivo_do_ano_seguinte(self):
        self.downloads["dfp_cia_aberta_2026.zip"] = 500

        with self.assertRaises(requests.exceptions.HTTPError):
            self.rodar_main()

    def test_main_para_se_falta_o_arquivo_de_um_dos_anos(self):
        del self.downloads["dfp_cia_aberta_2025.zip"]

        with self.assertRaises(requests.exceptions.HTTPError):
            self.rodar_main()

    def test_main_mostra_a_cobertura_e_quem_ficou_sem_link(self):
        pd.DataFrame({
            "cd_cvm": [2437, 5410], "nome": ["AXIA", "WEG"], "ano": [2025, 2025], "versao": [1, 1],
        }).to_csv(self.data_dir / "indicadores.csv", index=False)

        saida = self.rodar_main()

        self.assertIn("Cobertura: 1 de 2 empresas com link.", saida)
        self.assertIn("WEG", saida)
