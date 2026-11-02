# Plano até a banca (versão acelerada)

Meta: **feito, não perfeito**. O código congela na **sex 06/11** e tudo fica pronto para entregar na **qua 11/11**, com folga
até a entrega de **seg 16/11** (banca prevista para qua 18/11, a confirmar). Se a banca vier antes, já estamos prontos.

**O que o projeto precisa ter** vem dos arquivos do professor, em `docs/professor/` (`requisitos_projeto.MD` e
`guia_projeto_final.pdf`). Eles valem mais que este plano: nada que esteja neles pode ser cortado (seção 7).

**Onde está cada coisa:** o que fazer agora → seção 0; quem faz o quê e quando → seção 3; o que o professor exige e o status de
cada item → [REQUISITOS.md](REQUISITOS.md); o que já aconteceu → [HISTORICO.md](HISTORICO.md).

**Como usar:** cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (ex.: MA2). No Claude Code, comece
com `/inicio-de-sessao MA2` e termine com `/fim-de-sessao`: ele faz o Git, atualiza a seção 0, o REQUISITOS e o HISTORICO,
abre o PR, espera o CI e faz o merge depois do seu "pode". Guia: [aprender/claude-code.md](../aprender/claude-code.md).

**Hipóteses:** cada pessoa tem de 6 a 12 h por semana, fora a aula. Eduardo, Marcos e Miguel usam o Claude Code;
a Náthally não programa com IA e sobe arquivos pelo navegador do GitHub (seção 3).

---

## 0. Situação atual (o `/fim-de-sessao` reescreve esta seção e apaga o que ficou velho)

**Em seg 02/11 (feriado), ~16h30.** Na `main`: PRs #1 a #16 e #19 a #36 (hoje entraram o #30, travas; o #31, justificativa
técnica; o #32 e o #33, notas do Eduardo; o #36, a MG4). O #34 trocou o guia do professor por uma versão sem os exemplos, refeita
pelo grupo, e o #35 o desfez: a `main` voltou a ter o guia original (`git diff --stat 9e1a974 c7869e3` → vazio). O guia fica como o
professor mandou (HISTORICO, decisões). A MA3 e a MA4 (Marcos) ainda não têm branch.

**PR #36 (Miguel, MG4, 02/11): a aplicação usa o contêiner do banco** (`requisitos_projeto.MD`, Aplicação: "Backend e Frontend" e
"Banco de dados"; regra do professor de 02/11: 2 contêineres). Em `app/streamlit_app.py`:
- o `USAR_DADOS_FALSOS = True` fixo saiu. A tela usa a mesma regra do raio-x (`usando_falsos()`, de `raiox/segmentos.py`): com a
  `data/indicadores.csv` real, a busca e o `registrar_consulta` usam o PostgreSQL (`raiox/dados.py`); com `RAIOX_DADOS=falsos`, os falsos;
- com `RAIOX_IA_REAL=1`, se o Gemini der erro, a tela monta o texto sem IA (os números são os mesmos) e mostra um aviso, em vez de parar;
- banco desligado ou vazio vira mensagem com o que fazer; se gravar a consulta falhar, o raio-x aparece do mesmo jeito;
- o `cd_cvm` vira número antes do raio-x e do registro (o `raiox/dados.py` ainda devolve texto: MA3).

Conferido no `docker compose` (os 2 `healthy`): o raio-x sem IA de WEG, Embraer e Ambev pelo navegador, e as 3 linhas na `consultas`
com `cd_cvm` número (`docker compose exec banco psql -U postgres -d raiox -c "SELECT registro_json FROM consultas"`).
Testes novos em `tests/test_tela.py` (6, com o `AppTest` do Streamlit; nenhum chama o Gemini). Local, com o PostgreSQL ligado:
230 passed, nenhum pulado; no contêiner: 210 passed e 20 pulados, todos do `tests/test_guarda.py`, que precisam do `git`.
**Não conferido:** a volta para o modo sem IA com o Gemini de verdade; a tela nova pelo Terraform.
**Para a demo de ter 03/11:** depois do merge, `docker compose up -d --build` (senão o contêiner roda a tela antiga); com IA, `RAIOX_IA_REAL=1`.

**PR #30 (Eduardo, ED12): as travas estão na `main`** (`requisitos_projeto.MD`, Aplicação: "Arquivos utilizados de prompts para o
vibecoding"; guia §2: "agentic coding"). São o `.claude/settings.json` (do grupo), os 3 hooks do `.claude/hooks/guarda.py` e a
conferência do commit pelo próprio Git (`.githooks/pre-commit`). O que cada uma bloqueia ou pergunta está no CLAUDE.md, em "Travas
automáticas". O subagent `revisor` (só lê) entra no passo 6 do `/fim-de-sessao`. No #30 ele revisou 4 vezes, e os achados viraram
testes (`tests/test_guarda.py`). **Não conferido:** se o "ask" de um hook aparece no modo bypass (por isso o merge e o Gemini também
são regra `ask` do settings); o Linux; o `user.name` do Git do Marcos.
**Quem usa Claude Code (Marcos e Miguel), uma vez:** `git switch main`, `git pull`, `git config core.hooksPath .githooks` e abrir o
`claude` de novo na raiz. Sem `.venv`, pôr o `RAIOX_PYTHON` no seu `.claude/settings.local.json` (`aprender/claude-code.md`, "Travas").

**PR #31 (Eduardo, ED8, 02/11): justificativa técnica em `docs/justificativa.md`** (`guia_projeto_final.pdf` §6: "Justificativa
técnica das escolhas de modelos/arquiteturas (ex.: RAG vs Fine-tuning)"; §7: "chains e a memória"). Explica:
- por que nem RAG vetorial nem fine-tuning: a base de conhecimento é a tabela da CVM, buscada pela chave da empresa;
- a chain de 2 passos, sem memória e sem agente, de propósito;
- o K-means e a lição da silhueta 0,77;
- a parte técnica da segurança;
- 6 perguntas prováveis da banca, com resposta curta.

Cada afirmação cita arquivo e linha, conferidos em 02/11 (ex.: `avaliacao/resultados.csv`: 10 casos, 0 removidos, US$ 0,0118, 2,2 s
em média). O README ganhou a seção "Como usamos IA para programar" (R14). O texto vai para o `documentacao.pdf` (MA6). Escrito pelo
Claude Code a pedido do Eduardo, e não por ele, como dizia a seção 3. **Falta o "pronto quando": o Marcos ler e entender.**
Testes: 207 passed, 17 skipped (os do banco, com o PostgreSQL local desligado; o CI roda os 17).

**PR #29 (Miguel, MG3, 31/10): o Terraform está na `main`, em `infra/`** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura
automatizada com Terraform"). Dentro de `infra/`, `terraform apply` constrói a imagem do `Dockerfile` e sobe a tela (`raiox-tela`)
e o PostgreSQL (`raiox-banco`, `postgres:17`, com o `raiox_teste`), numa rede `raiox`, como o `docker-compose.yml`. Provider
`kreuzwerker/docker` 4.6.0, travado no `infra/.terraform.lock.hcl`. Escolhas (`infra/main.tf`):
- o volume do banco (`raiox-banco-dados`) não é recurso do Terraform: o `destroy` apaga os contêineres e mantém o banco;
- a chave do Gemini não passa pelo Terraform: o `.env` é montado só leitura na tela (o código chama `load_dotenv()`), e a chave
  não fica no `terraform.tfstate`. Resolve os itens "chave opcional" e "chave no tfstate" da nota de 30/10;
- portas só em `127.0.0.1`; imagem nova só quando o código muda (`triggers`).

Conferido no Linux do Miguel (Terraform 1.17.0), nas portas 8502 e 5433, com o compose ligado nas padrão: os 2 `healthy`,
`curl localhost:8502/_stcore/health` → `ok`, a tela abre; `docker exec raiox-tela python -m pytest -q` → 87 passed, nenhum pulado;
a imagem não tem `.env` nem `data/`, e `grep -c GOOGLE_API_KEY infra/terraform.tfstate` → 0; uma tabela de marca no banco e a
`data/` sobreviveram ao `destroy` + `apply`; o 2º `terraform plan` → "No changes". CI novo, `.github/workflows/terraform.yml`:
`terraform fmt` e `validate` em todo PR que mexe em `infra/` (não é check obrigatório da `main`). Local: 87 passed, nenhum pulado.
IA pelo Terraform: o Miguel rodou com `-var ia_real=true` e viu "Texto escrito pelo Gemini." e os tokens com o custo em
"Detalhes técnicos" (conferido por ele; o Claude não viu). **Não conferido:** as portas padrão (8501 e 5432; só muda o número); o Mac;
carregar a CVM pelo `docker exec` (o comando está no topo do `infra/main.tf`, igual ao do compose).
Com o compose ligado, o `terraform apply` dá `port is already allocated` (aconteceu em 31/10): um de cada vez, ou outras portas
(`-var porta_tela=8502 -var porta_banco=5433`). Está no README e no `aprender/COMANDOS.md`, seção 9.

> **Decisão de 30/10: o Terraform é obrigatório, e os arquivos do professor são a fonte da verdade** (PR #28).
> O `requisitos_projeto.MD` do professor (29/10, repositório do curso; cópia em `docs/professor/`) pede, em "Aplicação",
> "Infraestrutura automatizada com Terraform, podendo rodar localmente ou na nuvem". As notas seguiam só o guia em PDF (07/10),
> que aceita "Terraform ou conteinerização", e tratavam o Terraform como cortável: errado. O R também pede backend e frontend,
> banco de dados, os arquivos de prompts do vibecoding, README com as tecnologias e um documento com as etapas desenvolvidas.
> O CLAUDE.md, o AGENTS.md, o REGRAS-IA.md e as 3 skills agora mandam ler os dois arquivos em toda sessão. O que ficou a
> responder ao professor está no REQUISITOS ("Perguntas para o professor"); o que falta, nas linhas R13, R14, D1b, D1c e D2.
**O PostgreSQL está na `main`** (MA2: PR #21 do Marcos e PR #22). Com a `data/` real e o PostgreSQL local: 87 passed,
nenhum pulado. O CI agora também roda os testes do banco (#22).

**PR #24 (Miguel, MG2, 30/10, primeira sessão dele com o Claude Code): `docker compose up -d --build` sobe a tela e o PostgreSQL.**
Branch nova `miguel-docker`, a partir da `main`, com o `Dockerfile` e o `.dockerignore` da `docs-docker-e-terraform` (27–28/10).
O que mudou: `FROM python:3.14-slim` (igual ao CI); a tela roda de dentro de `app/` (tema); `HEALTHCHECK`; `data/` e `infra/` fora
da imagem (`avaliacao/`, `tests/` e `aprender/` ficam: o prompt lê `avaliacao/regras_prompt.md` e o `tests/test_aprender.py` roda o
notebook); `docker-compose.yml` com o `banco` (`postgres:17`, volume `banco-dados`, porta só em `127.0.0.1`) e a `tela`
(espera o banco ficar healthy; `DATABASE_URL` aponta para o serviço `banco`; `data/` como volume; chave e modos por variável);
`infra/banco/01_banco_de_testes.sql` cria o `raiox_teste` na 1ª vez. Os comandos estão no topo do `docker-compose.yml`.
Conferido no Linux do Miguel (Docker 29.9.2, Compose 5.6.1): os 2 contêineres `healthy`; `curl localhost:8501/_stcore/health` → `ok`;
`carregar_dfp.py` dentro do contêiner gravou no banco dele (384.561 linhas de contas, 2.567 empresas, em ~1 min com o download);
`docker compose run --rm tela python -m pytest -q` → 87 passed, nenhum pulado; na tela, o raio-x da WEG sem IA com os números reais
(receita R$ 40,8 bi), ainda com o aviso "empresas e números inventados" (MG4). Imagem: 1,74 GB; nem a `data/` nem o `.env` entram nela.

**PR #23 (Eduardo, 30/10): o Gemini desiste rápido se a API travar.** Antes, a biblioteca esperava sem limite de tempo e
fazia até 6 tentativas (`timeout = None`, `max_retries = 6`, conferido na `langchain-google-genai` 4.4.2): na banca, a tela
ficaria girando em vez de mostrar o erro. Agora `raiox/ia.py` usa `TEMPO_LIMITE_S = 15` e `TENTATIVAS = 2` (o pedido e mais
uma): o erro chega em até uns 30 s. Conferido: 1 chamada real (WEG, 2,8 s, US$ 0,0011, 0 removidos) e, com o limite forçado
em 50 ms, o erro chegou em 0,4 s. Teste novo: `test_gemini_desiste_rapido_se_a_api_travar`.

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
- **PostgreSQL local:** `docker compose up -d banco` (o `docker-compose.yml` do #24) sobe o `postgres:17` com usuário e senha
  `postgres` na porta 5432, que é o endereço padrão do código (não precisa de `DATABASE_URL` no `.env`), já com o `raiox` e o
  `raiox_teste`. Quem subiu o `raiox-postgres` pelo `docker run` antigo: os dois disputam a porta 5432; pare um
  (`docker stop raiox-postgres`) ou suba o do compose em outra porta (`PORTA_BANCO=5433 docker compose up -d`).

**Onde está cada frente:**
- **Dados (Marcos):** o que sobrou da MA2 (contratos C1 e C2), sem teste ainda:
  1. `raiox/dados.py` devolve o `cd_cvm` como texto (`'5410'`); o C1 pede int (desde o #36, a tela converte, mas o conserto é aqui);
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
  suponho, sem conferir, que a fonte dela tire o arrendamento). Serve à MA3. Subi-lo numa branch nova é sugestão para ela (seção 3); o Marcos também pode pedir o arquivo direto.
- **IA (Eduardo):** ED7 feita (PR #20); limite do Gemini (PR #23); ED8 no PR #31 (02/11). Próxima: ter 03/11, demo ponta a ponta e tag `v0.1-demo` (a MG4 entrou no #36). Conferido em 30/10 com a `data/`
  real: o raio-x sem IA roda nas 595 empresas (0 erros, 0 removidos), e a busca do PostgreSQL devolve as mesmas 595.
  O K-means mudou um pouco com os dados do #22: silhueta 0,29 (era 0,30) e treino de 327, 76, 59 e 102 empresas
  (eram 330, 99, 74 e 59). Os PNG de `docs/graficos/` ainda são de 28/10: refazer com `python -m raiox.segmentos` depois da MA3.
- **Docker (Miguel, MG2):** feito no PR #24 (acima). Dos 7 ajustes de 29/10, os do Docker (1, 2, 3 e 6) entraram: a branch nova
  já parte da `main`, e o `.gitignore` com as linhas de cópia de chat não veio (o da `main` já tem as regras do Terraform).
- **Terraform (Miguel, MG3): feito no PR #29** (acima), em `infra/`. A branch antiga `docs-docker-e-terraform` (27–28/10) foi
  comparada com a `main` em 02/11: o Dockerfile e o Terraform dela foram substituídos pela MG2 e pela MG3; só não vieram 5 linhas de
  proteção do `.gitignore` (`crash.log`, `*.tfplan`, `*.tfvars.json`, `.aws/`, `.ssh/`), que hoje não fazem falta. O Miguel decidiu
  apagá-la: a cópia local saiu; a do GitHub ele apaga pelo site (a trava barra `git push --delete`).
- **Tela (Miguel, MG4): feita no PR #36** (acima).
- **Produto (Náthally):** regras v2 (PR #11) e `cd_cvm` dos 10 casos (PR #10) na `main`. Ela ainda confere os 10 códigos.
- **GitHub (Miguel, MG1): feito.** Conferido em 30/10, 11h35, pela API (`gh api repos/MiguelGrispan/trabalho-tcs/branches/main/protection`
  e `gh api repos/MiguelGrispan/trabalho-tcs`): a `main` exige PR (0 aprovações) e o check `testes`, inclusive para o admin
  (`enforce_admins`), sem force push nem apagar a `main`; só "Allow merge commits"; "Automatically delete head branches" ligado.
  Na prática: o #24 ficou `BLOCKED` enquanto o CI rodava e `CLEAN` depois do `pass`. A nota das 9h30 dizia que faltava; não conferi quando foi ligado.
  Sobram as branches antigas `tratamento_dados` (Marcos) e `feat/metricas` (Náthally).

**Caminho crítico** (o que trava os outros):
1. **MA3, os números certos** (Marcos): a Camil errada na demo é pior que nenhum raio-x.
2. **Trabalho fora da `main`:** toda entrega sai de uma branch nova a partir da `main` (seção 2); senão, alguém tem de portar à mão.

**Próximo passo de cada um:**
- **Marcos:** MA3: a issue #17 e as diferenças de Magalu e RD Saúde (acima), o OK, ou não, no corte de R$ 10 mi, e os 3 itens
  do C1 e do C2 que sobraram (acima), com teste. Dizer o que fazer com `verificar_automatico.py`, `graficos.py` e o PDF (o `docs/Raio-X Comercial.pdf`
  ainda fala de `catalogo.db` e `sqlite3`: parece o plano de 21/10 impresso), e se a
  `tratamento_dados` pode ser apagada.
- **Miguel:** avisar o grupo da MG4 (mexeu em `tests/`, `.env.example` e `aprender/`, pastas comuns) e mandar o print da tela
  rodando no Docker (MG1); conferir o `GOOGLE_API_KEY` no `.env`, se a demo for com IA (em 30/10 chegou vazio no
  `docker compose config`; ninguém abriu o arquivo; pelo Terraform, a IA funcionou em 31/10); apagar a `docs-docker-e-terraform`
  no GitHub, pelo site; MG5 (diagrama e README) na qua 04/11.
- **Alguém com Mac (Eduardo?):** dentro de `infra/`, `terraform init` e `terraform apply` (se não achar o Docker, o
  `DOCKER_HOST` do README) e dizer no grupo se subiu.
- **Náthally** (desde 02/11, as tarefas dela separam obrigatório de sugestão: seção 3). **Obrigatório:**
  1. até qui 05/11, o ROI mínimo (NA3);
  2. o slide de métricas (NA4);
  3. a ética e o deck (NA5 e NA6).

  **Sugestões, se der tempo:**
  - subir o `revisao_manual.md` (na `feat/metricas`) numa branch nova, em `avaliacao/`: ajuda a MA3 do Marcos;
  - testes com usuários e a `revisao.csv`;
  - regras v3: na ED7, 27 de 30 lacunas saíram genéricas e só 21 de 40 perguntas citam o produto ou o objetivo.

  Também: dizer se a `feat/metricas` pode ser apagada.
- **Eduardo, em ordem** (o Claude Code faz o Git):
  1. hoje: ensinar o Claude Code ao Miguel (travas no #30 e a nota explicando; falta conversar com ele); mandar ao grupo a mensagem geral (fluxo `/inicio-de-sessao` e `/fim-de-sessao`,
     regra do PostgreSQL, ajustes do Docker, resultado da ED7). Em 30/10, só a mensagem ao Marcos sobre o #22 está confirmada;
  2. perguntar ao professor a data da banca, as 2 perguntas que sobraram no REQUISITOS ("Perguntas para o professor": arquivos de
     prompts e base de conhecimento; a de backend e frontend foi respondida) e se há outras regras além dos arquivos dele (anotar no REQUISITOS);
  3. ✅ ED8 (PR #31, 02/11): falta o Marcos ler a `docs/justificativa.md` (é o "pronto quando");
  4. ter 03/11: demo ponta a ponta com `docker compose up -d --build` (tela + PostgreSQL + `data/` real; a tela usa o banco desde o #36) e tag `v0.1-demo`;
  5. no meio disso: `/explicar` nos pontos da seção 8.

**Pendências pequenas:**
- Eduardo: o `tests/test_aprender.py:19` exige exatamente "5 passed" no notebook; refazer os gráficos e os números do K-means
  depois da MA3 (acima).
- Marcos: `test_resolver_conflitos_trata_valor_vazio_como_divergente` (`tests/test_limpeza.py:147`) passa só pela ordem das linhas;
  `test_obter_indicadores_deixa_ausente_…` (`tests/test_dados.py:83`) não olha o `ativo_total`; `test_calcular_exporta_…` não tem
  receita de 2 anos antes igual a zero. (Os nomes ainda existem; não reli o corpo dos testes depois do #21.)
- O C4 (`contratos.md`) diz que o `avaliacao/conferencia.csv` é da Náthally, mas quem escreve é o Marcos (MA3): corrigir com o ok dos dois.

**Decisões em aberto:**
- data e horário da banca (Eduardo pergunta ao professor);
- `scripts/dados.py` ou `raiox/dados.py`: ficar com um só (os dois existem; Marcos);
- `verificar_automatico.py`, `yfinance` e `graficos.py`, cortados na seção 7 e de volta na `main` pelo #21 (Marcos e Eduardo);
- as 2 perguntas que sobraram para o professor (REQUISITOS): arquivos de prompts do vibecoding e base de conhecimento (Eduardo pergunta);
- apagar `tratamento_dados` e `feat/metricas` (Marcos e Náthally);
- corte de receita mínima de R$ 10 mi (Marcos, MA3; números do `avaliar_corte_receita.py` acima);
- as 3 notas do código (`NOTAS_DO_CODIGO`, em `raiox/ia.py`) vão para a v3 das regras? (Náthally).

**Progresso estimado** (Eduardo, 30/10, 9h30; a linha "tela e infraestrutura" e o total, Claude, 13h30, depois de ler o
`requisitos_projeto.MD`: estimativa, não medida):

| parte | feito | falta |
|---|---|---|
| núcleo do produto: dados, ML, IA, validador, avaliação | ~88% | MA3 (Camil, Magalu, RD Saúde); `cd_cvm` int e só ativas no C1; tabela `indicadores` |
| tela e infraestrutura | ~75% (Claude, 02/11, depois da MG4) | MG5 (diagrama e README); MG6 e MG7 (vídeo) |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~10% | quase tudo, mas não depende de código novo |
| **total** | **~53%** (Claude, 31/10) | com 11 de 26 dias usados (~42%): o núcleo está adiantado. Em 30/10 caiu um pouco porque o `requisitos_projeto.MD` (29/10) acrescentou itens: Terraform obrigatório, banco usado pela tela, documento das etapas, prompts do vibecoding |

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
| sáb 31/10 | revisões; ED8 começa; plano B da MA2 se precisar | **MA2 (prazo)**; MA3 | ✅ MG3 Terraform (PR #29) | NA3 tempo manual; marcar testes |
| dom 01/11 | revisões | MA4 EDA | ~~prazo da MG3~~ (entrou no sáb); MG4 | NA3 |
| seg 02/11 (feriado) | ✅ ED12 na `main` (#30); ✅ ED8 adiantada (#31) | | ✅ MG4 adiantada (#36) | |
| ter 03/11 | **demo ponta a ponta · tag `v0.1-demo`** | MA4 | ~~MG4~~ (feita em 02/11) | NA3 ROI mínimo |
| qua 04/11 | ✅ ED8 (feita em 02/11) | MA5 BPMN | MG5 arquitetura + README | NA4 slide de métricas |
| qui 05/11 | só bugs | MA5 | MG6 vídeo v0 | NA3 (prazo do ROI mínimo) |
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
| ED8 | qua 04/11 | ✅ PR #31 (02/11; escrita pelo Claude Code a pedido do Eduardo; falta o Marcos ler) | justificativa técnica para o PDF (inclui RAG × fine-tuning e por que os dados da CVM são a base de conhecimento da IA) + README "Como usamos IA para programar", ligado aos arquivos de prompts do vibecoding (REQUISITOS R14) | `docs/justificativa.md`, `README.md` | Manual (você escreve; a IA confere com arquivo e linha) | o Marcos lê e entende | PR |
| ED9 | sex 06/11 | — | congelar | só bugs | Plan | CI verde + ponta a ponta verde | **tag `v1.0`** |
| ED10 | sáb 07/11 | — | teste do zero em outra máquina, só com o README | consertos | Manual | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisar |
| ED11 | sex 06/11 | — | avaliação final na `v1.0` (só se a IA mudou depois do ED7) + ensaio de defesa | `resultados.csv` | Plan | 10 perguntas da banca respondidas sem consulta | PR |
| ED12 | sáb 31/10 | ✅ PR #30 (na `main` em 02/11) | travas do Claude Code (R14 e guia §2, agentic coding): `.claude/settings.json`, `.claude/hooks/guarda.py`, subagent `revisor`, import do `requisitos_projeto.MD` | `.claude/`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `aprender/claude-code.md`, `tests/test_guarda.py` | Plan | testes verdes; o hook bloqueia de verdade numa sessão | `eduardo-claude-config` |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | ✅ PR #21 (Marcos, 29/10) e PR #22 (Eduardo, 30/10, com o ok do Marcos): o "pronto quando" passa. Sobram para a MA3: `cd_cvm` int e só ativas no C1, tabela `indicadores` (seção 0) | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 | — | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | — | montar o `documentacao.pdf` | `docs/documentacao.pdf` | fora do Claude | etapas desenvolvidas no processo (R Documentação; a base é o `docs/HISTORICO.md`) + BPMN + justificativa + ética + arquitetura | PR |

### Miguel (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | ✅ conferido em 30/10: PR e check `testes` obrigatórios, só merge commit, apagar branch após o merge; tela rodando no Docker (o print vai para o grupo) | configurar o GitHub (seção 2, "Proteção da `main`"); rodar a tela local | configurações | só leitura | as 3 configurações feitas; print da tela no grupo | — |
| MG2 | qui 29–sex 30/10 | ✅ PR #24 (30/10): os 2 contêineres `healthy`, health `ok`, `carregar_dfp.py` no banco do contêiner, 87 passed no contêiner | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | ✅ PR #29 (31/10): `apply` sobe os 2 `healthy`; `destroy` + `apply` mantém o banco e a `data/`; 87 passed no contêiner; 2º `plan` sem mudanças. IA pelo Terraform vista pelo Miguel. Não conferidos: portas padrão, Mac (seção 0) | **Terraform na `main`, obrigatório** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform"): provider docker com os 2 contêineres (tela + PostgreSQL), a partir do `terraform/` da branch `docs-docker-e-terraform`. Prazo: dom 01/11; reserva: seg 02/11 com o Eduardo. Não pode ser cortado | `infra/` | Plan | `terraform apply` sobe a tela e o banco; `destroy` + `apply` mantém a `data/` e o banco | PR |
| MG4 | dom 01–ter 03/11 | ✅ PR #36 (02/11): WEG, Embraer e Ambev geram o raio-x no contêiner, e as 3 consultas estão na `consultas`; 6 testes em `tests/test_tela.py`. Não conferidos: a volta para o modo sem IA com o Gemini de verdade e a tela pelo Terraform (seção 0) | tela com dados reais e **com o banco** (R Aplicação: banco de dados): `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`, e com `real` a busca e o `registrar_consulta` usam o PostgreSQL (`raiox/dados.py`); volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner, e cada consulta aparece na tabela `consultas` | PR (Eduardo) |
| MG5 | qua 04/11 | — | diagrama de arquitetura + README (tema, objetivo e tecnologias já estão; pré-requisitos com Python 3.14; rodar local, Docker e Terraform) | `docs/arquitetura.png`, `README.md` | Manual | um colega entende o fluxo lendo o README; o README cobre o que o R pede em "Documentação" | PR |
| MG6 | qui 05/11 | — | roteiro de 6 min da demo + vídeo v0 | — | — | vídeo salvo em 2 lugares | — |
| MG7 | sáb 07/11 | — | vídeo final na `v1.0` | — | — | vídeo salvo em 2 lugares | — |

### Náthally (sem IA de código: GitHub pelo navegador)

Para subir um arquivo:
1. No GitHub, com a branch `main` selecionada, "Add file → Upload files".
2. Escolha "Create a new branch" (`nathally-tarefa`).
3. Abra o PR. O Eduardo revisa com o Claude Code e faz o merge.

**Obrigatório × sugestão (02/11):** a Náthally trabalha no ritmo dela.
- **Obrigatório** é só o que os arquivos do professor pedem:
  - o deck (`requisitos_projeto.MD`, Documentação: "Criar slides");
  - a análise de ética (guia §2 e §6);
  - na apresentação, a viabilidade de negócio e as métricas de sucesso (guia §3). O valor de negócio pesa 20% na banca (guia §5),
    e o guia §7 pede para "explicar claramente o retorno sobre o investimento (ROI) ou a redução do tempo operacional".
- **Sugestão** é todo o resto.
- Ela pode usar IA (ChatGPT, Claude) para rascunhar texto e slides. Os números ela pede ao Eduardo, que confere com o Claude Code.

| # | data | status | objetivo | altera | pronto quando |
|---|---|---|---|---|---|
| NA1 | qua 28–qui 29/10 | ✅ regras v2 (PR #11) | regras v2 alinhadas ao código | `avaliacao/regras_prompt.md` | PR aberto |
| NA2 | sex 30/10 | ✅ códigos (PR #10); ela ainda confere | preencher o `cd_cvm` dos 10 casos (WEG = 5410) | `avaliacao/casos_avaliacao.csv` | `tests/test_ponta_a_ponta.py` passa (o Eduardo roda) |
| NA3 | até qui 05/11 | — | **Obrigatório, versão mínima: o ROI.** Cronometrar 1 vez a montagem manual de um raio-x (1 empresa, pelo site de RI) e 1 vez com a ferramenta, contando digitar, ler e conferir (não só os ~2 s da API), com a conta do ganho em 3 linhas (guia §7: "ROI ou a redução do tempo operacional"). *Sugestão:* 3 empresas no `tempo_manual.csv` e 3 testes com usuários (sem nome) | `docs/produto/` (ou `avaliacao/`) | 1 tempo medido e a conta do ROI |
| NA4 | qua 04/11 | — | **Obrigatório: 1 slide de métricas** com os números do `avaliacao/resultados.csv` (10 casos, 0 trechos removidos, US$ 0,0012 por raio-x, 2,2 s) e o acerto: **7 de 10 batem com o RI** na conferência manual dela de 29/10 (as 3 que diferem estão na MA3). Sem o acerto, o slide parece melhor que a realidade, que o Eduardo tira com o Claude Code. *Sugestão:* `revisao.csv`, com a nota dela para cada raio-x | deck (e `avaliacao/revisao.csv`, se fizer) | o slide de métricas existe |
| NA5 | sáb 07–dom 08/11 | — | **Obrigatório: o texto de governança e ética** (guia §2; §6: "análise de ética e segurança", no PDF): viabilidade, limites, viés, confiabilidade, alucinação, segurança de dados e uso responsável. Base pronta: `docs/justificativa.md`, seção 5. Deck com o tempo de cada parte | `docs/etica.md`, deck | o Marcos recebe a ética; todos os slides chegaram |
| NA6 | seg 09–qua 11/11 | — | **Obrigatório: o deck final** (`requisitos_projeto.MD`, Documentação; guia §6) e ensaios cronometrados (guia §3: no máximo 20 min; guia §7 pede o ensaio; o grupo marcou 2) | deck | ensaio abaixo de 20 min |

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
| `tests/test_raio_x.py` | validador (regra de ouro), contrato C3, fonte, modo sem IA nas 30 empresas falsas, prompt (lê as regras da Náthally, chaves preservadas, só marcadores de indicador), texto sem IA na forma da v2, limite de tempo e de tentativas do Gemini, `RAIOX_DADOS`, segmentação (k = 3, 29 de 30; menor grupo ≥ 5%; empresas pequenas fora do treino; `segmentos.csv` refeito quando o código muda), gráficos, checador | Eduardo | sim |
| `tests/test_avaliar.py` | `avaliar.py`: colunas do C4, casos válidos, caso com erro, formato do `casos_avaliacao.csv` (5 colunas, `cd_cvm` inteiro em todos) | Eduardo | sim |
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py`, `test_banco.py`, `test_verificar_automatico.py` (PRs #4 e #21) | regras de limpeza, carga da DFP (rede simulada), catálogo e C1 em PostgreSQL (banco de teste separado: `tests/banco_teste.py`); o C2 (CSV padrão, `cd_cvm` int) em `test_calcular_grava_csv_padrao_com_cd_cvm_inteiro` (#22) | Marcos | sim: o CI sobe um PostgreSQL desde o #22 (sem ele, os testes do banco pulam; `-rs` mostra quais) |
| C1 na busca (MA3) | `cd_cvm` int e só companhias ativas | Marcos | ainda não existe |
| `tests/test_tela.py` (MG4) | a tela com os falsos: busca, gerar, 6 métricas, sem erro | Miguel | sim |
| `tests/test_ponta_a_ponta.py` | C2 real, raio-x sem IA de 3 setores, `cd_cvm` dos casos (todos preenchidos e na tabela real) | Eduardo | **não**: pula sem `data/`. Rodar local antes de `v0.1-demo`, `v1.0` e no teste do zero |
| `tests/test_aprender.py` | o notebook `aprender/passo_a_passo.ipynb` roda inteiro e vai para o Git sem saídas | Eduardo | sim |
| `tests/test_guarda.py` (#30, 137 testes) | as travas do Claude Code (`.claude/hooks/guarda.py`): o que bloqueia, o que pergunta e o que libera; o teste do fim de resposta; e o repositório inteiro sem `data/`, `.env`, chave nem arquivo acima de 10 MB (vale para os 4, inclusive upload pelo navegador) | Eduardo | sim (os de Git pulam no contêiner, que não tem `git`) |
| Docker | `curl localhost:8501/_stcore/health` → `ok`; os testes dentro do contêiner: `docker compose run --rm tela python -m pytest -q` (87 passed em 30/10) | Miguel | não (checklist da demo) |
| Terraform | `terraform fmt -check` e `terraform validate` no CI (`.github/workflows/terraform.yml`, PRs que mexem em `infra/`); `apply`, `docker exec raiox-tela python -m pytest -q` (87 passed em 31/10) e `destroy` + `apply` na mão | Miguel | só o `fmt` e o `validate` |

---

## 5. Pontos de integração

| data | quem | o que sincroniza | o que congela |
|---|---|---|---|
| sex 30/10 | Marcos → todos | `data/` v1 no Drive | — |
| sáb 31/10 | Marcos → todos | PostgreSQL na `main` e C2 cumprido (MA2) | formato e colunas do C2; `DATABASE_URL` |
| dom 01/11 | Miguel | Terraform na `main` (MG3, obrigatório) | infra |
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
| R9 Arquitetura e infra com Terraform (obrigatório) | MG2, MG3, MG5 |
| R10 Governança e ética | NA5, ED8, MG4 |
| R11 ROI | NA1, NA3 |
| R12 Métricas | NA2, ED5, ED7, NA4, ED11 |
| R13 Backend, frontend e banco na aplicação | MG4 (pergunta ao professor respondida em 02/11: Streamlit vale, em 2 contêineres) |
| R14 Prompts do vibecoding | ED8 |
| D1 Repositório | ED0, MA1, NA1, ED9 |
| D1b README | MG5, ED8, ED10 |
| D1c Infra (Terraform) e notebooks | MG2, MG3, MA4 |
| D2 Documento (etapas, BPMN, justificativa, ética) | MA6 (com MA5, ED8, NA5, MG5) |
| D3 Deck | NA5, NA6 |
| D4 Vídeo | MG6, MG7 |
| D5 20 minutos | NA6 + ensaios de 10–11/11 |

---

## 7. Riscos, plano B e o que cortar

| marco | risco | plano B |
|---|---|---|
| sex 30/10 | o Miguel não abre o PR do Docker | no sáb 31/10, o Eduardo abre o PR com os 7 ajustes e o `docker-compose.yml` com o PostgreSQL (seção 0) e o Miguel revisa |
| dom 01/11 | o Terraform não sobe | a dupla de reserva da infra (Miguel ↔ Eduardo) termina na seg 02/11 (feriado). **Não pode ser cortado**: o `requisitos_projeto.MD` exige o Terraform (o guia aceitava "ou conteinerização", mas vale o mais exigente) |
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

**Se faltar tempo, cortar nesta ordem** (só o que **não** está nos arquivos do professor; o Terraform, o BPMN com o Raio-X,
o documento, o deck, o README e os prompts do vibecoding não podem ser cortados):
1. BPMN "hoje" (o do processo com o Raio-X é obrigatório)
2. testes com usuários (já são sugestão desde 02/11, seção 3)
3. ED11 (fica o resultado do ED7)

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
| `raiox/ia.py`, `_llm()` | por que 15 s e 2 tentativas (sem limite, a biblioteca espera para sempre e tenta 6 vezes), e o que a tela faz com o erro |
| `avaliacao/avaliar.py`, `avaliar()` | o laço, por que um erro não para a rodada, as colunas do C4 |
| `tests/conftest.py` | por que todo teste usa a tabela falsa |

**Método:** ler o trecho → prever o resultado → rodar → só então pedir "explique".
No Claude Code, `/explicar raiox/segmentos.py matriz` (por exemplo) segue esse método e termina com 3 perguntas como as da banca.
