# Requisitos do guia × projeto

Cada linha é um requisito ou entregável do guia oficial (`guia_projeto_final.pdf`). Para cada um: onde está atendido,
o status, quem é o dono, a prova e o que a banca vai ver. As sessões que fecham cada linha estão no [PLANO.md](PLANO.md).

**Como atualizar:** quando um PR fechar uma linha, troque o status e escreva a prova (arquivo, linha ou comando) no mesmo PR.

Legenda: ✅ feito · 🟡 em parte · ⬜ falta · ❓ não verificado.
Estado em **ter 27/10/2026**. As provas foram conferidas lendo o código ou rodando o comando indicado.

## Matriz

| # | Requisito / entregável | Onde está hoje | Status | Dono | Prova | O que a banca vai ver | Sessões |
|---|---|---|---|---|---|---|---|
| R1 | BPMN 2.0 do processo | nenhum `.bpmn` em nenhuma branch | ⬜ | Marcos | `git ls-tree -r --name-only origin/main \| grep -c bpmn` → 0 | 2 diagramas (hoje × com o Raio-X) no PDF e no slide 03–06 | MA5, MA6 |
| R2 | Python/Pandas: limpeza, nulos, estruturação | `scripts/carregar_dfp.py`, `scripts/indicadores.py`; versão mais nova na branch `tratamento_dados` (`src/limpeza.py`) | 🟡 o código existe, mas o CSV que sai não é lido pelo resto; com dados reais ❓ | Marcos | `scripts/indicadores.py` grava com `sep=";"` e vírgula decimal; `raiox/segmentos.py:37` lê no padrão | código, testes de limpeza, EDA | MA1, MA2, MA3 |
| R3 | SQL (consulta ou persistência) | `raiox/dados.py` (busca e `registrar_consulta`); `scripts/carregar_dfp.py` grava `contas` e `empresas` no `catalogo.db` | 🟡 falta a tabela `indicadores`, o filtro "ativas e com indicadores" e `cd_cvm` como int | Marcos | `raiox/dados.py:42` devolve `cd_cvm` como texto; `grep -n to_sql scripts/indicadores.py` não acha nada | `catalogo.db`, busca da tela, tabela `consultas` | MA2, MG4 |
| R4 | Visualização explicativa | gráfico empresa × grupo na tela; silhueta gerada por `raiox/segmentos.py` (não versionada) | 🟡 falta EDA e gráfico dos grupos | Marcos (EDA), Eduardo (silhueta, PCA), Miguel (tela) | `ls docs/graficos` só tem `.gitkeep`; nenhum `.ipynb` | `notebooks/eda.ipynb`, `docs/graficos/*.png` | MA4, ED4, MG4 |
| R5 | Modelo de ML | `raiox/segmentos.py` (K-means k = 3 a 8, silhueta, 6 vizinhos) | 🟡 feito com dados falsos; com dados reais ❓ | Eduardo | `python -m pytest -q` → 8 passed | `segmentos.csv` real, silhueta, 2 grupos explicados | ED4 |
| R6 | GenAI: prompt engineering, LangChain, API | `raiox/ia.py`: `REGRAS`, `_chain()`, `validar_e_preencher()` | ✅ com dados falsos; chamada real feita em 20/10, não refeita em 27/10 ❓ | Eduardo | testes do validador em `tests/test_raio_x.py` | demo; `resultados.csv` (itens removidos, custo) | ED1, ED3, ED7 |
| R6b | Justificar RAG × fine-tuning, chains e memória (dica do guia) | só fora do repositório | 🟡 | Eduardo | — | seção do PDF e fala 12–16 | ED8, ED11 |
| R7 | Interface funcional | `app/streamlit_app.py` | 🟡 só com dados falsos; se a API falha, a tela para | Miguel | `grep -n "USAR_DADOS_FALSOS =" app/streamlit_app.py` → `True` | demo ao vivo de 6 min | MG4, MG6 |
| R8 | Código com boas práticas e agentic coding | `tests/`, `contratos.md`, `REGRAS-IA.md`, `CLAUDE.md`, PRs revisados | 🟡 CI, versões fixadas, config do pytest, `AGENTS.md` e modelo de PR entram no PR de padronização; falta "Como usamos IA" no README | todos (coordena Eduardo) | `gh pr list --state all` | PRs com checklist, CI verde, seção no README | ED0, ED2, ED6, ED8 |
| R9 | Arquitetura + Terraform ou contêiner | `infra/` só com `.gitkeep` | ⬜ | Miguel | `ls infra` | `Dockerfile`, `infra/main.tf`, diagrama, `terraform apply` na demo | MG2, MG3, MG5 |
| R10 | Governança e ética (viabilidade, limites, viés, confiabilidade, uso responsável) | validador; auditoria de dados que só aponta; aviso "não é recomendação de investimento" na tela; `REGRAS-IA.md` §6 | 🟡 falta o texto | Náthally + todos | `grep -n "investimento" app/streamlit_app.py` | seção do PDF, slide 16–18, métricas | NA5, ED8, MG4 |
| R11 | Valor de negócio e ROI | persona, roteiro, pitch e comparação de LLMs na branch `feat/metricas` | 🟡 falta `tempo_manual.csv` e a conta do ROI | Náthally | `git ls-tree -r --name-only origin/feat/metricas` | slide 00–03 com o tempo medido | NA1, NA3 |
| R12 | Métricas de sucesso | `casos_avaliacao.csv` com 10 casos na `feat/metricas`, fora do formato C4 (sem `cd_cvm`) | ⬜ | Náthally + Eduardo | colunas `id,empresa,setor,produto,objetivo_reuniao` | `resultados.csv`, `revisao.csv`, números no deck | NA2, ED5, ED7, NA4, ED11 |
| D1 | Repositório organizado | `main` organizada; o trabalho de 2 pessoas está em branches sem história em comum com a `main` | 🟡 | todos | `git merge-base origin/main origin/tratamento_dados` não imprime nada | GitHub | ED0, MA1, NA1, ED9 |
| D1b | README com arquitetura, pré-requisitos e como rodar | `README.md` | 🟡 faltam Docker/Terraform, versão do Python e "Como usamos IA" | Miguel (+ seções dos outros) | `README.md` | README | MG5, ED8, ED10 |
| D1c | Scripts de infraestrutura e notebooks | nada | ⬜ | Miguel, Marcos | — | `infra/`, `notebooks/` | MG2, MG3, MA4 |
| D2 | PDF: BPMN + justificativa técnica + ética e segurança | nada | ⬜ | Marcos monta; Eduardo e Náthally escrevem | — | `docs/documentacao.pdf` | MA6 (com MA5, ED8, NA5, MG5) |
| D3 | Deck (PDF ou PPTX) | nada | ⬜ | Náthally | — | deck | NA5, NA6 |
| D4 | Vídeo de backup da demo (dica do guia) | nada | ⬜ | Miguel | — | vídeo em 2 lugares | MG6, MG7 |
| D5 | 20 minutos cronometrados, todos falam | divisão de fala definida | 🟡 | Náthally coordena | — | ensaios de 14–15/11 | NA6 |

## Diagnóstico de 27/10 (foto do dia; não precisa atualizar)

### Branches

| branch | situação em 27/10 | o que fazer |
|---|---|---|
| `eduardo` | toda contida na `main` (0 commits à frente) | pode apagar |
| `fundacao` | entrou pelo PR #2 | pode apagar |
| `tratamento_dados` (Marcos) | sem história em comum com a `main`; código de 27/10 mais novo que o da `main` | portar para a estrutura da `main` (sessão MA1) |
| `feat/metricas` (Náthally) | sem história em comum com a `main` | portar para `docs/produto/` e `avaliacao/` (sessão NA1) |

Prova: `git rev-list --left-right --count origin/main...origin/<branch>` e `git merge-base origin/main origin/<branch>`.

### Riscos encontrados

| risco | situação | prova |
|---|---|---|
| Chave ou `.env` no Git | nenhum encontrado em todo o histórico | `git log --all -p \| grep -c AIza` → 0 |
| Arquivos grandes na `tratamento_dados` | não existem mais: o maior objeto do histórico tem cerca de 10 KB | `git rev-list --objects origin/tratamento_dados \| git cat-file --batch-check` |
| Formato do CSV (C2) | `indicadores.csv` e `contas.csv` são gravados com `;` e lidos com `,` → 1 coluna só | `grep -n to_csv scripts/*.py` e `grep -n read_csv raiox/segmentos.py raiox/checagem.py` |
| `cd_cvm` como texto (C1/C2) | o contrato pede int | `grep -n "str(codigo)" raiox/dados.py` |
| Casos de avaliação (C4) | sem `cd_cvm`, o `montar()` não acha a empresa | `raiox/ia.py`, função `montar()` |
| Regras v1 × prompt v3 | 7 diferenças (marcadores com chave simples, "em linha", 2–4 × 2–3 frases, entre outras) | `docs/seguindo-o-projeto.md`, item 7 |
| Teste do C3 | usa a empresa falsa 90001 e quebra com dados reais | `grep -n 90001 tests/test_raio_x.py` |
| Dependências sem versão | um `pip install` novo pode trazer outra versão do LangChain | `requirements.txt` antes do PR de padronização |
| Tela sem plano B | se a API falha, mostra erro e para | `app/streamlit_app.py`, bloco `except` do botão "Gerar" |
| Código duplicado | modelo do Gemini definido em `raiox/ia.py` e `raiox/checagem.py`; filtro "ÚLTIMO + maior versão" em 2 scripts | `grep -n "MODELO =" raiox/*.py` |
| Infraestrutura | nada começado | `ls infra` |

### Divergências entre o artefato de 21/10, o guia e o código

| tema | artefato | guia | código | o que vale |
|---|---|---|---|---|
| Terraform | Docker **e** Terraform no mínimo | "Terraform **ou** conteinerização" | nada | Docker obrigatório; Terraform fino (provider docker) se o Docker estiver pronto até 03/11 |
| Pastas | `app.py` e `ia.py` na raiz, `src/dados.py`, `prompts/` | — | `raiox/`, `app/`, `avaliacao/regras_prompt.md` | o código (PR #2 aprovado) |
| Formato do `indicadores.csv` | não define | — | `;` e vírgula | CSV padrão (vírgula, ponto, UTF-8), escrito no C2 |
| Casos de avaliação | 20 | — | 10 | mínimo 10 bem revisados; 20 se sobrar tempo |
| Data da banca | semana de 09–15/11 | 48 h antes da banca | — | prevista qua 18/11, **a confirmar**; entrega seg 16/11 |
| RAG, agentes, memória | fora | pede RAG **ou** agentes **ou** prompt engineering + LangChain + API | chain simples | manter, com justificativa no PDF |
| Plano B da IA | não fala | — | a tela para no erro | a tela volta sozinha para o modo sem IA, com aviso (MG4) |
