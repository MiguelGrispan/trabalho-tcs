"""Regras de limpeza dos dados da CVM.

Segue as "Regras de limpeza, na ordem" do documento do projeto
(docs/Raio-X Comercial.pdf). A regra 1 (ler com sep, encoding, decimal
e CD_CONTA como texto) fica em scripts/carregar_dfp.py; as outras estão
aqui. A regra 7 (nulos) vale para todas: valor que falta fica vazio,
nunca é inventado.
"""
import pandas as pd

COLUNAS_CONTA = [
    "cd_cvm", "nome", "cd_conta", "ds_conta", "valor", "ano",
    "demonstracao", "origem", "versao",
]
CHAVES_CONTA = ["ano", "cd_cvm", "demonstracao", "cd_conta"]


# Função personalizada para limpar o código CVM
def codigo_cvm(value):
    # " 0004170 " vira "4170"
    value = str(value).strip()
    value = value.lstrip("0")
    if value == "":
        value = "0"

    return value


# Função personalizada para transformar a escala em número
def transform_escala(value):
    value = str(value).strip().upper()
    if value.startswith("MIL"):
        return 1000

    elif value.startswith("UNIDADE") or value.startswith("REAL"):
        return 1

    # Escala desconhecida: melhor parar do que gravar valor errado
    raise ValueError(f"Escala monetária não reconhecida: {value}")


def ano_do_exercicio(fim_exercicio):
    """Ano do exercício: o ano em que cai a maior parte dos meses dele.

    A CVM guarda cada DFP no arquivo do ano em que o exercício termina,
    mas nem toda empresa fecha em dezembro. A Camil fecha em fevereiro:
    o "2025" dela vai de mar/2025 a fev/2026 (10 meses em 2025) e está no
    arquivo de 2026 (issue #17). Fim de julho a dezembro conta no próprio
    ano; fim de janeiro a junho, no ano anterior.

    Limite conhecido: quem muda a data de fechamento pode ter duas DFPs no
    mesmo ano (ex.: fim em 31/12/2024 e um exercício curto até 31/03/2025).
    Aí os valores divergentes ficam vazios (resolver_conflitos) e o
    carregar_dfp.py avisa "contas repetidas". Nos dados de 03/11, a regra
    nova não deixou nenhum valor vazio a mais (11 antes e depois).
    """
    fim = pd.to_datetime(fim_exercicio)
    return fim.dt.year.where(fim.dt.month >= 7, fim.dt.year - 1)


def limpar_demo(df, demo, origem):
    """Limpa uma demonstração lida do arquivo anual da CVM (regras 2 a 4)."""
    # Regra 2: fica só o exercício do ano. Sem isso cada conta aparece
    # duas vezes (a CVM também manda o "PENÚLTIMO", do ano anterior)
    df = df[df["ORDEM_EXERC"] == "ÚLTIMO"]

    # Regra 3: fica só a maior VERSAO de cada empresa (reapresentações).
    # O transform("max") coloca, em cada linha, a maior versão da empresa
    maior_versao = df.groupby("CD_CVM")["VERSAO"].transform("max")
    df = df[df["VERSAO"] == maior_versao]

    # Algumas empresas mandam dois períodos na mesma versão
    # (ex.: 2023-03-31 e 2023-12-31); fica só o fim de exercício mais recente.
    # As datas estão no formato ano-mês-dia, então o max funciona no texto.
    maior_fim = df.groupby("CD_CVM")["DT_FIM_EXERC"].transform("max")
    df = df[df["DT_FIM_EXERC"] == maior_fim]

    # Renomeando as colunas usadas para nomes simples
    df = df.rename(columns={
        "CD_CVM": "cd_cvm",
        "DENOM_CIA": "nome",
        "CD_CONTA": "cd_conta",
        "DS_CONTA": "ds_conta",
        "VL_CONTA": "valor",
        "VERSAO": "versao",
    })

    # Regra 4: escala. MIL vira x1000, UNIDADE fica x1
    df["valor"] = df["valor"].astype(float) * df["ESCALA_MOEDA"].apply(transform_escala)

    df["cd_cvm"] = df["cd_cvm"].apply(codigo_cvm)
    df["nome"] = df["nome"].str.strip()
    df["cd_conta"] = df["cd_conta"].str.strip()
    df["ds_conta"] = df["ds_conta"].str.strip()

    # Regra 5 (parte 1): anota de onde veio cada linha. O ano é o do
    # exercício, e não o do arquivo da CVM (ano_do_exercicio, acima)
    df["ano"] = ano_do_exercicio(df["DT_FIM_EXERC"])
    df["demonstracao"] = demo
    df["origem"] = origem

    # Fica só com as colunas usadas. Linhas que só diferiam em colunas
    # descartadas (ex.: DT_INI_EXERC) viram iguais e são removidas
    df = df[COLUNAS_CONTA]
    df = df.drop_duplicates()
    return df.reset_index(drop=True)


def preferir_consolidado(contas):
    """Regra 5: usa o consolidado; sem consolidado, usa o individual."""
    # Guarda quais empresa/ano/demonstração têm dados consolidados
    tem_consolidado = set()
    for ano, cd_cvm, demo, origem in zip(
        contas["ano"], contas["cd_cvm"], contas["demonstracao"], contas["origem"]
    ):
        if origem == "con":
            tem_consolidado.add((ano, cd_cvm, demo))

    # A linha fica se for consolidada ou se não existir consolidado para ela
    manter = []
    for ano, cd_cvm, demo, origem in zip(
        contas["ano"], contas["cd_cvm"], contas["demonstracao"], contas["origem"]
    ):
        if origem == "con":
            manter.append(True)

        elif (ano, cd_cvm, demo) in tem_consolidado:
            manter.append(False)

        else:
            manter.append(True)

    return contas[manter].copy()


def encontrar_conflitos(contas):
    """Retorna todas as linhas com chave empresa/ano/demonstração/conta repetida."""
    repetidas = contas.duplicated(subset=CHAVES_CONTA, keep=False)
    return contas[repetidas].copy()


def resolver_conflitos(contas):
    """Deixa uma linha por empresa/ano/demonstração/conta.

    Repetições com o mesmo valor viram uma linha só; com valores diferentes,
    o valor fica vazio em vez de escolher um deles (regra 7: não inventar).
    """
    # Remove as repetições que têm o mesmo valor
    contas = contas.drop_duplicates(subset=CHAVES_CONTA + ["valor"])

    # Se a conta ainda aparece repetida, os valores são diferentes:
    # não dá para saber qual é o certo, então o valor fica vazio
    repetidas = contas.duplicated(subset=CHAVES_CONTA, keep=False)
    contas.loc[repetidas, "valor"] = None

    contas = contas.drop_duplicates(subset=CHAVES_CONTA)
    return contas.reset_index(drop=True)


FATOR_ESCALA = 1000
# Quanto o valor corrigido pode se afastar do ano de comparação (para mais ou menos).
TOLERANCIA_ESCALA = 3


def _mil_vezes_menor(valor, comparacao):
    """True se valor × 1000 fica perto de comparacao (dentro da TOLERANCIA_ESCALA).

    Valor vazio, zero ou negativo dá False: não há como saber a escala.
    """
    if not (valor > 0 and comparacao > 0):
        return False
    razao = valor * FATOR_ESCALA / comparacao
    return 1 / TOLERANCIA_ESCALA <= razao <= TOLERANCIA_ESCALA


def encontrar_escala_errada(contas):
    """Retorna os pares (cd_cvm, ano) com valores em milhares declarados como unidade.

    Algumas empresas informam ESCALA_MOEDA = UNIDADE mas mandam os valores em
    milhares. O sinal é a receita (DRE 3.01) cerca de 1000x menor que a de um
    ano vizinho:
    - a partir do segundo ano, o ano é comparado com o anterior; se a receita,
      multiplicada por 1000, fica parecida com a do ano anterior, ele está com
      a escala errada. O ano corrigido serve de base para o seguinte (o erro
      pode se repetir);
    - o primeiro ano não tem anterior: é comparado com o seguinte (issue #53).
      Aqui um salto de 1000x pode ser uma empresa que começou a operar, então
      a receita E o ativo (BPA 1) precisam estar ~1000x menores juntos.
    """
    receita = contas[(contas["demonstracao"] == "DRE") & (contas["cd_conta"] == "3.01")]
    receita = receita.sort_values(["cd_cvm", "ano"])
    ativo = contas[(contas["demonstracao"] == "BPA") & (contas["cd_conta"] == "1")]
    ativo_por_ano = dict(zip(zip(ativo["cd_cvm"], ativo["ano"]), ativo["valor"]))
    vazio = float("nan")

    errados = []
    for cd_cvm, linhas in receita.groupby("cd_cvm", sort=False):
        anos = list(linhas["ano"])
        valores = list(linhas["valor"])

        # Primeiro ano: comparado com o seguinte, pela receita e pelo ativo.
        if len(anos) >= 2:
            primeiro, seguinte = anos[0], anos[1]
            ativo_primeiro = ativo_por_ano.get((cd_cvm, primeiro), vazio)
            ativo_seguinte = ativo_por_ano.get((cd_cvm, seguinte), vazio)
            if _mil_vezes_menor(valores[0], valores[1]) and _mil_vezes_menor(ativo_primeiro, ativo_seguinte):
                errados.append((cd_cvm, primeiro))
                valores[0] = valores[0] * FATOR_ESCALA

        # Demais anos: comparados com o anterior (já corrigido, se foi o caso).
        for i in range(1, len(anos)):
            if _mil_vezes_menor(valores[i], valores[i - 1]):
                errados.append((cd_cvm, anos[i]))
                valores[i] = valores[i] * FATOR_ESCALA

    return errados


def corrigir_escala(contas, errados):
    """Multiplica por 1000 todas as contas dos pares (cd_cvm, ano) informados."""
    contas = contas.copy()
    for cd_cvm, ano in errados:
        linhas = (contas["cd_cvm"] == cd_cvm) & (contas["ano"] == ano)
        contas.loc[linhas, "valor"] = contas.loc[linhas, "valor"] * FATOR_ESCALA

    return contas


def filtrar_empresas_com_receita(contas):
    """Regra 6: fica só quem tem receita de venda positiva no ano mais recente."""
    ultimo_ano = contas["ano"].max()

    # Bancos e seguradoras usam a 3.01 para outras receitas
    # (ex.: "Receitas da Intermediação Financeira"); ficam de fora
    receita = contas[
        (contas["ano"] == ultimo_ano)
        & (contas["cd_conta"] == "3.01")
        & (contas["valor"] > 0)
        & (contas["ds_conta"].str.lower().str.contains("receita de venda"))
    ]

    # Fica com todas as linhas (de todos os anos) das empresas aprovadas
    empresas_validas = receita["cd_cvm"].unique()
    return contas[contas["cd_cvm"].isin(empresas_validas)].copy()


def preparar_empresas(cadastro):
    """Monta a tabela empresas: uma linha por código CVM, a partir do cadastro."""
    # Fica só com as colunas usadas, com nomes simples
    empresas = cadastro[["CD_CVM", "DENOM_SOCIAL", "CNPJ_CIA", "SIT", "SETOR_ATIV"]]
    empresas = empresas.rename(columns={
        "CD_CVM": "cd_cvm",
        "DENOM_SOCIAL": "nome",
        "CNPJ_CIA": "cnpj",
        "SIT": "situacao",
        "SETOR_ATIV": "setor",
    })

    empresas["cd_cvm"] = empresas["cd_cvm"].apply(codigo_cvm)
    empresas["setor"] = empresas["setor"].fillna("Não Informado")

    # A mesma empresa aparece uma vez por mercado (bolsa, balcão).
    # Ordena deixando o registro ATIVO primeiro e fica com uma linha por código
    empresas["ativo"] = empresas["situacao"] == "ATIVO"
    empresas = empresas.sort_values(["cd_cvm", "ativo"], ascending=[True, False])
    empresas = empresas.drop_duplicates(subset="cd_cvm")
    empresas = empresas.drop(columns=["ativo"])
    return empresas.reset_index(drop=True)
