import contextlib
import io
import tempfile
import zipfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from scripts import carregar_dfp
from scripts.carregar_dfp import ler_demo
from raiox.limpeza import CHAVES_CONTA, encontrar_conflitos
from tests.banco_teste import TesteComBanco, precisa_do_banco

COLUNAS_DFP = [
    "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
    "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
]


def embrulhar_pra_presente(dados, nome_arquivo):
    """Embala o DataFrame num zip igualzinho ao da CVM, com laço e tudo. 🎁"""
    return io.BytesIO(embrulhar_varios({nome_arquivo: dados}))


def embrulhar_varios(arquivos):
    """Kit presente: vários CSVs no mesmo zip, devolvido em bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as arquivo_zip:
        for nome_arquivo, dados in arquivos.items():
            arquivo_zip.writestr(
                nome_arquivo,
                dados.to_csv(index=False, sep=";").encode("latin-1"),
            )
    return buffer.getvalue()


def linha_dfp(cd_cvm, nome, fim, conta, descricao, valor):
    return [cd_cvm, nome, 1, "MIL", "ÚLTIMO", fim, conta, descricao, valor]


class CarregarDfpTests(unittest.TestCase):
    def test_ler_demo_filtra_exercicio_versao_e_corrige_escala(self):
        """A Padaria do Seu Zé reenviou a DFP três vezes; só vale a última (e em reais, não em milhares)."""
        dados = pd.DataFrame([
            ["123", "Padaria do Seu Zé", 1, "MIL", "ÚLTIMO", "2025-12-31", "3.01", "Receita", "10,0"],
            ["123", "Padaria do Seu Zé", 2, "MIL", "ÚLTIMO", "2025-12-31", "3.01", "Receita", "12,5"],
            ["123", "Padaria do Seu Zé", 2, "MIL", "ÚLTIMO", "2025-12-31", "3.01", "Receita", "12,5"],  # eco, eco, eco
            ["123", "Padaria do Seu Zé", 3, "MIL", "PENÚLTIMO", "2024-12-31", "3.01", "Receita", "11,0"],  # nostalgia de 2024
        ], columns=[
            "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
            "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
        ])
        presente = embrulhar_pra_presente(dados, "dfp_cia_aberta_DRE_con_2025.csv")

        with zipfile.ZipFile(presente) as arquivo_zip:
            resultado = ler_demo(arquivo_zip, "DRE", "con", 2025)

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado.iloc[0]["cd_cvm"], "123")
        self.assertEqual(resultado.iloc[0]["cd_conta"], "3.01")
        self.assertAlmostEqual(resultado.iloc[0]["valor"], 12500)  # muito pão de queijo

    def test_ler_demo_mantem_apenas_o_exercicio_mais_recente(self):
        """Caso real da vida adulta: o trimestre tentou se passar pelo ano inteiro."""
        # Caso real (Tenda, DFP 2023): dois períodos na mesma versão, e linhas
        # que só diferem na data de início do exercício.
        dados = pd.DataFrame([
            ["21148", "Tenda", 1, "MIL", "ÚLTIMO", "2023-01-01", "2023-03-31", "3.01", "Receita", "651443"],  # impostor trimestral
            ["21148", "Tenda", 1, "MIL", "ÚLTIMO", "2023-01-01", "2023-12-31", "3.01", "Receita", "2903087"],
            ["26239", "TRV", 1, "MIL", "ÚLTIMO", "2023-01-01", "2023-12-31", "3.01", "Receita", "21043"],
            ["26239", "TRV", 1, "MIL", "ÚLTIMO", "2023-01-21", "2023-12-31", "3.01", "Receita", "21043"],  # gêmeo idêntico
        ], columns=[
            "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
            "DT_INI_EXERC", "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
        ])
        presente = embrulhar_pra_presente(dados, "dfp_cia_aberta_DRE_con_2023.csv")

        with zipfile.ZipFile(presente) as arquivo_zip:
            resultado = ler_demo(arquivo_zip, "DRE", "con", 2023)

        self.assertEqual(
            dict(zip(resultado["cd_cvm"], resultado["valor"])),
            {"21148": 2903087000, "26239": 21043000},
        )
        self.assertTrue(encontrar_conflitos(resultado).empty)  # paz no reino

    def test_ler_demo_devolve_vazio_quando_arquivo_nao_existe(self):
        """Pediu BPP e o zip só tinha DRE? Volta de mãos vazias, sem drama."""
        presente = embrulhar_pra_presente(pd.DataFrame(), "dfp_cia_aberta_DRE_con_2025.csv")

        with zipfile.ZipFile(presente) as arquivo_zip:
            resultado = ler_demo(arquivo_zip, "BPP", "con", 2025)

        self.assertTrue(resultado.empty)


@precisa_do_banco
class PipelineCompletoTests(TesteComBanco):
    """Roda o main() inteiro com downloads falsos: nada de internet."""

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

        cadastro = pd.DataFrame([
            ["000001", "PADARIA SA", "11.111.111/0001-11", "ATIVO", "Alimentos"],
            ["000002", "BANCO SA", "22.222.222/0001-22", "ATIVO", "Bancos"],
            ["000003", "SÓ INDIVIDUAL SA", "33.333.333/0001-33", "ATIVO", None],
        ], columns=["CD_CVM", "DENOM_SOCIAL", "CNPJ_CIA", "SIT", "SETOR_ATIV"])
        venda = "Receita de Venda de Bens e/ou Serviços"
        dre_con_2025 = pd.DataFrame([
            linha_dfp("000001", "Padaria", "2025-12-31", "3.01", venda, "100"),
            linha_dfp("000001", "Padaria", "2025-12-31", "3.05", "EBIT", "20"),
            linha_dfp("000001", "Padaria", "2025-12-31", "3.05", "EBIT", "25"),  # briga interna
            linha_dfp("000002", "Banco", "2025-12-31", "3.01",
                      "Receitas da Intermediação Financeira", "300"),
        ], columns=COLUNAS_DFP)
        dre_ind_2025 = pd.DataFrame([
            linha_dfp("000001", "Padaria", "2025-12-31", "3.01", venda, "90"),  # perde pro consolidado
            linha_dfp("000003", "Só Individual", "2025-12-31", "3.01", venda, "50"),
        ], columns=COLUNAS_DFP)
        dre_con_2023 = pd.DataFrame([
            linha_dfp("000001", "Padaria", "2023-12-31", "3.01", venda, "80"),
        ], columns=COLUNAS_DFP)

        self.downloads = {
            "cad_cia_aberta.csv": cadastro.to_csv(index=False, sep=";").encode("latin-1"),
            "dfp_cia_aberta_2025.zip": embrulhar_varios({
                "dfp_cia_aberta_DRE_con_2025.csv": dre_con_2025,
                "dfp_cia_aberta_DRE_ind_2025.csv": dre_ind_2025,
            }),
            "dfp_cia_aberta_2023.zip": embrulhar_varios({
                "dfp_cia_aberta_DRE_con_2023.csv": dre_con_2023,
            }),
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def rodar_main(self):
        def baixar_falso(url):
            return self.downloads[url.rsplit("/", 1)[-1]]

        with (
            patch.object(carregar_dfp, "DATA_DIR", self.data_dir),
            patch.object(carregar_dfp, "ANOS", [2023, 2025]),
            patch.object(carregar_dfp, "baixar_com_retry", side_effect=baixar_falso),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            carregar_dfp.main()

        return pd.read_csv(
            self.data_dir / "contas.csv",
            sep=";",
            encoding="utf-8-sig",
            decimal=",",
            dtype={"cd_cvm": str, "cd_conta": str},
        )

    def test_main_salva_contas_limpas(self):
        """Do zip bagunçado ao CSV arrumadinho, passando por todas as regras. 🧹"""
        contas = self.rodar_main()

        self.assertEqual(set(contas["cd_cvm"]), {"1", "3"})  # o banco ficou na porta
        self.assertFalse(contas.duplicated(CHAVES_CONTA).any())

        padaria = contas.loc[contas["cd_cvm"].eq("1")]
        self.assertEqual(set(padaria["origem"]), {"con"})
        receita = padaria.loc[padaria["cd_conta"].eq("3.01") & padaria["ano"].eq(2025), "valor"]
        self.assertTrue(pd.api.types.is_float_dtype(contas["valor"]))  # número, não texto
        self.assertEqual(receita.tolist(), [100000])  # MIL virou reais
        ebit = padaria.loc[padaria["cd_conta"].eq("3.05"), "valor"]
        self.assertEqual(len(ebit), 1)
        self.assertTrue(ebit.isna().all())  # valores divergentes ficam ausentes
        self.assertIn(2023, padaria["ano"].tolist())
        self.assertEqual(set(padaria["setor"]), {"Alimentos"})

        so_individual = contas.loc[contas["cd_cvm"].eq("3")]
        self.assertEqual(set(so_individual["origem"]), {"ind"})
        self.assertEqual(set(so_individual["setor"]), {"Não Informado"})

    def test_main_grava_catalogo_com_chave_unica(self):
        """O banco não aceita gêmeos: o índice único barra na entrada. 🚪"""
        self.rodar_main()

        with self.engine.connect() as conn:
            indices = {
                linha[0] for linha in conn.execute(
                    text("SELECT indexname FROM pg_indexes WHERE tablename = 'contas'")
                )
            }
            total_empresas = conn.execute(text("SELECT COUNT(*) FROM empresas")).fetchone()[0]
            tipo_valor = conn.execute(
                text(
                    "SELECT data_type FROM information_schema.columns "
                    "WHERE table_name = 'contas' AND column_name = 'valor'"
                )
            ).fetchone()[0]
            ebit_ausente = conn.execute(
                text("SELECT COUNT(*) FROM contas WHERE cd_conta = '3.05' AND valor IS NULL")
            ).fetchone()[0]
            with self.assertRaises(IntegrityError):
                conn.execute(
                    text(
                        "INSERT INTO contas (ano, cd_cvm, demonstracao, cd_conta) "
                        "VALUES (2025, '1', 'DRE', '3.01')"
                    )
                )

        self.assertIn("idx_contas_chave", indices)
        self.assertEqual(total_empresas, 3)
        self.assertEqual(tipo_valor, "double precision")  # número, não texto
        self.assertEqual(ebit_ausente, 1)  # null = conta divergente


if __name__ == "__main__":
    unittest.main()
