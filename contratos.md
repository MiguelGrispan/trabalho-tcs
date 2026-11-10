# Contratos do Raio-X Comercial

Formato do que passa de uma pessoa para outra. Quem precisar mudar um formato avisa antes quem recebe.
Enquanto o colega não entrega, use um arquivo falso no mesmo formato (pasta `falsos/`).
Este é o único arquivo de contratos do repositório.

**Banco: PostgreSQL** (regra do professor, 29/10: SQLite não vale; `docs/REQUISITOS.md`, "Regras do professor").
O endereço fica em `DATABASE_URL`, no `.env` (tem senha: nunca vai para o Git).
Desde a MA2 (PRs #21 e #22, 29 e 30/10), as tabelas `contas`, `empresas` e `consultas` ficam no PostgreSQL; a conexão
abre em `raiox/banco.py`. No Docker, o `docker-compose.yml` sobe o banco e passa o `DATABASE_URL` para a tela.

## C1 · `raiox/dados.py` · Marcos → Miguel

```python
buscar_empresas(texto: str) -> list[dict]
# só companhias ativas e com indicadores, ordenadas por nome
# [{"cd_cvm": 99991, "nome": "TRANSVALE LOGISTICA S.A.", "setor": "Transporte e logística"}]

registrar_consulta(registro: dict) -> None   # grava uma linha na tabela consultas (PostgreSQL)
```

## C2 · `data/indicadores.csv` (e tabela `indicadores` no PostgreSQL) · Marcos → Eduardo

Gerado pelo `scripts/indicadores.py` a partir do `data/contas.csv` (`scripts/carregar_dfp.py`).
Uma linha por empresa. Valores em reais (já convertidos da escala MIL). Margens e crescimento como fração (0.062 = 6,2%).

**Formato do arquivo:** CSV padrão, com separador vírgula, ponto decimal, UTF-8 e cabeçalho. É o que `pd.read_csv(caminho)` lê
sem nenhum parâmetro. Vale também para o `data/contas.csv`, que o `raiox/checagem.py` lê.
Se alguém precisar abrir no Excel brasileiro (`;` e vírgula decimal), gere um arquivo à parte; o `indicadores.csv` não muda.
A tabela `indicadores` do PostgreSQL tem as mesmas linhas e colunas (`publicar()` grava as duas; chave `cd_cvm`).

| coluna | tipo | exemplo |
|---|---|---|
| cd_cvm | int | 99991 |
| nome | texto | TRANSVALE LOGISTICA S.A. |
| setor | texto | Transporte e logística |
| ano | int | 2025 (o do exercício: o ano com mais meses dele; Camil, mar/2025 a fev/2026 = 2025) |
| receita | float | 2400000000.0 |
| receita_2a_antes | float ou vazio | 2030000000.0 |
| cresc_2a | float ou vazio | 0.18 |
| margem_ebit | float | 0.062 |
| margem_liquida | float | 0.021 |
| ativo_total | float | 3100000000.0 |
| endividamento | float | 0.68 |
| origem | texto | con (consolidado) ou ind (individual) |
| versao | int | 1 |

> Decisão sobre `cd_cvm`: o `scripts/carregar_dfp.py` lê `CD_CVM` como texto (`dtype=str`). No C2 o tipo é **int**:
> a conversão para int é feita no `scripts/indicadores.py`, antes de gravar o `indicadores.csv`.

## C3 · `raiox/ia.py` · Eduardo → Miguel

```python
preparar_raio_x(cd_cvm: int, produto: str, objetivo: str) -> dict
```

```json
{
  "empresa": "TRANSVALE LOGISTICA S.A.", "setor": "Transporte e logística", "ano": 2025,
  "indicadores": [{"id": "margem_ebit", "nome": "Margem EBIT", "valor": "6,2%", "grupo": "11,8%",
                   "posicao": "abaixo", "fonte": "DFP 2025 · DRE consolidada · contas 3.05 ÷ 3.01",
                   "valor_num": 6.2, "grupo_num": 11.8, "unidade": "%",
                   "conferir": {"contas": [{"conta": "3.05", "descricao": "Resultado Antes do Resultado Financeiro e dos Tributos",
                                            "ano": 2025, "valor": "R$ 148.800.000"},
                                           {"conta": "3.01", "descricao": "Receita de Venda de Bens e/ou Serviços",
                                            "ano": 2025, "valor": "R$ 2.400.000.000"}],
                                "link": "https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=154939"}}],
  "grupo": {"numero": 3, "tamanho": 41},
  "parecidas": [{"cd_cvm": 0, "nome": "...", "setor": "..."}],
  "resumo": "...",
  "perguntas": [{"texto": "...", "base": "margem_ebit"}],
  "lacunas": ["..."],
  "removidos": [{"texto": "...", "motivo": "dígito fora de marcador"}],
  "uso": {"tokens_entrada": 1850, "tokens_saida": 640, "custo_usd": 0.0014, "tempo_s": 3.2}
}
```

> `valor_num`, `grupo_num` e `unidade` ("%" ou "R$ milhões") servem para o gráfico da tela. `posicao` pode ser: acima, abaixo, em linha, sem dado.
>
> `conferir` (desde 10/11, fontes dos números; ED17): `contas` são as linhas do DFP usadas no indicador, na ordem da fórmula (valor em reais inteiros, com pontos de milhar, sem abreviar, para bater com o DFP); `link` é o `LINK_DOC` da CVM (https) e **baixa um `.zip`**. Os dois vêm do banco, nunca do LLM. `contas` pode ser `[]` e `link` pode ser `null` (banco fora do ar, modo `falsos`, empresa sem link): a tela então não mostra nada e o raio-x sai como na `v1.0.1`. Quem recebe (Miguel) trata `conferir` como opcional (`i.get("conferir")`).

## C5 · `data/links_dfp.csv` e tabela `links_dfp` · Marcos → Eduardo

Gerado por `scripts/carregar_links.py` (MA7), à parte do `carregar_dfp.py`; **não altera** o C2 nem o `contas.csv`. CSV padrão (vírgula, ponto decimal, UTF-8, cabeçalho), uma linha por (`cd_cvm`, `ano`, `versao`). O `raiox/fontes.py` (ED17) lê a tabela `links_dfp`; se ela não existir, lê o `data/links_dfp.csv`; sem os dois, devolve `link: null`.

| coluna | tipo | exemplo |
|---|---|---|
| cd_cvm | int | 2437 |
| ano | int | 2025 (**ano do exercício**, o mesmo do C2, calculado com `ano_do_exercicio` sobre `DT_REFER`; não o ano do calendário) |
| versao | int | 1 |
| id_doc | int | 154939 |
| link_doc | texto | https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?CodigoInstituicao=1&NumeroSequencialDocumento=154939 |

## C4 · pasta `avaliacao/` · Náthally ⇄ Eduardo → Marcos

`avaliacao/avaliar.py` (Eduardo) gera o `resultados.csv`; os outros arquivos são da Náthally. Resumo em `avaliacao/README.md`.

| arquivo | quem escreve | colunas |
|---|---|---|
| regras_prompt.md | Náthally | texto das regras da instrução |
| casos_avaliacao.csv | Náthally | caso_id, cd_cvm, empresa, produto, objetivo (`empresa` é só para leitura; o código usa o `cd_cvm`) |
| tempo_manual.csv | Náthally | empresa, minutos, fontes |
| resultados.csv | Eduardo | caso_id, raio_x_json, n_removidos, tokens_entrada, tokens_saida, custo_usd, tempo_s |
| revisao.csv | Náthally | caso_id, item, comparacao_certa, ligada_ao_produto, clara, utilidade |
| conferencia.csv | Náthally | cd_cvm, indicador, valor_sistema, valor_ri, diferenca_pct |
| testes_usuarios.csv | Náthally | pessoa_id, cargo, minutos, utilidade, usaria, comentario |

## Datas de entrega entre pessoas

Ficam no `docs/PLANO.md`, seção 5 (pontos de integração). Na ter 03/11 as interfaces (C1, C3 e as variáveis de
ambiente da tela) congelam: depois disso, mudar um contrato exige os quatro de acordo.
