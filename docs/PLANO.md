# Plano até a banca (versão acelerada)

Meta: **feito, não perfeito**. O código congela na **sex 06/11** e tudo fica pronto para entregar na **qua 11/11**, com folga
até a entrega de **seg 16/11** (banca prevista para qua 18/11, a confirmar). Se a banca vier antes, já estamos prontos.

**Onde está cada coisa:** o que fazer agora → seção 0; quem faz o quê e quando → seção 3; o que o guia exige e o status de
cada item → [REQUISITOS.md](REQUISITOS.md); o que já aconteceu → [HISTORICO.md](HISTORICO.md).

**Como usar:** cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (ex.: MA2). No Claude Code, comece
com `/inicio-de-sessao MA2` e termine com `/fim-de-sessao`: ele faz o Git, atualiza a seção 0, o REQUISITOS e o HISTORICO,
abre o PR, espera o CI e faz o merge depois do seu "pode". Guia: [aprender/claude-code.md](../aprender/claude-code.md).

**Hipóteses:** cada pessoa tem de 6 a 12 h por semana, fora a aula. Eduardo, Marcos e Miguel usam o Claude Code;
a Náthally não programa com IA e sobe arquivos pelo navegador do GitHub (seção 3).

---

## 0. Situação atual (o `/fim-de-sessao` reescreve esta seção e apaga o que ficou velho)

**Em sex 30/10, 9h.** Na `main`: PRs #1 a #16 e #19 a #22. **O PostgreSQL está na `main`** (MA2: PR #21 do Marcos e PR #22).
Com a `data/` real e o PostgreSQL local: 86 passed, nenhum pulado. O CI agora também roda os testes do banco (#22).

**MA2, conferida pelo Eduardo em 30/10:**
- **PR #21 (Marcos, 29/10, 17h52):** `raiox/banco.py` abre a conexão (`DATABASE_URL`; sem ela, `postgres:postgres@localhost:5432/raiox`),
  o `scripts/carregar_dfp.py` grava as tabelas `contas` e `empresas` e o `raiox/dados.py` busca com `ILIKE`. Carga real em 44 s:
  384.561 linhas de contas, 2.567 empresas (660 ativas); a busca "weg" acha a WEG (5410). Entrou com a descrição do PR em branco.
- **PR #22 (Eduardo, plano B da seção 7, com o ok do Marcos):** o CI sobe um `postgres:17` (`.github/workflows/testes.yml`); antes,
  os 17 testes do banco eram pulados e o CI ficava verde mesmo assim. O `contas.csv` e o `indicadores.csv` saem em CSV padrão e o
  `cd_cvm` sai como int (`scripts/indicadores.py`, `scripts/carregar_dfp.py`): antes, numa máquina nova o raio-x quebrava
  (`tests/test_ponta_a_ponta.py`, 3 falhas). Teste novo: `test_calcular_grava_csv_padrao_com_cd_cvm_inteiro`.
  Os números são os de antes, menos Padtec (18414) e Elea Digital (26948), que ganharam a correção de escala ×1000 do #21.
- **Quem tem a `data/` anterior a 30/10:** rodar de novo `python scripts/carregar_dfp.py` e `python scripts/indicadores.py`.
- **PostgreSQL local, como o Eduardo subiu (Docker):** usuário e senha `postgres`, porta 5432, que é o endereço padrão do código
  (não precisa de `DATABASE_URL` no `.env`):
  `docker run -d --name raiox-postgres --restart unless-stopped -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=raiox -p 5432:5432 -v raiox-postgres-dados:/var/lib/postgresql/data postgres:17`
  e depois `docker exec raiox-postgres psql -U postgres -c "CREATE DATABASE raiox_teste"`. O `docker-compose.yml` da MG2 substitui isso.

**Onde está cada frente:**
- **Dados (Marcos):** o que sobrou da MA2 (contratos C1 e C2), sem teste ainda:
  1. `raiox/dados.py` devolve o `cd_cvm` como texto (`'5410'`); o C1 pede int;
  2. a busca não filtra as companhias ativas (`grep -n situacao raiox/dados.py` não acha nada); o C1 pede "só ativas";
  3. não existe a tabela `indicadores` no banco; o C2 pede.

  Voltaram no #21, mesmo cortados (seção 7): `scripts/verificar_automatico.py` (com o `yfinance` no `requirements.txt` e
  `tests/test_verificar_automatico.py`) e `scripts/graficos.py`. Entrou também um `docs/Raio-X Comercial.pdf` (26 páginas,
  impresso do Chrome; não abri). O `scripts/avaliar_corte_receita.py` (na `main` desde o #21) roda com os dados reais:
  abaixo de R$ 10 mi, 31 empresas, 52% com |margem EBIT| > 100%; acima, 564 e 4%. Falta o OK do Marcos no corte.
- **Issue #17 (Náthally, 29/10):** a Camil tem ano fiscal de março a fevereiro, e, segundo ela, o raio-x trata a DFP encerrada
  em 28/02/2025 como se fosse a de 2025. A ED7 reforça: 4 dos 6 indicadores da Camil diferem da conferência manual dela
  (receita R$ 12,3 bi × 11,1 bi; crescimento +20% × −1,2%). Não conferi o código. É dos dados (Marcos, MA3).
- **Conferência manual da Náthally (29/10):** o `Semana_02/revisao_manual.md`, na `feat/metricas` (sem commit novo desde 29/10,
  16h38), tem os 6 indicadores das 10 empresas tirados do RI, com links. Contra a ED7, batem 7 de 10. Diferem: Camil (issue #17),
  Magalu (margem EBIT 5,0% × 5,81%) e RD Saúde (margem EBIT 6,2% × 5,27%, endividamento 70,9% × 62,4%, ativo R$ 25,2 bi × 20,6 bi;
  suponho, sem conferir, que a fonte dela tire o arrendamento). Serve à MA3. Ela precisa subi-lo numa branch nova (seção 3).
- **IA (Eduardo):** ED7 feita (PR #20). Próxima: ED8 (qua 04/11).
- **Docker e Terraform (Miguel, MG2 e MG3):** na branch `docs-docker-e-terraform`, sem commit desde 28/10 e sem PR (o prazo era hoje).
  Funcionam (teste do Eduardo em 29/10). O Eduardo ensina o Claude Code ao Miguel hoje. Faltam 7 ajustes antes do PR:
  1. `git merge main` (a branch é anterior aos #7 a #22; sem isso, o diff parece apagar as skills, os gráficos e o PostgreSQL);
  2. `.dockerignore`: tirar a `data/` (hoje ela entra na imagem) e a `aprender/`. **Não** tirar a `avaliacao/`: com a IA ligada,
     o prompt lê `avaliacao/regras_prompt.md`;
  3. `Dockerfile`: `FROM python:3.14-slim`, a versão do CI (testado: funciona igual);
  4. `terraform/main.tf`: montar a `data/` como volume (`volumes { host_path = "<caminho>/data", container_path = "/app/data" }`)
     e passar `RAIOX_DADOS=real` (e `RAIOX_IA_REAL=1`, se a demo usar a IA). Hoje, depois de `destroy` + `apply`, a `data/` some;
  5. `terraform/variables.tf`: deixar a `google_api_key` opcional (hoje ela é pedida até para a demo sem IA);
  6. `.gitignore`: apagar a primeira linha (` ```gitignore `) e a última (` ``` `), sobra de cópia de um chat;
  7. README: avisar que a chave fica em texto puro no `terraform.tfstate` (o `.gitignore` já tira esse arquivo; não mandar para ninguém).

  Com o PostgreSQL, o Docker vira um `docker-compose.yml` com 2 contêineres (MG2): o banco igual ao do CI (`postgres:17`,
  usuário `postgres`) e a tela com `DATABASE_URL=postgresql://postgres:<senha>@<nome do serviço do banco>:5432/raiox`.
- **Tela (Miguel, MG4):** com `RAIOX_DADOS=real`, a tela já gera o raio-x de empresas reais, mas o aviso diz "empresas e números
  inventados", e se a API falha a tela para.
- **Produto (Náthally):** regras v2 (PR #11) e `cd_cvm` dos 10 casos (PR #10) na `main`. Ela ainda confere os 10 códigos.
- **GitHub (Miguel, MG1):** falta o check `testes` obrigatório, "Automatically delete head branches" e só "Allow merge commits".
  Sobram as branches antigas `tratamento_dados` (Marcos) e `feat/metricas` (Náthally).

**Caminho crítico** (o que trava os outros):
1. **PR do Docker com o `docker-compose.yml`** (Miguel; o prazo era hoje): a demo de ter 03/11, a MG3 e o teste do zero dependem dele.
   Se não vier até sáb 31/10, plano B (seção 7).
2. **MA3, os números certos** (Marcos): a Camil errada na demo é pior que nenhum raio-x.
3. **Trabalho fora da `main`:** toda entrega sai de uma branch nova a partir da `main` (seção 2); senão, alguém tem de portar à mão.

**Próximo passo de cada um:**
- **Marcos:** MA3: a issue #17 e as diferenças de Magalu e RD Saúde (acima), o OK, ou não, no corte de R$ 10 mi, e os 3 itens
  do C1 e do C2 que sobraram (acima), com teste. Dizer o que fazer com `verificar_automatico.py`, `graficos.py` e o PDF, e se a
  `tratamento_dados` pode ser apagada.
- **Miguel:** aprender o Claude Code com o Eduardo; `/inicio-de-sessao MG2`: os 7 ajustes e o `docker-compose.yml`; terminar a MG1.
- **Náthally:** subir o `revisao_manual.md` numa branch nova a partir da `main`, na pasta `avaliacao/`; conferir os 10 códigos
  em `avaliacao/casos_avaliacao.csv`; dizer se a `feat/metricas` pode ser apagada. Depois, NA3 (tempo manual e ROI); a NA4 já
  pode começar (o `resultados.csv` está na `main`). Para a v3 das regras (não trava nada): na ED7, 27 de 30 lacunas saíram
  genéricas e só 21 de 40 perguntas citam o produto ou o objetivo; vale dar exemplos de lacuna boa (quem decide, orçamento,
  fornecedor atual) e pedir o produto nas perguntas.
- **Eduardo, em ordem** (o Claude Code faz o Git):
  1. hoje: ensinar o Claude Code ao Miguel; mandar ao grupo a mensagem geral (fluxo `/inicio-de-sessao` e `/fim-de-sessao`,
     regra do PostgreSQL, ajustes do Docker, resultado da ED7). Em 30/10, só a mensagem ao Marcos sobre o #22 está confirmada;
  2. perguntar ao professor a data da banca e se há outras regras além do guia (anotar no REQUISITOS);
  3. sáb 31/10: se o PR do Docker não veio, plano B (seção 7); começar a ED8;
  4. ter 03/11: demo ponta a ponta com `docker compose` (tela + PostgreSQL + `data/` real) e tag `v0.1-demo`;
  5. no meio disso: `/explicar` nos pontos da seção 8.

**Pendências pequenas:**
- Eduardo: o `tests/test_aprender.py:19` exige exatamente "5 passed" no notebook.
- Marcos: `test_resolver_conflitos_trata_valor_vazio_como_divergente` (`tests/test_limpeza.py:147`) passa só pela ordem das linhas;
  `test_obter_indicadores_deixa_ausente_…` (`tests/test_dados.py:83`) não olha o `ativo_total`; `test_calcular_exporta_…` não tem
  receita de 2 anos antes igual a zero. (Os nomes ainda existem; não reli o corpo dos testes depois do #21.)
- O C4 (`contratos.md`) diz que o `avaliacao/conferencia.csv` é da Náthally, mas quem escreve é o Marcos (MA3): corrigir com o ok dos dois.

**Decisões em aberto:**
- data e horário da banca (Eduardo pergunta ao professor);
- `scripts/dados.py` ou `raiox/dados.py`: ficar com um só (os dois existem; Marcos);
- `verificar_automatico.py`, `yfinance` e `graficos.py`, cortados na seção 7 e de volta na `main` pelo #21 (Marcos e Eduardo);
- pasta da infraestrutura: `infra/` ou `terraform/` (Miguel, no PR do Docker);
- apagar `tratamento_dados` e `feat/metricas` (Marcos e Náthally);
- corte de receita mínima de R$ 10 mi (Marcos, MA3; números do `avaliar_corte_receita.py` acima);
- as 3 notas do código (`NOTAS_DO_CODIGO`, em `raiox/ia.py`) vão para a v3 das regras? (Náthally).

**Progresso estimado** (Eduardo, 30/10):

| parte | feito | falta |
|---|---|---|
| núcleo do produto: dados, ML, IA, validador, avaliação | ~88% | MA3 (Camil, Magalu, RD Saúde); `cd_cvm` int e só ativas no C1; tabela `indicadores` |
| tela e infraestrutura | ~35% | PR do Docker com `docker-compose.yml` e do Terraform (funcionam, sem PR); MG4 (aviso, modo sem IA automático) |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~10% | quase tudo, mas não depende de código novo |
| **total** | **~48%** | com 10 de 26 dias usados (~38%): o núcleo está adiantado; o Docker (Miguel) é o caminho crítico |

**Folga:** sobram 4 dias de reserva (12 a 15/11) antes da entrega de seg 16/11, e mais 2 até a banca.
Regra: atraso come a folga; **nunca** se acrescenta escopo. Se a folga acabar, use a lista de cortes da seção 7.

---

## 1. Fundação (feita no PR #3, 27/10)

Os arquivos comuns entraram no PR #3: `CLAUDE.md` (o Claude Code lê em toda sessão), `AGENTS.md` (o mesmo, para o Codex),
`REGRAS-IA.md`, `contratos.md`, `requirements.txt` com versões fixas (Python 3.14), `pytest.ini`, `.gitignore`, o CI
(`.github/workflows/testes.yml`: testes em todo PR e em todo push na `main`) e o modelo de PR. O porquê de cada decisão
está no [HISTORICO.md](HISTORICO.md), tabela de decisões.

---

## 2. Git

Quem usa o Claude Code não precisa decorar esta tabela: o `/inicio-de-sessao` e o `/fim-de-sessao` seguem estas regras.
Os comandos, um por um, estão em [aprender/COMANDOS.md](../aprender/COMANDOS.md), seção 7.

| tema | combinado | por quê |
|---|---|---|
| Modelo | `main` + **uma branch curta por sessão**, a partir da `main` atual, com nome `pessoa-tarefa` (ex.: `marcos-postgres`) | branch longa acumula diferença e vira PR gigante. Hífen, não barra: o Git não deixa criar `eduardo/...` enquanto existir a branch `eduardo` |
| Quando abrir PR | quando o "pronto quando" da sessão passa e `python -m pytest -q` está verde | PR pequeno é revisado no mesmo dia |
| Quem revisa | o CI (os testes) e o Claude Code, que lê o diff no `/fim-de-sessao`. Uma pessoa só quando o PR mexe no `contratos.md` ou na pasta dela: o ok vem no grupo, não no GitHub | combinado em 29/10: o clique de "aprovar" travava tudo e ninguém lia o diff de verdade |
| Quem faz o merge | o autor (o `/fim-de-sessao` faz), com o CI verde, depois de um "pode". PR da Náthally: o Eduardo revisa com o Claude Code e faz o merge | ninguém fica esperando outra pessoa para fechar o próprio trabalho |
| Tipo de merge | **merge commit** (nunca squash nem rebase) | guarda os commits pequenos (prova do processo para a banca) e não quebra quem continua na branch |
| Proteção da `main` | exige PR e o check `testes` verde; só "Allow merge commits"; "Automatically delete head branches" ligado. Quem configura: o Miguel (só ele é admin), na MG1 | sem pedir aprovação, o CI é a trava: nada entra com teste vermelho |
| Trazer a `main` para a sua branch | `git merge main` e rodar os testes. Conflito: `git merge --abort` e fale com o dono do arquivo | o `rebase` exige `push --force`, o jeito mais comum de apagar trabalho do colega |
| Tags | `v0.1-demo` na **ter 03/11** e `v1.0` na **sex 06/11**; depois, só `v1.0.1`… com consertos. Quem cria é o Eduardo: `git tag -a v1.0 -m "versão da banca"` e `git push origin v1.0` | avaliação final, vídeo e teste do zero rodam na mesma versão |
| Arquivo comum (`README`, `contratos`, `requirements`, `tests/`, `docs/`) | um PR por vez; avise no grupo | evita conflito |

---

## 3. Sessões, em ordem, por pessoa

**Regras de sessão:**
- **Uma sessão = uma linha abaixo = uma branch = um PR.** Começa com `/inicio-de-sessao` e termina com `/fim-de-sessao`.
- **Modo Plan** para mais de um arquivo, para contrato ou para arquivo comum; **manual** para um arquivo só, ou quando você mesmo escreve o código.
- **`/clear`** entre uma tarefa e outra, nunca com mudança sem commit. Detalhes: [aprender/claude-code.md](../aprender/claude-code.md).

### Calendário

| data | Eduardo | Marcos | Miguel | Náthally |
|---|---|---|---|---|
| ter 27/10 | ✅ ED0, ED1, ED2, ED5, ED4 (código), ED6; portes MA1 e NA1 | ✅ #4 na `main` (MA1) | ✅ #3 na `main` | ✅ #5 na `main` |
| qua 28/10 | ✅ ED4 (segmentação consertada, PR #9) | MA2 (passou para 29–31/10) | MG1; começa o Docker | NA1 regras v2 |
| qui 29/10 | ✅ ED3 e ED7 (adiantadas); portes NA1 e NA2 (PRs #10 e #11); teste do Docker e do Terraform | ✅ MA2: PR #18 fechado; PR #21 mesclado às 17h52 | MG2 Docker + PostgreSQL | ✅ NA1 e NA2 entregues |
| sex 30/10 | ✅ conferência da MA2 e PR #22 (CI com PostgreSQL, CSV do C2); ensinar o Claude Code ao Miguel | MA3 | MG2 (`docker-compose.yml`), **prazo do PR** | NA3 tempo manual |
| sáb 31/10 | revisões; ED8 começa; plano B da MA2 se precisar | **MA2 (prazo)**; MA3 | MG3 Terraform | NA3 tempo manual; marcar testes |
| dom 01/11 | revisões | MA4 EDA | **MG3: se o Terraform não subiu, fica só o Docker**; MG4 | NA3 |
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
| ED1 | 27/10 | ✅ `data/ed1/` | 3 raio-x reais para a Náthally, com os scripts do Marcos e o CSV convertido só na sua `data/` | nada no Git | Manual | 3 empresas de setores diferentes, `removidos` conferido, enviado | nenhum |
| ED2 | 27/10 | ✅ PR #6 | testes sem depender de `data/` (`RAIOX_DADOS`); "balanço consolidado" | `raiox/`, `tests/` | — | 17 passam | `eduardo-ia-testes` |
| ED3 | qui 29/10 | ✅ PR #11 | regras v2 da Náthally no prompt: `regras()` lê `avaliacao/regras_prompt.md` | `raiox/ia.py`, `tests/` | Manual | 3 chamadas reais sem item removido por dígito (feito: 0 removidos, US$ 0,0036) | `eduardo-regras-v2` |
| ED4 | qua 28/10 | ✅ PR #9 | consertar a segmentação real: receita mínima de R$ 10 mi, extremos cortados em 5/95, menor grupo com pelo menos 5% das empresas. Os gráficos de antes (`data/ed1/*_antes_ed4.png`, só na máquina do Eduardo) servem para a banca: "a silhueta alta enganava" | `raiox/segmentos.py`, `tests/`, `docs/graficos/*.png` | Plan | nenhum grupo com menos de 5%; "parecidas" de 3 empresas conhecidas fazem sentido; 2 PNG reais | `eduardo-segmentacao` |
| ED5 | 27/10 | ✅ PR #6 | `avaliacao/avaliar.py` (C4) | `avaliacao/`, `tests/` | — | `python -m avaliacao.avaliar` grava o C4 | `eduardo-ia-testes` |
| ED6 | 27/10 | ✅ PR #6 | teste ponta a ponta (pula sem `data/`) | `tests/test_ponta_a_ponta.py` | — | pula no CI; roda local com dados reais | `eduardo-ia-testes` |
| ED7 | qui 29/10 | ✅ PR #20 | `python -m avaliacao.avaliar --com-ia` nos 10 casos (avisar o grupo) | `avaliacao/resultados.csv` | Manual | 10 linhas; custo anotado (feito: 10 linhas, 0 erros, 0 removidos, US$ 0,0118) | `eduardo-avaliacao-ia` |
| ED8 | qua 04/11 | — | justificativa técnica para o PDF + README "Como usamos IA" | `docs/justificativa.md`, `README.md` | Manual (você escreve; a IA confere com arquivo e linha) | o Marcos lê e entende | PR |
| ED9 | sex 06/11 | — | congelar | só bugs | Plan | CI verde + ponta a ponta verde | **tag `v1.0`** |
| ED10 | sáb 07/11 | — | teste do zero em outra máquina, só com o README | consertos | Manual | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisar |
| ED11 | sex 06/11 | — | avaliação final na `v1.0` (só se a IA mudou depois do ED7) + ensaio de defesa | `resultados.csv` | Plan | 10 perguntas da banca respondidas sem consulta | PR |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | ✅ PR #21 (Marcos, 29/10) e PR #22 (Eduardo, 30/10, com o ok do Marcos): o "pronto quando" passa. Sobram para a MA3: `cd_cvm` int e só ativas no C1, tabela `indicadores` (seção 0) | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 | — | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | — | montar o `documentacao.pdf` | `docs/documentacao.pdf` | fora do Claude | BPMN + justificativa + ética + arquitetura | PR |

### Miguel (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | 🟡 #3 na `main` e aprovação obrigatória tirada (29/10); falta o check `testes` obrigatório, apagar branch após o merge e só merge commit | configurar o GitHub (seção 2, "Proteção da `main`"); rodar a tela local | configurações | só leitura | as 3 configurações feitas; print da tela no grupo | — |
| MG2 | qui 29–sex 30/10 | 🟡 funciona (testado em 29/10); sem PR; 7 ajustes na seção 0 | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | 🟡 `apply`, `destroy` e `apply` funcionam (29/10); falta montar a `data/` | Terraform (provider docker) com os 2 contêineres (tela + PostgreSQL), **só se o Docker estiver pronto**. Prazo: dom 01/11; senão, corta | `infra/` | Plan | `terraform apply` sobe; `destroy` + `apply` mantém `data/` e o banco | PR |
| MG4 | dom 01–ter 03/11 | — | tela com dados reais: `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`; volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner | PR (Eduardo) |
| MG5 | qua 04/11 | — | diagrama de arquitetura + README (pré-requisitos com Python 3.14; rodar local, Docker e Terraform) | `docs/arquitetura.png`, `README.md` | Manual | um colega entende o fluxo lendo o README | PR |
| MG6 | qui 05/11 | — | roteiro de 6 min da demo + vídeo v0 | — | — | vídeo salvo em 2 lugares | — |
| MG7 | sáb 07/11 | — | vídeo final na `v1.0` | — | — | vídeo salvo em 2 lugares | — |

### Náthally (sem IA de código: GitHub pelo navegador)

Para subir um arquivo:
1. No GitHub, com a branch `main` selecionada, "Add file → Upload files".
2. Escolha "Create a new branch" (`nathally-tarefa`).
3. Abra o PR. O Eduardo revisa com o Claude Code e faz o merge.

| # | data | status | objetivo | altera | pronto quando |
|---|---|---|---|---|---|
| NA1 | qua 28–qui 29/10 | ✅ regras v2 (PR #11) | regras v2 alinhadas ao código | `avaliacao/regras_prompt.md` | PR aberto |
| NA2 | sex 30/10 | ✅ códigos (PR #10); ela ainda confere | preencher o `cd_cvm` dos 10 casos (WEG = 5410) | `avaliacao/casos_avaliacao.csv` | `tests/test_ponta_a_ponta.py` passa (o Eduardo roda) |
| NA3 | sáb 31/10–qui 05/11 | — | `tempo_manual.csv` (3 empresas), 3 testes com usuários (sem nome), conta do ROI | `avaliacao/` | 3 testes feitos; ROI com números medidos |
| NA4 | qua 04/11 | — | `revisao.csv` sobre o `resultados.csv`; métricas | `avaliacao/revisao.csv`, `docs/produto/metricas.md` | % de comparações certas, % de perguntas ligadas ao produto, utilidade, custo, tempo |
| NA5 | sáb 07–dom 08/11 | — | texto de governança e ética; deck com o tempo de cada parte | `docs/etica.md`, deck | o Marcos recebe a ética; todos os slides chegaram |
| NA6 | seg 09–qua 11/11 | — | deck final; 2 ensaios cronometrados | deck | ensaio abaixo de 20 min |

---

## 4. Testes

**Regra:**
- Toda mudança de comportamento vem com um teste novo ou atualizado, no mesmo PR.
- Rode `python -m pytest -q` antes de cada commit e antes de cada PR.
- O CI roda em todo PR, e nada entra na `main` com o CI vermelho.
- Nenhum teste chama a API do Gemini.

| arquivo | o que testa | dono | roda no CI? |
|---|---|---|---|
| `tests/conftest.py` | todo teste usa a tabela falsa (`RAIOX_DADOS=falsos`) e nada grava em `data/` | Eduardo | sim |
| `tests/test_raio_x.py` | validador (regra de ouro), contrato C3, fonte, modo sem IA nas 30 empresas falsas, prompt (lê as regras da Náthally, chaves preservadas, só marcadores de indicador), texto sem IA na forma da v2, `RAIOX_DADOS`, segmentação (k = 3, 29 de 30; menor grupo ≥ 5%; empresas pequenas fora do treino; `segmentos.csv` refeito quando o código muda), gráficos, checador | Eduardo | sim |
| `tests/test_avaliar.py` | `avaliar.py`: colunas do C4, casos válidos, caso com erro, formato do `casos_avaliacao.csv` (5 colunas, `cd_cvm` inteiro em todos) | Eduardo | sim |
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py`, `test_banco.py`, `test_verificar_automatico.py` (PRs #4 e #21) | regras de limpeza, carga da DFP (rede simulada), catálogo e C1 em PostgreSQL (banco de teste separado: `tests/banco_teste.py`); o C2 (CSV padrão, `cd_cvm` int) em `test_calcular_grava_csv_padrao_com_cd_cvm_inteiro` (#22) | Marcos | sim: o CI sobe um PostgreSQL desde o #22 (sem ele, os testes do banco pulam; `-rs` mostra quais) |
| C1 na busca (MA3) | `cd_cvm` int e só companhias ativas | Marcos | ainda não existe |
| `tests/test_tela.py` (MG4) | a tela com os falsos: busca, gerar, 6 métricas, sem erro | Miguel | sim |
| `tests/test_ponta_a_ponta.py` | C2 real, raio-x sem IA de 3 setores, `cd_cvm` dos casos (todos preenchidos e na tabela real) | Eduardo | **não**: pula sem `data/`. Rodar local antes de `v0.1-demo`, `v1.0` e no teste do zero |
| `tests/test_aprender.py` | o notebook `aprender/passo_a_passo.ipynb` roda inteiro e vai para o Git sem saídas | Eduardo | sim |
| Docker | `curl localhost:8501/_stcore/health` → `ok` | Miguel | não (checklist da demo) |

---

## 5. Pontos de integração

| data | quem | o que sincroniza | o que congela |
|---|---|---|---|
| sex 30/10 | Marcos → todos | `data/` v1 no Drive | — |
| sáb 31/10 | Marcos → todos | PostgreSQL na `main` e C2 cumprido (MA2) | formato e colunas do C2; `DATABASE_URL` |
| dom 01/11 | Miguel | decisão: Terraform ou só Docker | infra |
| ter 03/11 | os 4 | demo ponta a ponta; tag `v0.1-demo` | **interfaces** (C1, C3, `RAIOX_DADOS`) e escopo: nada novo |
| sex 06/11 | os 4 | tag `v1.0` | código |
| dom 08/11 | todos → Náthally | conteúdo dos slides | roteiro |
| qua 11/11 | os 4 | tudo pronto para entregar | entregáveis |

**Como os dados chegam a cada um:**
- O Marcos publica um zip da pasta `data/` (os CSV) no Drive na sex 30/10 e na sex 06/11.
- O banco não vai no zip: cada um sobe o PostgreSQL com `docker compose up` e carrega com `python scripts/carregar_dfp.py`
  (22 s na máquina do Eduardo no ED1).
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
| sex 30/10 | o Miguel não abre o PR do Docker | no sáb 31/10, o Eduardo abre o PR com os 7 ajustes e o `docker-compose.yml` com o PostgreSQL (seção 0) e o Miguel revisa |
| dom 01/11 | o Terraform não sobe | fica só o Docker (o guia aceita "Terraform ou conteinerização") |
| ter 03/11 | o PostgreSQL não sobe no Docker na demo | `docker compose up` ensaiado no teste do zero (ED10); vídeo gravado (MG6/MG7); a busca falsa (`falsos/`) ainda mostra a tela sem banco |
| ter 03/11 | a demo não roda inteira | qua e qui 04–05/11 só para isso; o vídeo vira obrigatório; demo por `docker run` ou `streamlit run` local |
| dia da banca | a API falha ou o crédito acaba (erro 402) | a tela volta sozinha para o modo sem IA, com aviso (MG4); vídeo; saldo conferido em 08/11 |
| qualquer dia | a banca é **antes** | o código já congela em 06/11 e os entregáveis ficam prontos em 11/11 |
| qualquer dia | alguém fica indisponível | duplas de reserva: Marcos ↔ Eduardo (dados), Miguel ↔ Eduardo (infra), Náthally ↔ Marcos (deck e PDF) |

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

O código do ED2, do ED5 e do ED4 (27–28/10) e o da ED3 (29/10) foi escrito pela IA, para adiantar o projeto.
Antes da banca, o Eduardo explica em voz alta, sem olhar, cada um destes pontos. Se não conseguir, pede "explique para iniciante" e tenta de novo.

| arquivo e função | o que explicar |
|---|---|
| `raiox/segmentos.py`, `treino()` e `matriz()` | por que só receita a partir de R$ 10 mi, por que a receita entra em log, por que cortar extremos em 5/95, por que a mediana nos nulos, o que o `StandardScaler` faz |
| `raiox/segmentos.py`, `segmentar()` e `escolher_k()` | K-means, silhueta, por que k vai de 3 a 8, por que a silhueta 0,77 enganava e a regra dos 5%, `NearestNeighbors` com 6 vizinhos |
| `raiox/segmentos.py`, `grafico_grupos()` | o que o PCA faz e o que significa "39% + 20% da variação" nos eixos |
| `raiox/ia.py`, `montar()` | o que vai para o LLM e o que nunca vai (`valores`) |
| `raiox/ia.py`, `validar_e_preencher()` | por que a IA não consegue escrever número na tela |
| `raiox/ia.py`, `regras()`, `_prompt()` e `marcadores_do_llm()` | por que o prompt lê o arquivo da Náthally em vez de uma cópia, por que `SystemMessage` (as chaves `{margem_ebit}`), por que o Gemini só recebe `{id}` e `{id_grupo}`, por que o custo subiu de US$ 0,0008 para 0,0012 |
| `avaliacao/avaliar.py`, `avaliar()` | o laço, por que um erro não para a rodada, as colunas do C4 |
| `tests/conftest.py` | por que todo teste usa a tabela falsa |

**Método:** ler o trecho → prever o resultado → rodar → só então pedir "explique".
No Claude Code, `/explicar raiox/segmentos.py matriz` (por exemplo) segue esse método e termina com 3 perguntas como as da banca.
