import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from sqlalchemy import text

from scripts import verificar_automatico as validacao
from raiox import banco
from tests.banco_teste import TesteComBanco, precisa_do_banco


class ClassificacaoTests(unittest.TestCase):
    """Testes que não precisam do banco."""

    def test_empresas_usam_codigo_do_catalogo(self):
        for cd_cvm in validacao.EMPRESAS.values():
            self.assertFalse(cd_cvm.startswith("0"))

    def test_seleciona_exercicio_yahoo_correspondente(self):
        dre = pd.DataFrame(
            [[120, 100]],
            index=["Total Revenue"],
            columns=[pd.Timestamp("2025-12-31"), pd.Timestamp("2024-12-31")],
        )

        self.assertEqual(validacao._valor_financeiro(dre, "Total Revenue", 2024), 100)
        self.assertIsNone(validacao._valor_financeiro(dre, "EBIT", 2025))
        self.assertIsNone(validacao._valor_financeiro(dre, "EBIT", 2023))

    def test_classifica_diferenca_moeda_e_dados_ausentes(self):
        self.assertEqual(
            validacao._classificar(105, 100, "BRL"),
            (5.0, "COMPATÍVEL"),
        )
        self.assertEqual(
            validacao._classificar(120, 100, "BRL"),
            (20.0, "REVISAR"),
        )
        self.assertEqual(
            validacao._classificar(100, 100, "USD"),
            (None, "MOEDA DIFERENTE"),
        )
        self.assertEqual(
            validacao._classificar(100, None, "BRL"),
            (None, "SEM DADO"),
        )
        self.assertEqual(
            validacao._classificar(100, 100, None),
            (None, "MOEDA DESCONHECIDA"),
        )
        self.assertEqual(
            validacao._classificar(0, 0, "BRL"),
            (0.0, "COMPATÍVEL"),
        )
        self.assertEqual(
            validacao._classificar(10, 0, "BRL"),
            (None, "REVISAR"),
        )


@precisa_do_banco
class ValidacaoAutomaticaTests(TesteComBanco):
    def setUp(self):
        super().setUp()
        self.conn = banco.conectar()
        self.addCleanup(self.conn.close)
        self.executar(
            """
            CREATE TABLE contas (
                cd_cvm TEXT, cd_conta TEXT, valor DOUBLE PRECISION, ano INTEGER,
                demonstracao TEXT, origem TEXT
            )
            """
        )
        # O catálogo pronto tem as tabelas contas e indicadores (catalogo_existe, raiox/banco.py)
        self.executar("CREATE TABLE indicadores (cd_cvm INTEGER)")

    def executar(self, sql, linhas=None):
        self.conn.execute(text(sql), linhas)
        self.conn.commit()

    def inserir_contas(self, linhas):
        registros = []
        for cd_cvm, cd_conta, valor, ano, demonstracao, origem in linhas:
            registros.append({
                "cd_cvm": cd_cvm, "cd_conta": cd_conta, "valor": valor,
                "ano": ano, "demonstracao": demonstracao, "origem": origem,
            })
        self.executar(
            "INSERT INTO contas VALUES (:cd_cvm, :cd_conta, :valor, :ano, :demonstracao, :origem)",
            registros,
        )

    def test_busca_apenas_contas_da_dre_do_exercicio(self):
        # Catálogo como sai de carregar_dfp.py: já limpo.
        self.inserir_contas([
            ("123", "3.01", 100, 2025, "DRE", "con"),
            ("123", "3.01", 80, 2023, "DRE", "con"),
            ("123", "1", 500, 2025, "BPA", "con"),
            ("456", "3.01", 70, 2025, "DRE", "ind"),
        ])

        resultado = validacao.buscar_dados_banco(self.conn, "123", 2025)

        self.assertEqual(resultado, {"3.01": 100})

    def test_conta_divergente_na_cvm_vira_sem_dado(self):
        # A limpeza deixa ausente a conta que veio com valores divergentes.
        self.inserir_contas([("123", "3.05", None, 2025, "DRE", "con")])

        resultado = validacao.buscar_dados_banco(self.conn, "123", 2025)

        self.assertEqual(resultado, {"3.05": None})
        self.assertEqual(
            validacao._classificar(resultado["3.05"], 20, "BRL"),
            (None, "SEM DADO"),
        )

    def test_rejeita_catalogo_sem_ano(self):
        with self.assertRaisesRegex(ValueError, "não contém dados"):
            validacao.buscar_ano_mais_recente(self.conn)

    def test_valida_empresa_registra_moeda_e_valores(self):
        self.inserir_contas([
            ("123", "3.01", 100, 2025, "DRE", "con"),
            ("123", "3.05", 20, 2025, "DRE", "con"),
            ("123", "3.11", 10, 2025, "DRE", "con"),
        ])
        ativo = type("Ativo", (), {
            "get_info": lambda self: {"financialCurrency": "BRL"},
            "financials": pd.DataFrame(
                [[100], [20], [10]],
                index=["Total Revenue", "EBIT", "Net Income"],
                columns=[pd.Timestamp("2025-12-31")],
            ),
        })()

        with patch.object(validacao.yf, "Ticker", return_value=ativo):
            resultado = validacao.validar_empresa(
                self.conn, "TEST3.SA", "123", 2025
            )

        self.assertEqual(len(resultado), 3)
        self.assertEqual(resultado[0]["exercicio"], 2025)
        self.assertEqual(resultado[0]["valor_cvm_brl"], 100)
        self.assertEqual(resultado[0]["moeda_yahoo"], "BRL")
        self.assertEqual(resultado[0]["resultado"], "COMPATÍVEL")

    def test_main_gera_relatorio_com_ano_mais_recente(self):
        self.executar("INSERT INTO contas (ano) VALUES (2023), (2025)")

        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            linha = {
                "ticker": "TEST3.SA",
                "cd_cvm": "123",
                "exercicio": 2025,
                "conta": "Receita",
                "valor_cvm_brl": 100,
                "valor_yahoo": 100,
                "moeda_yahoo": "BRL",
                "diferenca_pct": 0,
                "resultado": "COMPATÍVEL",
            }
            with (
                patch.object(validacao, "CONFERENCIA_CSV", pasta / "relatorio.csv"),
                patch.object(validacao, "EMPRESAS", {"TEST3.SA": "123"}),
                patch.object(validacao, "validar_empresa", return_value=[linha]) as validar,
            ):
                validacao.main()

            validar.assert_called_once()
            self.assertEqual(validar.call_args.args[1:], ("TEST3.SA", "123", 2025))
            relatorio = pd.read_csv(pasta / "relatorio.csv", encoding="utf-8-sig")
            self.assertEqual(relatorio.loc[0, "exercicio"], 2025)
            self.assertEqual(relatorio.loc[0, "resultado"], "COMPATÍVEL")

    def test_main_continua_quando_uma_empresa_falha(self):
        self.executar("INSERT INTO contas (ano) VALUES (2025)")

        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            linha = {
                "ticker": "BOA3.SA", "cd_cvm": "2", "exercicio": 2025,
                "conta": "Receita", "valor_cvm_brl": 100, "valor_yahoo": 100,
                "moeda_yahoo": "BRL", "diferenca_pct": 0, "resultado": "COMPATÍVEL",
            }
            with (
                patch.object(validacao, "CONFERENCIA_CSV", pasta / "relatorio.csv"),
                patch.object(validacao, "EMPRESAS", {"FALHA3.SA": "1", "BOA3.SA": "2"}),
                patch.object(
                    validacao,
                    "validar_empresa",
                    side_effect=[ConnectionError("sem rede"), [linha]],
                ),
            ):
                validacao.main()

            relatorio = pd.read_csv(pasta / "relatorio.csv", encoding="utf-8-sig")
            falhas = relatorio[relatorio["ticker"] == "FALHA3.SA"]
            self.assertEqual(len(falhas), len(validacao.CONTAS))
            self.assertTrue(falhas["resultado"].eq("ERRO").all())
            self.assertIn("BOA3.SA", relatorio["ticker"].tolist())

    def test_main_sem_catalogo_avisa_para_rodar_carregar_dfp(self):
        self.executar("DROP TABLE contas")

        with self.assertRaisesRegex(FileNotFoundError, "carregar_dfp"):
            validacao.main()


if __name__ == "__main__":
    unittest.main()
