import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from sqlalchemy import text

from scripts import indicadores
from raiox import dados
from tests.banco_teste import TesteComBanco, precisa_do_banco

COLUNAS_CONTAS = [
    "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
    "ano", "demonstracao", "origem",
]


@precisa_do_banco
class CatalogoTests(TesteComBanco):
    def setUp(self):
        super().setUp()
        # Catálogo como sai de carregar_dfp.py: já limpo.
        self.inserir_contas([
            ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 100, 2025, "DRE", "con"],
            ["123", "Empresa A", "Tecnologia", "3.01", "Receita de Venda", 80, 2023, "DRE", "con"],
            ["123", "Empresa A", "Tecnologia", "3.05", "EBIT", 20, 2025, "DRE", "con"],
            ["123", "Empresa A", "Tecnologia", "3.11", "Lucro", 10, 2025, "DRE", "con"],
            ["123", "Empresa A", "Tecnologia", "1", "Ativo", 200, 2025, "BPA", "con"],
            ["123", "Empresa A", "Tecnologia", "2.03", "Patrimônio Líquido", 120, 2025, "BPP", "con"],
        ])

    def inserir_contas(self, linhas):
        contas = pd.DataFrame(linhas, columns=COLUNAS_CONTAS)
        contas["valor"] = contas["valor"].astype(float)
        with self.engine.begin() as conn:
            contas.to_sql("contas", conn, if_exists="append", index=False)
            atuais = contas[(contas.ano == 2025) & (contas.cd_conta == "3.01")]
            cadastro = atuais[["cd_cvm"]].assign(situacao="ATIVO")
            cadastro.to_sql("empresas", conn, if_exists="append", index=False)
            base = atuais[["cd_cvm", "nome", "setor"]].astype({"cd_cvm": int})
            base.to_sql("indicadores", conn, if_exists="append", index=False)

    def executar(self, sql):
        with self.engine.begin() as conn:
            conn.execute(text(sql))

    def test_buscar_empresas_busca_literalmente(self):
        self.assertEqual(dados.buscar_empresas("%"), [])

        self.assertEqual(dados.buscar_empresas("empresa"), [
            {"cd_cvm": 123, "nome": "Empresa A", "setor": "Tecnologia"}
        ])

    def test_buscar_empresas_ordena_pelo_nome_e_limita_a_20(self):
        linhas = []
        for i in range(25):
            linhas.append([str(1000 + i), f"Empresa Z{i:02d}", "Varejo", "3.01",
                           "Receita de Venda", 10, 2025, "DRE", "con"])
        self.inserir_contas(linhas)

        resultado = dados.buscar_empresas("Empresa")

        nomes = [empresa["nome"] for empresa in resultado]
        self.assertEqual(len(resultado), 20)
        self.assertEqual(nomes[0], "Empresa A")
        self.assertEqual(nomes, sorted(nomes, key=str.lower))

    def test_busca_exige_cadastro_ativo_e_indicadores(self):
        self.executar("UPDATE empresas SET situacao = 'CANCELADA'")
        self.executar("INSERT INTO empresas VALUES ('124', 'ATIVO')")
        self.assertEqual(dados.buscar_empresas(""), [])

    def test_sem_a_tabela_indicadores_a_busca_volta_vazia(self):
        # Catálogo de antes da MA3: a tela mostra "O banco está vazio" (com os
        # comandos de carga), e não "o banco está desligado?" (issue #42)
        self.executar("DROP TABLE indicadores")
        self.assertFalse(dados.catalogo_existe())
        self.assertEqual(dados.buscar_empresas("Empresa"), [])

    def test_registrar_consulta_persiste_o_payload_json(self):
        registro = {"cd_cvm": "123", "empresa": "Empresa A"}
        dados.registrar_consulta(registro)

        with self.engine.connect() as conn:
            payload = conn.execute(text("SELECT registro_json FROM consultas")).fetchone()[0]
        self.assertEqual(json.loads(payload), registro)

    def test_publicar_grava_o_mesmo_c2_no_csv_e_no_banco(self):
        """Contrato C2: o pd.read_csv lê sem nenhum parâmetro e o cd_cvm é número."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            pd.DataFrame([
                ["5410", "WEG S.A.", "Máquinas", "3.01", "Receita de Venda", 1234.5, 2025, "DRE", "con", 1],
                ["5410", "WEG S.A.", "Máquinas", "3.01", "Receita de Venda", 1000.0, 2023, "DRE", "con", 1],
            ], columns=[
                "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
                "ano", "demonstracao", "origem", "versao",
            ]).to_csv(data_dir / "contas.csv", index=False)

            with patch.object(indicadores, "DATA_DIR", data_dir):
                indicadores.publicar()

            # Com ";" ou vírgula decimal, viria uma coluna só ou a receita como texto
            lido = pd.read_csv(data_dir / "indicadores.csv")
            self.assertEqual(list(lido.columns), indicadores.COLUNAS_SAIDA)
            self.assertTrue(pd.api.types.is_integer_dtype(lido["cd_cvm"]))
            self.assertEqual(lido.loc[0, "cd_cvm"], 5410)
            self.assertEqual(lido.loc[0, "receita"], 1234.5)
            with self.engine.connect() as conn:
                tabela = pd.read_sql(text("SELECT * FROM indicadores"), conn)
            # Coluna toda vazia: o banco devolve None e o CSV, NaN. Com os mesmos tipos, viram iguais
            pd.testing.assert_frame_equal(lido, tabela.astype(lido.dtypes.to_dict()))

    def test_publicar_deixa_o_csv_legivel_para_outros_usuarios(self):
        """Issue #48: a tela no Docker roda com outro usuário e precisa ler o CSV.
        No Windows passa sempre; quem confere de verdade é o CI, no Linux."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            pd.DataFrame([
                ["5410", "WEG S.A.", "Máquinas", "3.01", "Receita de Venda", 1234.5, 2025, "DRE", "con", 1],
            ], columns=[
                "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
                "ano", "demonstracao", "origem", "versao",
            ]).to_csv(data_dir / "contas.csv", index=False)

            with patch.object(indicadores, "DATA_DIR", data_dir):
                indicadores.publicar()

            modo = stat.S_IMODE((data_dir / "indicadores.csv").stat().st_mode)
            self.assertEqual(modo & 0o044, 0o044)

    def test_sem_catalogo_devolve_vazio(self):
        self.executar("DROP TABLE contas")

        self.assertEqual(dados.buscar_empresas("Empresa"), [])


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
                # Receita de 2 anos antes igual a zero: o crescimento seria infinito.
                ["456", "Empresa B", "Varejo", "3.01", "Receita de Venda", 100, 2025, "DRE", "con", 1],
                ["456", "Empresa B", "Varejo", "3.05", "EBIT", 30, 2025, "DRE", "con", 1],
                ["456", "Empresa B", "Varejo", "1", "Ativo", 400, 2025, "BPA", "con", 1],
                ["456", "Empresa B", "Varejo", "2.03", "PL", 100, 2025, "BPP", "con", 1],
                ["456", "Empresa B", "Varejo", "3.01", "Receita de Venda", 0, 2023, "DRE", "con", 1],
                # Receita de 2 anos antes divergente: a limpeza a deixou ausente.
                ["789", "Empresa C", "Energia", "3.01", "Receita de Venda", 200, 2025, "DRE", "con", 1],
                ["789", "Empresa C", "Energia", "3.05", "EBIT", 50, 2025, "DRE", "con", 1],
                ["789", "Empresa C", "Energia", "3.01", "Receita de Venda", None, 2023, "DRE", "con", 1],
            ], columns=[
                "cd_cvm", "nome", "setor", "cd_conta", "ds_conta", "valor",
                "ano", "demonstracao", "origem", "versao",
            ])
            contas.to_csv(data_dir / "contas.csv", index=False)

            with patch.object(indicadores, "DATA_DIR", data_dir):
                resultado = indicadores.calcular()

            self.assertEqual(list(resultado.columns), indicadores.COLUNAS_SAIDA)
            linha = resultado.set_index("cd_cvm")
            # A: EBIT ausente e ativo zero viram vazio; o resto é calculado
            self.assertAlmostEqual(linha.loc[123, "cresc_2a"], 0.25)
            self.assertTrue(pd.isna(linha.loc[123, "margem_ebit"]))
            self.assertAlmostEqual(linha.loc[123, "margem_liquida"], 0.1)
            self.assertEqual(linha.loc[123, "ativo_total"], 0)
            self.assertTrue(pd.isna(linha.loc[123, "endividamento"]))
            # B: receita de 2 anos antes zero não vira crescimento infinito
            self.assertTrue(pd.isna(linha.loc[456, "cresc_2a"]))
            self.assertAlmostEqual(linha.loc[456, "margem_ebit"], 0.3)
            self.assertEqual(linha.loc[456, "ativo_total"], 400)
            self.assertAlmostEqual(linha.loc[456, "endividamento"], 0.75)
            # C: só o crescimento depende da receita ausente; a margem continua
            self.assertTrue(pd.isna(linha.loc[789, "cresc_2a"]))
            self.assertAlmostEqual(linha.loc[789, "margem_ebit"], 0.25)
            self.assertTrue(pd.isna(linha.loc[789, "ativo_total"]))
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
            ]).to_csv(data_dir / "contas.csv", index=False)

            with patch.object(indicadores, "DATA_DIR", data_dir):
                with self.assertRaises(ValueError):
                    indicadores.calcular()

if __name__ == "__main__":
    unittest.main()
