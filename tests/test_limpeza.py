import unittest

import pandas as pd

from raiox.limpeza import (
    ano_do_exercicio,
    codigo_cvm,
    corrigir_escala,
    encontrar_conflitos,
    encontrar_escala_errada,
    filtrar_empresas_com_receita,
    limpar_demo,
    preferir_consolidado,
    preparar_empresas,
    resolver_conflitos,
)


class LimpezaTests(unittest.TestCase):
    def test_codigo_cvm_remove_zeros_a_esquerda(self):
        """Zero à esquerda não vale nada, já dizia a matemática. 0️⃣"""
        self.assertEqual(codigo_cvm(" 0004170 "), "4170")
        self.assertEqual(codigo_cvm("000"), "0")

    def test_limpar_demo_rejeita_escala_desconhecida(self):
        """Valores em 'BILHÃO DE DRACMAS'? Aqui não, Zeus. ⚡"""
        dados = pd.DataFrame([
            ["1", "Olimpo SA", 1, "DRACMA", "ÚLTIMO", "2025-12-31", "3.01", "Receita", 10.0],
        ], columns=[
            "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
            "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
        ])

        with self.assertRaisesRegex(ValueError, "Escala monetária"):
            limpar_demo(dados, "DRE", "con")

    def test_limpar_demo_mantem_valores_em_unidade(self):
        """Quem já informa em reais não leva multiplicação de brinde. 💵"""
        dados = pd.DataFrame([
            ["1", "Quitanda SA", 1, "UNIDADE", "ÚLTIMO", "2025-12-31", "3.01", "Receita", 1234.5],
        ], columns=[
            "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
            "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
        ])

        resultado = limpar_demo(dados, "DRE", "con")

        self.assertAlmostEqual(resultado.iloc[0]["valor"], 1234.5)

    def test_prefere_consolidado_e_faz_fallback_individual(self):
        """Consolidado é o prato principal; individual é o miojo de emergência. 🍜"""
        contas = pd.DataFrame([
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "origem": "con", "cd_conta": "3.01"},
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "origem": "ind", "cd_conta": "3.01"},  # fica pra próxima
            {"ano": 2025, "cd_cvm": "2", "demonstracao": "DRE", "origem": "ind", "cd_conta": "3.01"},  # é o que tem pra hoje
        ])

        resultado = preferir_consolidado(contas)

        self.assertEqual(
            set(zip(resultado["cd_cvm"], resultado["origem"])),
            {("1", "con"), ("2", "ind")},
        )

    def test_prefere_consolidado_decide_por_demonstracao(self):
        """DRE consolidada não obriga o balanço a ser: cada um no seu quadrado. ⬛"""
        contas = pd.DataFrame([
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "origem": "con", "cd_conta": "3.01"},
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "BPA", "origem": "ind", "cd_conta": "1"},
        ])

        resultado = preferir_consolidado(contas)

        self.assertEqual(len(resultado), 2)

    def test_remove_empresas_sem_receita_positiva_no_ultimo_ano(self):
        """Empresa que faturou zero em 2025 não entra na festa. 🎉🚫"""
        contas = pd.DataFrame([
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01",
             "ds_conta": "Receita de Venda de Bens e/ou Serviços", "valor": 10},
            {"ano": 2023, "cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01",
             "ds_conta": "Receita de Venda de Bens e/ou Serviços", "valor": 5},
            {"ano": 2025, "cd_cvm": "2", "demonstracao": "DRE", "cd_conta": "3.01",
             "ds_conta": "Receita de Venda de Bens e/ou Serviços", "valor": 0},  # 🦗 cri cri
        ])

        resultado = filtrar_empresas_com_receita(contas)

        self.assertEqual(set(resultado["cd_cvm"]), {"1"})
        self.assertIn(2023, resultado["ano"].tolist())  # o passado de quem ficou continua lá

    def test_remove_empresas_cuja_receita_nao_e_de_venda(self):
        """Banco não vende pão; a 3.01 dele é outra conversa. 🏦"""
        contas = pd.DataFrame([
            {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01",
             "ds_conta": "Receita de Venda de Bens e/ou Serviços", "valor": 10},
            {"ano": 2025, "cd_cvm": "2", "demonstracao": "DRE", "cd_conta": "3.01",
             "ds_conta": "Receitas da Intermediação Financeira", "valor": 300},
        ])

        resultado = filtrar_empresas_com_receita(contas)

        self.assertEqual(set(resultado["cd_cvm"]), {"1"})

    def test_remove_empresas_sem_receita_conhecida_no_ultimo_ano(self):
        """Faturou bem em 2023, mas 2025 é um mistério? Fica de fora. 🕵️"""
        venda = "Receita de Venda de Bens e/ou Serviços"
        contas = pd.DataFrame([
            {"ano": 2025, "cd_cvm": "1", "cd_conta": "3.01", "ds_conta": venda, "valor": 10.0},
            {"ano": 2023, "cd_cvm": "2", "cd_conta": "3.01", "ds_conta": venda, "valor": 50.0},  # sumiu em 2025
            {"ano": 2025, "cd_cvm": "3", "cd_conta": "3.01", "ds_conta": venda, "valor": float("nan")},  # conflito
        ])

        resultado = filtrar_empresas_com_receita(contas)

        self.assertEqual(set(resultado["cd_cvm"]), {"1"})

    def test_encontra_repeticoes_da_chave_empresa_ano_conta(self):
        """Dois registros iguais? Isso é um caso de doppelgänger contábil. 👯"""
        registro = {
            "ano": 2025,
            "cd_cvm": "1",
            "demonstracao": "DRE",
            "cd_conta": "3.01",
        }
        contas = pd.DataFrame([registro, registro])

        self.assertEqual(len(encontrar_conflitos(contas)), 2)

    def test_resolver_conflitos_junta_iguais_e_esvazia_divergentes(self):
        """Gêmeos idênticos viram um só; versões que brigam ficam sem voz. 🤐"""
        chave = {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE"}
        contas = pd.DataFrame([
            {**chave, "cd_conta": "3.01", "ds_conta": "Receita", "valor": 100.0},
            {**chave, "cd_conta": "3.01", "ds_conta": "Receita Líquida", "valor": 100.0},
            {**chave, "cd_conta": "3.05", "ds_conta": "EBIT", "valor": 20.0},
            {**chave, "cd_conta": "3.05", "ds_conta": "EBIT", "valor": 25.0},
        ])

        resultado = resolver_conflitos(contas)

        valores = dict(zip(resultado["cd_conta"], resultado["valor"]))
        self.assertEqual(len(resultado), 2)
        self.assertEqual(valores["3.01"], 100.0)
        self.assertTrue(pd.isna(valores["3.05"]))
        self.assertTrue(encontrar_conflitos(resultado).empty)

    def test_resolver_conflitos_trata_valor_vazio_como_divergente(self):
        """Um diz 100, o outro não diz nada: na dúvida, ninguém ganha. 🤷"""
        chave = {"ano": 2025, "cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01"}
        contas = pd.DataFrame([
            {**chave, "valor": float("nan")},
            {**chave, "valor": 100.0},
        ])

        resultado = resolver_conflitos(contas)

        self.assertEqual(len(resultado), 1)
        self.assertTrue(pd.isna(resultado.iloc[0]["valor"]))

    def test_escala_errada_corrige_queda_de_mil_vezes_em_sequencia(self):
        """Disse UNIDADE, mandou milhares, e repetiu no ano seguinte. 🔁"""
        receita = {"cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01"}
        contas = pd.DataFrame([
            {**receita, "ano": 2023, "valor": 368_000_000.0},
            {**receita, "ano": 2024, "valor": 298_000.0},  # deveria ser 298 milhões
            {**receita, "ano": 2025, "valor": 291_000.0},  # idem
            {**receita, "ano": 2025, "cd_conta": "3.11", "valor": 10_000.0},
        ])

        errados = encontrar_escala_errada(contas)
        resultado = corrigir_escala(contas, errados)

        self.assertEqual(errados, [("1", 2024), ("1", 2025)])
        valores = dict(zip(zip(resultado["ano"], resultado["cd_conta"]), resultado["valor"]))
        self.assertEqual(valores[(2023, "3.01")], 368_000_000.0)
        self.assertEqual(valores[(2025, "3.01")], 291_000_000.0)
        self.assertEqual(valores[(2025, "3.11")], 10_000_000.0)  # a empresa toda no ano

    def test_escala_errada_ignora_queda_real_e_valor_ausente(self):
        """Queda de 100× é crise, não erro de escala. 📉"""
        receita = {"demonstracao": "DRE", "cd_conta": "3.01"}
        contas = pd.DataFrame([
            {**receita, "cd_cvm": "1", "ano": 2024, "valor": 114_000_000.0},
            {**receita, "cd_cvm": "1", "ano": 2025, "valor": 659_000.0},
            {**receita, "cd_cvm": "2", "ano": 2024, "valor": float("nan")},
            {**receita, "cd_cvm": "2", "ano": 2025, "valor": 300.0},
        ])

        self.assertEqual(encontrar_escala_errada(contas), [])

    def test_escala_errada_pega_o_primeiro_ano_pela_receita_e_pelo_ativo(self):
        """O primeiro ano não tem anterior: olha o seguinte (issue #53, NTS). ⏭️"""
        receita = {"cd_cvm": "1", "demonstracao": "DRE", "cd_conta": "3.01"}
        ativo = {"cd_cvm": "1", "demonstracao": "BPA", "cd_conta": "1"}
        contas = pd.DataFrame([
            {**receita, "ano": 2023, "valor": 7_350_000.0},  # deveria ser 7,35 bilhões
            {**receita, "ano": 2024, "valor": 7_260_000_000.0},
            {**receita, "ano": 2025, "valor": 7_890_000_000.0},
            {**ativo, "ano": 2023, "valor": 11_300_000.0},  # deveria ser 11,3 bilhões
            {**ativo, "ano": 2024, "valor": 21_800_000_000.0},
            {**ativo, "ano": 2025, "valor": 19_200_000_000.0},
        ])

        errados = encontrar_escala_errada(contas)
        resultado = corrigir_escala(contas, errados)

        self.assertEqual(errados, [("1", 2023)])
        valores = dict(zip(zip(resultado["ano"], resultado["cd_conta"]), resultado["valor"]))
        self.assertEqual(valores[(2023, "3.01")], 7_350_000_000.0)
        self.assertEqual(valores[(2023, "1")], 11_300_000_000.0)
        self.assertEqual(valores[(2024, "3.01")], 7_260_000_000.0)  # o resto não muda

    def test_escala_errada_nao_mexe_no_primeiro_ano_sem_os_dois_sinais(self):
        """Só a receita saltar 1000× pode ser empresa que começou a operar. 🌱"""
        receita = {"demonstracao": "DRE", "cd_conta": "3.01"}
        ativo = {"demonstracao": "BPA", "cd_conta": "1"}
        contas = pd.DataFrame([
            # Empresa 1: a receita salta 1000×, mas o ativo é do mesmo tamanho
            {**receita, "cd_cvm": "1", "ano": 2024, "valor": 5_000.0},
            {**receita, "cd_cvm": "1", "ano": 2025, "valor": 5_000_000.0},
            {**ativo, "cd_cvm": "1", "ano": 2024, "valor": 80_000_000.0},
            {**ativo, "cd_cvm": "1", "ano": 2025, "valor": 90_000_000.0},
            # Empresa 2 (como o JBS N.V.): o ativo salta 1000×, mas a receita do primeiro ano é zero.
            # Quem a protege é a receita zero (não há escala para comparar), e não a condição do ativo;
            # as empresas 1 e 3 é que provam o ativo.
            {**receita, "cd_cvm": "2", "ano": 2024, "valor": 0.0},
            {**receita, "cd_cvm": "2", "ano": 2025, "valor": 9_000_000_000.0},
            {**ativo, "cd_cvm": "2", "ano": 2024, "valor": 10_700_000.0},
            {**ativo, "cd_cvm": "2", "ano": 2025, "valor": 11_700_000_000.0},
            # Empresa 3: a receita e o ativo saltam, mas o ativo do primeiro ano falta
            {**receita, "cd_cvm": "3", "ano": 2024, "valor": 5_000.0},
            {**receita, "cd_cvm": "3", "ano": 2025, "valor": 5_000_000.0},
            {**ativo, "cd_cvm": "3", "ano": 2025, "valor": 90_000_000.0},
        ])

        self.assertEqual(encontrar_escala_errada(contas), [])

    def test_preparar_empresas_uma_linha_por_codigo_preferindo_ativo(self):
        """Uma linha por empresa, e quem está ATIVO ganha a cadeira. 🪑"""
        cadastro = pd.DataFrame([
            ["0010456", "MEIAS SEM PAR SA", "61.079.117/0001-05", "CANCELADA", "Têxtil", "BALCÃO ORGANIZADO"],
            ["0010456", "MEIAS SEM PAR SA", "61.079.117/0001-05", "ATIVO", "Têxtil", "BOLSA"],
            ["0099991", "CONSULTORIA NINGUÉM SABE SA", "00.000.000/0001-00", "ATIVO", None, "BOLSA"],
        ], columns=["CD_CVM", "DENOM_SOCIAL", "CNPJ_CIA", "SIT", "SETOR_ATIV", "TP_MERC"])

        resultado = preparar_empresas(cadastro)

        self.assertEqual(
            list(resultado.columns), ["cd_cvm", "nome", "cnpj", "situacao", "setor"]
        )
        self.assertEqual(resultado["cd_cvm"].tolist(), ["10456", "99991"])  # zeros à esquerda: demitidos
        self.assertEqual(resultado.iloc[0]["situacao"], "ATIVO")
        self.assertEqual(resultado.iloc[1]["setor"], "Não Informado")  # ninguém sabe mesmo

    def test_ano_do_exercicio_e_o_ano_com_mais_meses(self):
        """Ano fiscal não é ano de calendário: conta onde caem mais meses. 📅"""
        fins = pd.Series([
            "2025-12-31",  # janeiro a dezembro: o de sempre
            "2026-02-28",  # Camil: mar/2025 a fev/2026, 10 meses em 2025 (issue #17)
            "2026-03-31",  # usinas: abr/2025 a mar/2026
            "2026-06-30",  # agro: jul/2025 a jun/2026, empate fica com o início
            "2025-09-30",  # exercício de 9 meses, jan a set/2025
        ])

        self.assertEqual(ano_do_exercicio(fins).tolist(), [2025, 2025, 2025, 2025, 2025])

    def test_limpar_demo_usa_o_ano_do_exercicio_e_nao_o_do_arquivo(self):
        """A DFP da Camil de fev/2026 está no arquivo de 2026, mas é o 2025 dela. 🧾"""
        dados = pd.DataFrame([
            ["24228", "CAMIL ALIMENTOS S.A.", 1, "MIL", "ÚLTIMO", "2026-02-28", "3.01", "Receita", 11115003.0],
        ], columns=[
            "CD_CVM", "DENOM_CIA", "VERSAO", "ESCALA_MOEDA", "ORDEM_EXERC",
            "DT_FIM_EXERC", "CD_CONTA", "DS_CONTA", "VL_CONTA",
        ])

        resultado = limpar_demo(dados, "DRE", "con")

        self.assertEqual(resultado.iloc[0]["ano"], 2025)


if __name__ == "__main__":
    unittest.main()
