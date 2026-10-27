# Plano até a banca (versão acelerada)

Versão de **ter 27/10/2026, noite**. Meta: **feito, não perfeito**. O código congela na **sex 06/11** e tudo fica pronto
para entregar na **qua 11/11**, com folga até a entrega de seg 16/11. Se a banca cair na semana de 09–15/11, já estamos prontos.

A matriz do que o guia exige está em [REQUISITOS.md](REQUISITOS.md). Os detalhes técnicos do que estava quebrado, com
comandos de prova, estão em [aprender/seguindo-o-projeto.md](../aprender/seguindo-o-projeto.md).

**Como usar este plano:**
- Cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (por exemplo, MA2).
- Para começar, abra o Claude Code (ou o Codex) e diga:
  > Leia o CLAUDE.md e faça a sessão MA2 do docs/PLANO.md.
- **Ao terminar uma sessão:**
  1. atualize a seção 0 (situação atual) e a coluna "status" da sessão, no mesmo PR;
  2. se a sessão fecha uma linha do REQUISITOS.md, atualize essa linha também.

**Hipóteses deste plano:**
- Cada pessoa tem de 6 a 12 h por semana, fora a aula.
- Eduardo e Marcos usam Claude Code. O Miguel usa Codex ou Claude Code. A Náthally não usa IA para programar: ela sobe arquivos pelo navegador.
- Banca prevista para **qua 18/11 (a confirmar)**.

---

## 0. Situação atual (atualize a cada sessão)

**Em 27/10, noite:**

| PR | o que traz | quem revisa | ordem de merge |
|---|---|---|---|
| [#3](https://github.com/MiguelGrispan/trabalho-tcs/pull/3) `eduardo-padronizacao` | este plano, REQUISITOS, CLAUDE/AGENTS/REGRAS-IA, contratos (CSV padrão, `cd_cvm` int), versões fixas, `pytest.ini`, CI, modelo de PR | Miguel (CI), Marcos (contratos) | **1º**: o CI só existe a partir dele |
| [#4](https://github.com/MiguelGrispan/trabalho-tcs/pull/4) `marcos-porta-dados` | MA1: o código de dados do Marcos (27/10) na estrutura da `main`, 28 testes dele | Marcos | depois do #3 (`git merge main` antes) |
| [#5](https://github.com/MiguelGrispan/trabalho-tcs/pull/5) `nathally-produto` | NA1 (parte 1): `docs/produto/`, regras v1, 10 casos no formato C4 (`cd_cvm` vazio) | Náthally | depois do #3 |
| [#6](https://github.com/MiguelGrispan/trabalho-tcs/pull/6) `eduardo-ia-testes` | ED2, ED5, código do ED4, ED6: testes sem `data/`, `avaliar.py`, gráfico dos grupos, teste ponta a ponta | Marcos, Miguel | depois do #3 |

**Testes:**
- Na `main` hoje: 8.
- Com os PRs #3, #4 e #6 juntos (simulado numa cópia em 27/10): 47 passam, mais 4 pulados que esperam os dados reais.

**Para quem está aprendendo:** a pasta [aprender/](../aprender/README.md) reúne os comandos (o que rodar, em qual pasta),
os guias e o notebook `passo_a_passo.ipynb`, que segue uma empresa do começo ao fim. Nada nela é usado pelo código.

**Dados reais (ED1, 27/10):**
- **Carga:** os scripts da branch do #4 rodaram em 22 s e geraram 595 empresas, todas com DFP 2025.
- **Conferência:** a receita da WEG bate com a conferência do Marcos.
- **Formato:** o `indicadores.csv` saiu com `;` e vírgula decimal. O Eduardo converteu só na `data/` dele, e com isso `tests/test_ponta_a_ponta.py` passa.
- **Raio-x:** 3 gerados com IA (Camil, Magazine Luiza, WEG), sem nenhum item removido pelo validador, por US$ 0,0026 no total. Estão em `data/ed1/` (fora do Git) e já foram enviados à Náthally.
- **Problema achado (ED4):**
  - com os dados reais, o K-means escolhe k = 4 com silhueta 0,77, mas um grupo tem 567 das 595 empresas e os outros têm 9, 9 e 10;
  - a silhueta alta só mede a separação das empresas extremas (margens de −10.000%);
  - com isso, o "grupo" vira quase todas as empresas, e as "parecidas" não fazem sentido.
- **Conserto testado:** tirar as empresas com receita abaixo de R$ 10 mi e cortar os extremos em 5/95 dá k = 4 com grupos de 330, 99, 74 e 59 empresas (silhueta 0,30). Detalhes na linha do ED4.

**Próximo passo de cada um:**
- **Miguel:** MG1 (revisar e mesclar o #3; configurar o GitHub).
- **Marcos:** revisar o #4 e começar a MA2. Na MA3, decidir o corte de receita mínima junto com o Eduardo.
- **Náthally:** revisar o #5 e escrever as regras v2, usando as notas no fim de `data/ed1/raiox_para_nathally.md`.
- **Eduardo:** ED4 (consertar a segmentação), adiantado para qua 28/10.

**Decisões em aberto:**
- data e horário da banca;
- `scripts/dados.py` duplicado (Marcos decide, no #4);
- apagar as branches `eduardo` e `fundacao`, que já estão na `main`.

---

## 1. Fundação: arquivos iguais para todos

Todos entram no PR #3, menos os da última linha.

| arquivo | conteúdo mínimo | por quê |
|---|---|---|
| `docs/REQUISITOS.md`, `docs/PLANO.md` | a matriz do guia e este plano | um só lugar para "o que falta" e "quem faz quando" |
| `aprender/` | `COMANDOS.md`, guias, notebook passo a passo, atalhos do Mac | o que só serve para aprender fica numa pasta só, que o Docker pode ignorar inteira |
| `CLAUDE.md` | data da banca, leitura do PLANO, regras de Git e de testes | o Claude Code lê em toda sessão |
| `AGENTS.md` | aponta para CLAUDE.md, REGRAS-IA.md e contratos.md | o Codex lê `AGENTS.md`, não `CLAUDE.md` |
| `REGRAS-IA.md` | §5 Git: branch curta por tarefa, `merge` em vez de `rebase`, PR pelo navegador | as branches pessoais longas criaram duas histórias separadas |
| `contratos.md` | C2: CSV padrão e `cd_cvm` int; C3: fonte igual ao código; C4: casos com `cd_cvm` e `empresa` | contrato antes de código |
| `requirements.txt` | versões fixas (`==`), Python 3.14 | um build novo do Docker não pode trazer outro LangChain |
| `pytest.ini` | `testpaths = tests`, `pythonpath = .` | todos e o CI rodam os testes do mesmo jeito |
| `.gitignore` | `*.db`, `*.zip`, `*.parquet`, `myenv/` | banco ou zip fora de `data/` não entra por engano |
| `.github/workflows/testes.yml` | testes em todo PR e em todo push na `main` | nada entra com teste falhando |
| `.github/pull_request_template.md` | checklist do REGRAS-IA e "Feito com IA / Eu conferi" | a regra vira automática |
| `Dockerfile`, `.dockerignore`, `infra/` | Miguel, sessões MG2 e MG3 | dono da infra |

---

## 2. Git

| tema | combinado | por que, e não a alternativa óbvia |
|---|---|---|
| Modelo | `main` + **uma branch curta por sessão**, com nome `pessoa-tarefa` (ex.: `marcos-csv-padrao`) | branch pessoal longa acumula diferença e vira PR gigante. Hífen, não barra: o Git não deixa criar `eduardo/...` enquanto existir a branch `eduardo` |
| Criar a branch | `git switch main` → `git pull` → `git switch -c pessoa-tarefa` | sempre a partir da `main` atual |
| Quando abrir PR | quando o "pronto quando" da sessão passa e `python -m pytest -q` está verde | PR pequeno é revisado no mesmo dia |
| Quem revisa | quem **recebe** o contrato. Marcos → Eduardo (e Miguel, se mexer no C1). Eduardo → Marcos (e Miguel, se mexer no C3). Miguel → Eduardo. Náthally → Eduardo | quem recebe percebe quando quebra |
| Quem faz o merge | o autor, depois de 1 aprovação e com o CI verde | tira o Miguel do gargalo |
| Tipo de merge | **merge commit**. O Miguel desliga squash e rebase e liga "apagar branch após o merge" | guarda os commits pequenos (prova do processo para a banca) e não quebra quem continua na branch |
| Proteção da `main` | o PR #3 aparece como "review required": a `main` já parece exigir revisão. Na MG1, o Miguel confirma e acrescenta o check `testes` como obrigatório, se der | — |
| Trazer a `main` | `git switch main` → `git pull` → `git switch pessoa-tarefa` → `git merge main` → `python -m pytest -q` → `git push`. Conflito: `git merge --abort` e fale com o dono do arquivo | o `rebase` exige `push --force`, o jeito mais comum de apagar trabalho do colega |
| Tags | `v0.1-demo` na **ter 03/11** e `v1.0` na **sex 06/11**. Depois, só `v1.0.1`… com consertos. Quem cria é o Eduardo: `git tag -a v1.0 -m "versão da banca"` e `git push origin v1.0` | avaliação final, vídeo e teste do zero rodam na mesma versão |
| Arquivo comum (`README`, `contratos`, `requirements`, `tests/`, `docs/`) | um PR por vez; avise no grupo | evita conflito |

---

## 3. Sessões, em ordem, por pessoa

**Regras de sessão** (Claude Code; quem usa Codex segue o mesmo pelo `AGENTS.md`):
- **Uma sessão = uma linha abaixo = uma branch = um PR.**
- **Modo Plan** para mais de um arquivo, para contrato ou para arquivo comum. **Manual** para um arquivo só, ou quando você mesmo escreve o código.
- No Codex, comece com: "proponha um plano, não altere arquivos".
- **Sessão nova** para cada tarefa.
- **`/clear`**:
  - depois do commit e do PR;
  - quando a conversa muda de assunto;
  - quando o Claude começa a esquecer as instruções do início.
  - Nunca use `/clear` com mudança sem commit: anote antes onde parou.
- **Fim de toda sessão:** `python -m pytest -q` → `git status` (leia a lista) → commit → push → PR → atualizar a seção 0.

### Calendário

| data | Eduardo | Marcos | Miguel | Náthally |
|---|---|---|---|---|
| ter 27/10 | ✅ ED0, ED1, ED2, ED5, ED4 (código), ED6; portes MA1 e NA1 | — | — | — |
| qua 28/10 | ED4 consertar a segmentação | revisar o #4; MA2 | MG1 revisar e mesclar o #3 | revisar o #5; NA1 regras v2 |
| qui 29/10 | revisões | MA2 cumprir C1/C2 | MG2 Docker | NA1 |
| sex 30/10 | ED3 regras v2 no prompt | MA3 dados reais + Drive | MG2/MG3 | NA2 `cd_cvm` dos casos |
| sáb 31/10 | revisões; ED8 começa | MA3 | MG3 Terraform | NA3 tempo manual; marcar testes |
| dom 01/11 | ED7 rodada com IA | MA4 EDA | **MG3: se o Terraform não subiu, fica só o Docker**; MG4 | NA3 |
| seg 02/11 | feriado (reserva) | | | |
| ter 03/11 | **demo ponta a ponta · tag `v0.1-demo`** | MA4 | MG4 tela com dados reais | NA3 testes com usuários |
| qua 04/11 | ED8 justificativa + "Como usamos IA" | MA5 BPMN | MG5 arquitetura + README | NA4 revisão + métricas |
| qui 05/11 | só bugs | MA5 | MG6 vídeo v0 | NA3 (3 testes feitos) |
| sex 06/11 | **ED9: código congelado · tag `v1.0`**; ED11 avaliação final | | | |
| sáb 07/11 | ED10 teste do zero | MA6 PDF (rascunho) | MG7 vídeo final na `v1.0` | NA5 ética |
| dom 08/11 | **todos mandam o conteúdo dos slides à Náthally** | | | NA5 deck |
| seg 09/11 | | MA6 PDF final | | NA6 deck final |
| ter 10/11 | **ensaio 1 (20 min, todos)** | | | |
| qua 11/11 | **ensaio 2; tudo pronto para entregar** | | | |
| 12–15/11 | reserva (e prontos, se a banca vier antes) | | | |
| seg 16/11 | **entrega** (48 h antes de qua 18/11) | | | |

### Eduardo (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| ED0 | 27/10 | ✅ PR #3 | arquivos comuns, PLANO, REQUISITOS | seção 1 | Plan | PR aberto | `eduardo-padronizacao` |
| ED1 | 27/10 | ✅ `data/ed1/` | 3 raio-x reais para a Náthally: roda os scripts do Marcos (branch do #4) e converte o CSV só na sua `data/` | nada no Git | Manual | 3 empresas de setores diferentes, `removidos` conferido, enviado | nenhum |
| ED2 | 27/10 | ✅ PR #6 | testes sem depender de `data/` (`RAIOX_DADOS`); "balanço consolidado" | `raiox/`, `tests/` | — | 17 passam | `eduardo-ia-testes` |
| ED3 | sex 30/10 | — | regras v2 da Náthally no `REGRAS` | `raiox/ia.py` | Manual | 3 chamadas reais sem item removido por dígito | PR (Náthally lê) |
| ED4 | qua 28/10 | 🟡 código no #6; problema achado no ED1 | consertar a segmentação real: receita mínima de R$ 10 mi (combinar com o Marcos) e corte dos extremos em 5/95 em `matriz()`; só aceitar o k cujo menor grupo tenha pelo menos 5% das empresas; teste novo para isso; olhar 2 grupos; explicar `matriz()` e o PCA. Os gráficos de antes estão em `data/ed1/*_antes_ed4.png` e servem para a banca ("a silhueta alta enganava") | `raiox/segmentos.py`, `tests/`, `docs/graficos/*.png`, REQUISITOS (k, silhueta) | Plan | nenhum grupo com menos de 5% das empresas; "parecidas" de 3 empresas conhecidas fazem sentido; 2 PNG reais | PR |
| ED5 | 27/10 | ✅ PR #6 | `avaliacao/avaliar.py` (C4) | `avaliacao/`, `tests/` | — | `python -m avaliacao.avaliar` grava o C4 | `eduardo-ia-testes` |
| ED6 | 27/10 | ✅ PR #6 | teste ponta a ponta (pula sem `data/`) | `tests/test_ponta_a_ponta.py` | — | pula no CI; roda local com dados reais | `eduardo-ia-testes` |
| ED7 | dom 01/11 | — | `python -m avaliacao.avaliar --com-ia` nos 10 casos (avisar o grupo) | `avaliacao/resultados.csv` | Manual | 10 linhas; custo anotado (< US$ 0,05) | PR |
| ED8 | qua 04/11 | — | justificativa técnica para o PDF + README "Como usamos IA" | `docs/justificativa.md`, `README.md` | Manual (você escreve; a IA confere com arquivo e linha) | o Marcos lê e entende | PR |
| ED9 | sex 06/11 | — | congelar | só bugs | Plan | CI verde + ponta a ponta verde | **tag `v1.0`** |
| ED10 | sáb 07/11 | — | teste do zero em outra máquina, só com o README | consertos | Manual | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisar |
| ED11 | sex 06/11 | — | avaliação final na `v1.0` (só se a IA mudou depois do ED7) + ensaio de defesa | `resultados.csv` | Plan | 10 perguntas da banca respondidas sem consulta | PR |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ porte no PR #4 (feito pelo Eduardo) | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qua 28–qui 29/10 | — | cumprir C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `tests/test_contratos.py` | Plan | `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-csv-padrao` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 | — | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | — | montar o `documentacao.pdf` | `docs/documentacao.pdf` | fora do Claude | BPMN + justificativa + ética + arquitetura | PR |

### Miguel (Codex hoje; Claude Code se migrar)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | — | revisar e mesclar o #3; configurar o GitHub (só merge commit, apagar branch, check `testes`); rodar a tela local | configurações | só leitura | #3 na `main`; print da tela no grupo | merge do #3 |
| MG2 | qui 29–sex 30/10 | — | `Dockerfile` + `.dockerignore` (tela, `data/` como volume, chave por variável) | `Dockerfile`, `.dockerignore` | Plan | `docker build`, `docker run -p 8501:8501 …`, `curl localhost:8501/_stcore/health` → `ok` | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | — | Terraform (provider docker), **só se o Docker estiver pronto**. Prazo: dom 01/11; senão, corta | `infra/` | Plan | `terraform apply` sobe; `destroy` + `apply` mantém `data/` | PR |
| MG4 | dom 01–ter 03/11 | — | tela com dados reais: `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`; volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner | PR (Eduardo) |
| MG5 | qua 04/11 | — | diagrama de arquitetura + README (pré-requisitos com Python 3.14; rodar local, Docker e Terraform) | `docs/arquitetura.png`, `README.md` | Manual | um colega entende o fluxo lendo o README | PR |
| MG6 | qui 05/11 | — | roteiro de 6 min da demo + vídeo v0 | — | — | vídeo salvo em 2 lugares | — |
| MG7 | sáb 07/11 | — | vídeo final na `v1.0` | — | — | vídeo salvo em 2 lugares | — |

### Náthally (sem IA de código: GitHub pelo navegador)

Para subir um arquivo:
1. No GitHub, "Add file → Upload files".
2. Escolha "Create a new branch" (`nathally-tarefa`).
3. Abra o PR. O Eduardo revisa.

| # | data | status | objetivo | altera | pronto quando |
|---|---|---|---|---|---|
| NA1 | qua 28–qui 29/10 | 🟡 porte no PR #5 | revisar o #5; regras v2 alinhadas ao código (`aprender/seguindo-o-projeto.md`, item 7) | `avaliacao/regras_prompt.md` | PR aberto |
| NA2 | sex 30/10 | — | preencher o `cd_cvm` dos 10 casos (busca da tela ou `indicadores.csv` do Drive; WEG = 5410) | `avaliacao/casos_avaliacao.csv` | `tests/test_ponta_a_ponta.py` passa (o Eduardo roda) |
| NA3 | sáb 31/10–qui 05/11 | — | `tempo_manual.csv` (3 empresas), 3 testes com usuários (sem nome), conta do ROI | `avaliacao/` | 3 testes feitos; ROI com números medidos |
| NA4 | qua 04/11 | — | `revisao.csv` sobre o `resultados.csv`; métricas | `avaliacao/revisao.csv`, `docs/produto/metricas.md` | % de comparações certas, % de perguntas ligadas ao produto, utilidade, custo, tempo |
| NA5 | sáb 07–dom 08/11 | — | texto de governança e ética; deck com o tempo de cada parte | `docs/etica.md`, deck | o Marcos recebe a ética; todos os slides chegaram |
| NA6 | seg 09–qua 11/11 | — | deck final; 2 ensaios cronometrados | deck | ensaio abaixo de 20 min |

---

## 4. Testes

**Regra:**
- Toda mudança de comportamento vem com um teste novo ou atualizado, no mesmo PR.
- Rode `python -m pytest -q` antes de cada commit e antes de cada PR.
- O CI roda em todo PR, e ninguém aprova PR com CI vermelho.
- Nenhum teste chama a API do Gemini.

| arquivo | o que testa | dono | roda no CI? |
|---|---|---|---|
| `tests/conftest.py` | todo teste usa a tabela falsa (`RAIOX_DADOS=falsos`) e nada grava em `data/` | Eduardo | sim |
| `tests/test_raio_x.py` | validador (regra de ouro), contrato C3, fonte, modo sem IA nas 30 empresas falsas, `RAIOX_DADOS`, segmentação (k = 3, 29 de 30), gráficos, checador | Eduardo | sim |
| `tests/test_avaliar.py` | `avaliar.py`: colunas do C4, casos válidos, caso com erro, formato do `casos_avaliacao.csv` | Eduardo | sim |
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py` (PR #4) | regras de limpeza, carga da DFP (rede simulada), catálogo SQLite e C1 | Marcos | sim |
| `tests/test_contratos.py` (MA2) | C1 e C2 com os falsos: CSV padrão, `cd_cvm` int | Marcos | sim |
| `tests/test_tela.py` (MG4) | a tela com os falsos: busca, gerar, 6 métricas, sem erro | Miguel | sim |
| `tests/test_ponta_a_ponta.py` | C2 real, raio-x sem IA de 3 setores, `cd_cvm` dos casos | Eduardo | **não**: pula sem `data/`. Rodar local antes de `v0.1-demo`, `v1.0` e no teste do zero |
| `tests/test_aprender.py` | o notebook `aprender/passo_a_passo.ipynb` roda inteiro e vai para o Git sem saídas | Eduardo | sim |
| Docker | `curl localhost:8501/_stcore/health` → `ok` | Miguel | não (checklist da demo) |

---

## 5. Pontos de integração

| data | quem | o que sincroniza | o que congela |
|---|---|---|---|
| qua 28/10 | Miguel → todos | #3 na `main`; os outros PRs fazem `git merge main` | arquivos de padronização |
| qua 28/10 | Eduardo → Náthally | 3 raio-x reais | — |
| qui 29/10 | Marcos → Eduardo | C2 cumprido (MA2) | formato e colunas do C2 |
| sex 30/10 | Marcos → todos | `data/` v1 no Drive | — |
| sex 30/10 | Náthally → Eduardo | regras v2; casos com `cd_cvm` | texto das regras e formato do C4 |
| dom 01/11 | Miguel | decisão: Terraform ou só Docker | infra |
| ter 03/11 | os 4 | demo ponta a ponta; tag `v0.1-demo` | **interfaces** (C1, C3, `RAIOX_DADOS`) e escopo: nada novo |
| sex 06/11 | os 4 | tag `v1.0` | código |
| dom 08/11 | todos → Náthally | conteúdo dos slides | roteiro |
| qua 11/11 | os 4 | tudo pronto para entregar | entregáveis |

**Como os dados chegam a cada um:**
- O Marcos publica um zip da pasta `data/` no Drive na sex 30/10 e na sex 06/11.
- Os scripts continuam reproduzíveis, para o teste do zero.
- **Por que não cada um rodar os scripts:** multiplica os pontos de falha.
- **Por que não pôr no Git:** quebra a regra 5 do CLAUDE.md.

---

## 6. Mapa requisito → sessão

| requisito ([REQUISITOS.md](REQUISITOS.md)) | sessões |
|---|---|
| R1 BPMN | MA5, MA6 |
| R2 Pandas | MA1, MA2, MA3 |
| R3 SQL | MA2, MG4 |
| R4 Visualização | MA4, ED4, MG4 |
| R5 ML | ED4 |
| R6 GenAI | ED1, ED3, ED7 |
| R6b RAG × fine-tuning | ED8, ED11 |
| R7 Interface | MG4, MG6 |
| R8 Boas práticas e agentic coding | ED0, ED2, ED6, ED8, todos os PRs |
| R9 Arquitetura e infra | MG2, MG3, MG5 |
| R10 Governança e ética | NA5, ED8, MG4 |
| R11 ROI | NA1, NA3 |
| R12 Métricas | NA2, ED5, ED7, NA4, ED11 |
| D1 Repositório | ED0, MA1, NA1, ED9 |
| D1b README | MG5, ED8, ED10 |
| D1c Infra e notebooks | MG2, MG3, MA4 |
| D2 PDF | MA6 (com MA5, ED8, NA5, MG5) |
| D3 Deck | NA5, NA6 |
| D4 Vídeo | MG6, MG7 |
| D5 20 minutos | NA6 + ensaios de 10–11/11 |

---

## 7. Riscos, plano B e o que cortar

| marco | risco | plano B |
|---|---|---|
| qua 28/10 | o `carregar_dfp.py` não roda na máquina do Eduardo | o Marcos manda a `data/` dele; em último caso, 3 raio-x com a tabela falsa |
| qui 29/10 | a MA2 atrasa | o Eduardo converte o CSV localmente e segue; a MA2 entra até ter 03/11 |
| dom 01/11 | o Terraform não sobe | fica só o Docker (o guia aceita "Terraform ou conteinerização") |
| ter 03/11 | a demo não roda inteira | qua e qui 04–05/11 só para isso; o vídeo vira obrigatório; demo por `docker run` ou `streamlit run` local |
| dia da banca | a API falha ou o crédito acaba (erro 402) | a tela volta sozinha para o modo sem IA, com aviso (MG4); vídeo; saldo conferido em 08/11 |
| qualquer dia | a banca é **antes** | o código já congela em 06/11 e os entregáveis ficam prontos em 11/11 |
| qualquer dia | alguém fica indisponível | duplas de reserva: Marcos ↔ Eduardo (dados), Miguel ↔ Eduardo (infra), Náthally ↔ Marcos (deck e PDF) |
| qui 29/10 | o Miguel não abriu o PR do Docker | o Eduardo faz o Dockerfile e o Miguel revisa (dupla de reserva) |

**Já fora:**
- `verificar_automatico.py` (yfinance) e `graficos.py`;
- receita em 3 anos;
- filtro de setor;
- RAG, nome dos grupos pelo LLM, exportar o raio-x, número de empregados;
- refatorar as duplicações;
- 20 casos (ficam 10);
- conferência da Náthally no RI (fica a do Marcos, com 5 empresas).

**Se faltar tempo, cortar nesta ordem:**
1. Terraform
2. BPMN "hoje"
3. testes com usuários de 3 para 2
4. ED11 (fica o resultado do ED7)

---

## 8. Sessões do Eduardo: o que ele precisa saber explicar

O código do ED2, do ED5 e do ED4 foi escrito pela IA em 27/10, para adiantar o projeto.
Antes da banca, o Eduardo explica em voz alta, sem olhar, cada um destes pontos. Se não conseguir, pede "explique para iniciante" e tenta de novo.

| arquivo e função | o que explicar |
|---|---|
| `raiox/segmentos.py`, `matriz()` | por que a receita entra em log, por que cortar extremos, por que a mediana nos nulos, o que o `StandardScaler` faz |
| `raiox/segmentos.py`, `segmentar()` | K-means, silhueta, por que k vai de 3 a 8, `NearestNeighbors` com 6 vizinhos |
| `raiox/segmentos.py`, `grafico_grupos()` | o que o PCA faz e o que significa "61% da variação" |
| `raiox/ia.py`, `montar()` | o que vai para o LLM e o que nunca vai (`valores`) |
| `raiox/ia.py`, `validar_e_preencher()` | por que a IA não consegue escrever número na tela |
| `avaliacao/avaliar.py`, `avaliar()` | o laço, por que um erro não para a rodada, as colunas do C4 |
| `tests/conftest.py` | por que todo teste usa a tabela falsa |

**Método:** ler o trecho → prever o resultado → rodar → só então pedir "explique".

---

## Se começássemos do zero (para aprender, não para refazer)

1. **Matriz do guia com dono** no dia 1, antes de qualquer código.
2. **Contratos com o formato do arquivo** e falsos no mesmo formato. Os bugs do CSV com `;` e do `cd_cvm` como texto são de contrato.
3. **Repositório-esqueleto** feito por uma pessoa, de onde todos clonam, com CI e versões fixas desde o início.
4. **Docker "olá mundo"** na primeira semana.
5. **Cada um trabalhando contra os falsos**, com integração semanal e tag.
