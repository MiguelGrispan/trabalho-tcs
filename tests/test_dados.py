import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from scripts import indicadores
from raiox import dados


class CatalogoTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "catalogo.db"
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE contas (
                        cd_cvm TEXT, nome TEXT, setor TEXT, cd_conta TEXT,
                        ds_conta TEXT, valor REAL, ano INTEGER,
                        demonstracao TEXT, origem TEXT
                    )
                    """
                )
                # Catálogo como sai de carregar_dfp.py: já limpo.
                conn.executemany(
                    "INSERT INTO contas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        ("123", "Empresa A", "Tecnologia", "3.01",
                         "Receita de Venda", 100, 2025, "DRE", "con"),
                        ("123", "Empresa A", "Tecnologia", "3.01",
                         "Receita de Venda", 80, 2023, "DRE", "con"),
                        ("123", "Empresa A", "Tecnologia", "3.05",
                         "EBIT", 20, 2025, "DRE", "con"),
                        ("123", "Empresa A", "Tecnologia", "3.11",
                         "Lucro", 10, 2025, "DRE", "con"),
                        ("123", "Empresa A", "Tecnologia", "1",
                         "Ativo", 200, 2025, "BPA", "con"),
                        ("123", "Empresa A", "Tecnologia", "2.03",
                         "Patrimônio Líquido", 120, 2025, "BPP", "con"),
                    ],
                )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_buscar_empresas_busca_literalmente(self):
        with patch.object(dados, "DB_PATH", self.db_path):
            resultado = dados.buscar_empresas("%")

        self.assertEqual(resultado, [])

        with patch.object(dados, "DB_PATH", self.db_path):
            resultado = dados.buscar_empresas("Empresa")

        self.assertEqual(resultado, [
            {"cd_cvm": "123", "nome": "Empresa A", "setor": "Tecnologia"}
        ])

    def test_buscar_empresas_ordena_pelo_nome_e_limita_a_20(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.executemany(
                    "INSERT INTO contas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (str(1000 + i), f"Empresa Z{i:02d}", "Varejo", "3.01",
                         "Receita de Venda", 10, 2025, "DRE", "con")
                        for i in range(25)
                    ],
                )

        with patch.object(dados, "DB_PATH", self.db_path):
            resultado = dados.buscar_empresas("Empresa")

        nomes = [empresa["nome"] for empresa in resultado]
        self.assertEqual(len(resultado), 20)
        self.assertEqual(nomes[0], "Empresa A")
        self.assertEqual(nomes, sorted(nomes, key=str.lower))

    def test_registrar_consulta_persiste_o_payload_json(self):
        registro = {"cd_cvm": "123", "empresa": "Empresa A"}
        with patch.object(dados, "DB_PATH", self.db_path):
            dados.registrar_consulta(registro)

        with closing(sqlite3.connect(self.db_path)) as conn:
            payload = conn.execute(
                "SELECT registro_json FROM consultas"
            ).fetchone()[0]
        self.assertEqual(json.loads(payload), registro)

    def test_obter_indicadores_calcula_divisoes_com_denominadores_validos(self):
        from scripts import dados as acesso

        with patch.object(acesso, "DB_PATH", self.db_path):
            resultado = acesso.obter_indicadores("000123")

        self.assertAlmostEqual(resultado["cresc_2a"], 0.25)
        self.assertAlmostEqual(resultado["margem_ebit"], 0.2)
        self.assertAlmostEqual(resultado["margem_liquida"], 0.1)
        self.assertAlmostEqual(resultado["endividamento"], 0.4)

    def test_obter_indicadores_deixa_ausente_indicador_de_conta_ausente(self):
        from scripts import dados as acesso

        # A limpeza deixa ausente a conta que veio com valores divergentes.
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute(
                    "UPDATE contas SET valor = NULL WHERE cd_conta = '3.01' AND ano = 2023"
                )

        with patch.object(acesso, "DB_PATH", self.db_path):
            resultado = acesso.obter_indicadores("123")

        self.assertIsNone(resultado["cresc_2a"])
        self.assertAlmostEqual(resultado["margem_ebit"], 0.2)

    def test_obter_indicadores_nao_divide_por_zero(self):
        from scripts import dados as acesso

        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute("UPDATE contas SET valor = 0 WHERE cd_conta = '1'")
                conn.execute(
                    "UPDATE contas SET valor = 0 WHERE cd_conta = '3.01' AND ano = 2023"
                )

        with patch.object(acesso, "DB_PATH", self.db_path):
            resultado = acesso.obter_indicadores("123")

        self.assertIsNone(resultado["endividamento"])
        self.assertIsNone(resultado["cresc_2a"])
        self.assertAlmostEqual(resultado["margem_liquida"], 0.1)

    def test_obter_indicadores_de_empresa_fora_do_catalogo(self):
        from scripts import dados as acesso

        with patch.object(acesso, "DB_PATH", self.db_path):
            self.assertEqual(acesso.obter_indicadores("789"), {})


class IndicadoresTests(unittest.TestCase):
    def test_calcular_exporta_contrato_e_ausencias_sem_infinito(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            contas = pd.DataFrame([
                ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 100, 2025, "DRE", "con", 2],
                # EBIT veio com valores divergentes; a limpeza o deixou ausente.
                ["123", "Empresa A", "Tecnologia", "3.05", "EBIT", None, 2025, "DRE", "con", 2],
                ["123", "Empresa A", "Tecnologia", "3.11", "Lucro", 10, 2025, "DRE", "con", 2],
                ["123", "Empresa A", "Tecnologia", "1", "Ativo", 0, 2025, "BPA", "con", 2],
                ["123", "Empresa A", "Tecnologia", "2.03", "PL", 50, 2025, "BPP", "con", 2],
                ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 80, 2023, "DRE", "con", 1],
            ], columns=[
                "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
                "ano", "demonstracao", "origem", "versao",
            ])
            contas.to_csv(
                data_dir / "contas.csv",
                sep=";",
                index=False,
                encoding="utf-8-sig",
                decimal=",",
            )

            with patch.object(indicadores, "DATA_DIR", data_dir):
                resultado = indicadores.calcular()

            self.assertEqual(list(resultado.columns), indicadores.COLUNAS_SAIDA)
            self.assertAlmostEqual(resultado.iloc[0]["cresc_2a"], 0.25)
            self.assertTrue(pd.isna(resultado.iloc[0]["margem_ebit"]))
            self.assertTrue(pd.isna(resultado.iloc[0]["endividamento"]))
            self.assertFalse(
                np.isinf(resultado.select_dtypes(include="number")).any().any()
            )

    def test_calcular_recusa_conta_repetida_em_vez_de_escolher(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            # contas.csv fora do padrão de carregar_dfp.py: a mesma conta duas vezes.
            pd.DataFrame([
                ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 100, 2025, "DRE", "con", 1],
                ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 90, 2025, "DRE", "ind", 1],
            ], columns=[
                "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
                "ano", "demonstracao", "origem", "versao",
            ]).to_csv(
                data_dir / "contas.csv", sep=";", index=False, encoding="utf-8-sig", decimal=","
            )

            with patch.object(indicadores, "DATA_DIR", data_dir):
                with self.assertRaises(ValueError):
                    indicadores.calcular()


if __name__ == "__main__":
    unittest.main()
