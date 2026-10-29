# Plano até a banca (versão acelerada)

Versão de **ter 27/10/2026, noite** (seção 0 atualizada em qui 29/10). Meta: **feito, não perfeito**. O código congela na **sex 06/11** e tudo fica pronto
para entregar na **qua 11/11**, com folga até a entrega de seg 16/11. Se a banca cair na semana de 09–15/11, já estamos prontos.

A matriz do que o guia exige está em [REQUISITOS.md](REQUISITOS.md). Os detalhes técnicos do que estava quebrado, com
comandos de prova, estão em [aprender/seguindo-o-projeto.md](../aprender/seguindo-o-projeto.md).

**Como usar este plano:**
- Cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (por exemplo, MA2).
- Para começar, abra o Claude Code e digite `/inicio-de-sessao MA2` (ele cuida do Git).
- **Para terminar,** digite `/fim-de-sessao`. Ele:
  1. atualiza a seção 0 (situação atual) e a coluna "status" da sessão;
  2. atualiza a linha do REQUISITOS.md, se a sessão fecha uma;
  3. escreve de 1 a 3 linhas no [HISTORICO.md](HISTORICO.md) (o resumo de tudo o que já aconteceu);
  4. abre o PR, espera o CI e faz o merge depois do seu "pode".

**Hipóteses deste plano:**
- Cada pessoa tem de 6 a 12 h por semana, fora a aula.
- Eduardo, Marcos e Miguel usam Claude Code (o Miguel desde 28/10). A Náthally não usa IA para programar: ela sobe arquivos pelo navegador.
- Banca prevista para **qua 18/11 (a confirmar)**.

---

## 0. Situação atual (atualize a cada sessão)

**Em qui 29/10, 11h20** (sessão do Eduardo com o Claude Code: ED3, portes da NA1 e da NA2, teste do Docker e do Terraform, decisão do PostgreSQL, Git simplificado, PRs #11 a #14 na `main`).

> **Decisão de 29/10: o banco é PostgreSQL.** O professor disse que SQLite não vale (regra registrada no CLAUDE.md, no
> `contratos.md` e em `docs/REQUISITOS.md`, seção "Regras do professor"; PR #13). Por isso a MA2 ficou maior e o Docker
> passa a subir dois contêineres (tela + PostgreSQL). O replanejamento está nas seções 3, 5 e 7.

**Retomando numa sessão nova do Claude Code?**
1. Digite `/inicio-de-sessao ED7` (troque pelo código da sua sessão; o Eduardo segue a "ordem" abaixo).
   Ele atualiza a `main`, cria a branch e confere o GitHub. No fim, `/fim-de-sessao`. Guia: `aprender/claude-code.md`.
2. Antes de mexer em qualquer coisa, a sessão deve dizer o que mudou desde esta nota.

**O que mudou desde 28/10, 11h30:**
- **11h17: os PRs #11, #12, #13 e #14 entraram na `main`** (`8c51fcc`), depois do #10 (9h24) e dos #7 a #9 (28/10).
  Com a `data/` real, 73 passed; o CI da `main` está verde. O Miguel tirou a aprovação obrigatória do GitHub (`gh pr view` mostra
  os PRs como `CLEAN`, sem `REVIEW_REQUIRED`). Ainda falta o resto da MG1: check `testes` obrigatório e "apagar branch após o merge".
  Branches já inteiras na `main` foram apagadas; sobram `docs-docker-e-terraform` (Miguel), `tratamento_dados` (Marcos) e `feat/metricas` (Náthally).
- **A Náthally entregou as regras v2 e os `cd_cvm` dos 10 casos** (29/10, 9h), mas na `feat/metricas`, que não tem
  história em comum com a `main`. O Eduardo portou os dois, sem mudar as decisões dela:
  - **PR #10 (NA2):** `cd_cvm` dos 10 casos, como número inteiro e com a coluna `empresa` (C4). Ela escolheu
    Suzano S.A. (13986) e Localiza Rent a Car (19739). Os 10 existem na `data/` real. Dois testes que passavam sem testar
    nada agora testam (pendência de 27/10). **Já na `main`:** o Miguel aprovou e fez o merge 3 minutos depois de aberto,
    sem comentário e antes da Náthally conferir (o PR pedia o OK dela; a seção 2 diz que quem faz o merge é o autor).
    Os valores são dela, então o risco é baixo, mas ela ainda precisa conferir os 10 códigos na `main`.
  - **PR #11 (NA1 + ED3):** regras v2 em `avaliacao/regras_prompt.md`, sem mudar o texto. **ED3 feita:**
    - o `raiox/ia.py` não tem mais cópia das regras: `regras()` lê o arquivo dela e acrescenta 3 notas do código
      (`NOTAS_DO_CODIGO`: o grupo não é o setor; nome do indicador antes do marcador; onde vem a lista de marcadores);
    - o Gemini só recebe os marcadores `{id}` e `{id_grupo}` com valor, como pede a v2 (`marcadores_do_llm()`). Por isso o
      texto diz "a empresa", e não o nome; a tela mostra o nome no topo (`app/streamlit_app.py:106`);
    - o texto do modo sem IA (plano B) segue a mesma forma: 3 frases, perguntas com Como/Quais/O que/Onde, lacunas afirmativas;
    - 4 testes novos (`test_prompt_*`, `test_texto_sem_ia_segue_as_regras_v2`): 72 passed. Cada um pegou o código
      estragado de propósito;
    - **3 chamadas reais** (Camil, Magazine Luiza, WEG; produto e objetivo dos casos): nada removido pelo validador,
      3 frases em cada resumo, nenhuma palavra de intensidade, nenhuma lacuna em forma de pergunta, nenhum "setor" ou "mercado".
      As respostas estão em `data/ed3/` (fora do Git, só na máquina do Eduardo);
    - **custo:** o prompt passou de ~910 para ~2.260 tokens de entrada, e cada raio-x, de US$ 0,0008 para **US$ 0,0012**
      (os 3: US$ 0,0036). CLAUDE.md, README e `aprender/` corrigidos. Os 10 casos da ED7 custam ~US$ 0,012.
- **Antes × depois das regras v2** (mesmas 3 empresas do ED1, 27/10; o grupo também mudou no ED4):

  | o que a v2 pediu | ED1 (regras v3, 27/10) | ED3 (regras v2, 29/10) |
  |---|---|---|
  | sem palavras de intensidade | "muito superior", "significativamente acima", "tão expressiva" | nenhuma |
  | "do grupo ({x_grupo})" | "acima do crescimento em dois anos (+15%)" | "acima do grupo (+15%)" |
  | lacunas num formato só | 2 de 3 raio-x com lacunas em forma de pergunta | 0 de 3 |
  | perguntas abertas | "existe espaço no orçamento…?" (sim ou não) | todas com Como/Quais/O que |
  | nada removido pelo validador | 0 | 0 |

- **Para a Náthally olhar na v3** (não trava nada): as lacunas saíram genéricas nas 3 empresas ("Necessidade de entender…",
  "Falta de clareza sobre…", "Ausência de informações sobre…") e perderam os itens concretos da v1 (quem decide, orçamento,
  fornecedor atual): vale dar exemplos de lacuna boa. Algumas perguntas ligam endividamento a "capacidade de investir":
  é pergunta (regra 6 permite), mas fica perto de "insinuar que a empresa vai mal" (regra das perguntas). As 3 notas do código
  podem ir para a v3 dela.
- **Marcos:** subiu em 28/10 na `tratamento_dados` (sem história em comum com a `main`, estrutura antiga com `src/`) um
  script que avalia o corte de R$ 10 mi (`scripts/avaliar_corte_receita.py`), uma consulta SQL (`sql/prova_s1.sql`) e um
  `docs/Raio-X Comercial.pdf`. **A MA2 (CSV padrão, prazo hoje) não começou na `main`**: o script novo ainda lê com `sep=";"`.
  - **28/10, 20h10, também na `tratamento_dados`: "migra catálogo de SQLite para PostgreSQL"** (`5508116`, 18 arquivos;
    `sqlalchemy` e `psycopg` no `requirements.txt`; `src/banco.py`). É escopo novo e mexe em contrato (C1 e C2 falam do
    `data/catalogo.db`), no Docker (precisaria de um segundo contêiner com o PostgreSQL), no CI (os testes do banco pulam
    sem PostgreSQL: `tests/banco_teste.py`, `banco_disponivel()`) e no teste do zero (ED10: instalar PostgreSQL).
    O `indicadores.csv` continua com `sep=";"` (`git show 5508116:scripts/indicadores.py | grep -n sep=`).
    **Decidido em 29/10: fica o PostgreSQL** (regra do professor). Esse commit vira a base da MA2 (seção 3); na revisão,
    conferir os testes de "colunas ausentes" que ele apagou e fazer os testes do banco rodarem no CI (hoje pulariam).
- **Miguel: Docker e Terraform testados pelo Eduardo em 29/10**, numa cópia local da `main` + #11 + a branch dele
  (nada foi enviado ao GitHub). A branch continua sem PR. **Funcionam**; faltam ajustes.

  | teste (na máquina do Eduardo, Docker 29.8) | resultado |
  |---|---|
  | `docker build` como está (Python 3.12) | ✅ 4 min 40 s; imagem de 1,61 GB |
  | `docker build` com `python:3.14-slim` (igual ao CI) | ✅ build, 69 passed e 3 skipped, health `ok`; imagem de 1,62 GB |
  | `python -m pytest -q` dentro do contêiner | ✅ 69 passed, 3 skipped (igual ao CI) |
  | `curl localhost:8501/_stcore/health` | ✅ `ok` |
  | tela simulada (`AppTest` do Streamlit): busca, escolhe, preenche, gera | ✅ sem erro, 6 métricas, texto novo da ED3 |
  | tela com a IA (`-e RAIOX_IA_REAL=1`, `.env` montado só para leitura) | ✅ o Gemini respondeu (~2.250 tokens: leu as regras da Náthally); US$ 0,0011 |
  | tela com a `data/` real (`-e RAIOX_DADOS=real -v data:/app/data`) | ✅ WEG com números reais; ⚠️ o aviso diz "empresas e números inventados" |
  | `data/` real só para leitura (`-v data:/app/data:ro`) | ❌ o raio-x não saía. Bug do Eduardo (ED4): numa imagem, o `segmentos.py` é sempre mais novo que o `segmentos.csv`, e gravar dá erro. Consertado no PR #12 (`eduardo-segmentos-somente-leitura`, com teste) |
  | a chave (`.env`) entra na imagem? | ✅ não |
  | `terraform init` + `apply` (imagem `hashicorp/terraform:1.9.8`; provider docker 4.6.0) | ✅ sobe; health `ok` |
  | `terraform destroy` + `apply` | ✅ sobe de novo; mas sem volume, então a `data/` não existe no contêiner (critério da MG3 não passa) |

  **O que o Miguel acerta antes do PR** (cada item tem prova no teste acima):
  1. `git merge main` (a branch é anterior aos #7 a #10; com 2 pontos, o diff parece apagar as skills e os gráficos);
  2. `.dockerignore`: tirar a `data/` (hoje ela entra na imagem: um arquivo marcador posto na `data/` apareceu dentro dela)
     e a `aprender/`. Não tirar a `avaliacao/`: com a IA ligada, o prompt lê `avaliacao/regras_prompt.md`;
  3. `Dockerfile`: trocar para `FROM python:3.14-slim`, a versão do CI (testado: funciona igual);
  4. `terraform/main.tf`: montar a `data/` como volume (`volumes { host_path = "<caminho>/data", container_path = "/app/data" }`)
     e passar `RAIOX_DADOS=real` (e `RAIOX_IA_REAL=1`, se a demo usar a IA). Hoje o Terraform só sobe a versão de teste,
     e a chave que ele pede não é usada;
  5. `terraform/variables.tf`: a `google_api_key` é obrigatória, então o Terraform pede chave até para a demo sem IA. Deixar opcional;
  6. `.gitignore`: a primeira linha é ` ```gitignore ` e a última é ` ``` `, sobra de cópia de um chat. Apagar as duas;
  7. lembrar no README: a chave fica em texto puro no `terraform.tfstate` (o `.gitignore` já tira esse arquivo; não mandar para ninguém).
- **Mudança local no PLANO.md guardada:** às 9h17 o editor do Eduardo reformatou as tabelas deste arquivo (só espaços e
  traços; `git diff -w` mostra só isso). Ficou num `git stash` para não poluir os PRs. Para descartar: `git stash drop`.
  Para não acontecer de novo: desligar "Format On Save" para Markdown no VS Code.

**Progresso estimado** (Eduardo, 29/10):

| parte | feito | falta |
|---|---|---|
| núcleo do produto: dados, ML, IA, validador, avaliação | ~75% | MA2 (agora com o PostgreSQL na `main`), ED7 (ED3 e ED4 feitos) |
| tela e infraestrutura | ~35% | Docker e Terraform funcionam (testados em 29/10), mas numa branch sem PR; MG4 (aviso, modo sem IA automático) |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~10% | quase tudo, mas não depende de código novo |
| **total** | **~43%** | com 9 de 26 dias usados (~35%): o núcleo está adiantado; o PostgreSQL na `main` (MA2) e o PR do Docker estão no caminho crítico |

**Folga:** o plano termina na qua 11/11. Sobram 4 dias de reserva (12 a 15/11) antes da entrega de seg 16/11, e mais 2 até a banca.
Regra: atraso come a folga; **nunca** se acrescenta escopo. Se a folga acabar, use a lista de cortes da seção 7.

**Caminho crítico agora** (o que trava os outros):
1. **MA2** (Marcos): sem CSV padrão, o `test_ponta_a_ponta.py` só passa na máquina de quem converteu à mão, e a MG4
   (tela com dados reais) não começa. Plano B da seção 7: o Eduardo converte localmente e a MA2 entra até ter 03/11.
2. **MG2** (Miguel): o Docker funciona, mas não tem PR. Faltam os 7 ajustes acima. Plano B da seção 7: se não houver PR
   até sex 30/10, o Eduardo abre com os ajustes e o Miguel revisa.
3. **PostgreSQL na `main`** (MA2, Marcos, até sáb 31/10): a tela (C1), o Docker (MG2 e MG3), o CI e o teste do zero
   dependem dele. Plano B na seção 7: o Eduardo porta o commit `5508116` com o Claude e o Marcos revisa.
4. **Trabalho fora da `main`:** a Náthally e o Marcos ainda sobem nas branches antigas, e cada entrega precisa ser portada
   à mão. Daqui para a frente: **sempre uma branch nova a partir da `main`** (seção 2; para a Náthally, "Create a new branch"
   no GitHub com a `main` selecionada).

**Pendências da revisão de 27/10:**
- ✅ Regra de ouro no prompt: a v2 da Náthally proíbe número por extenso, e o prompt é o arquivo dela (ED3, PR #11).
- ✅ Eduardo: `test_casos_avaliacao_do_repositorio_segue_o_c4` agora confere a coluna `empresa`, e
  `test_casos_de_avaliacao_existem_na_tabela_real` não passa mais em branco (PR #10).
- **Falta (Eduardo):** o `tests/test_aprender.py` exige exatamente "5 passed" no notebook.
- **Falta (Marcos):** `test_resolver_conflitos_trata_valor_vazio_como_divergente` passa só pela ordem das linhas;
  `test_obter_indicadores_deixa_ausente_…` não olha o `ativo_total`; `test_calcular_exporta_…` não tem receita de 2 anos antes igual a zero.
- **Outros:** com dados reais, a tela mostra "empresas e números inventados" (MG4; o resto da tela já funciona com dados reais); o C4 diz que o `conferencia.csv` é da
  Náthally, mas quem escreve é o Marcos.

**Próximo passo de cada um:**
- **Náthally:** conferir os 10 códigos na `main` (`avaliacao/casos_avaliacao.csv`) e ler o exemplo da WEG no PR #11 (as regras v2
  dela já são o prompt). Se quiser mudar algo, vira a v3.
  Dizer se a `feat/metricas` pode ser apagada: a `Semana_01/` foi portada no #5, e as regras v2 e os casos estão nos
  PRs #10 e #11; só o `avaliacao.ipynb` (monta o CSV dos casos) ficou de fora: ela diz se quer guardar. Depois: tempo manual e ROI (NA3), testes com usuários, e revisão dos 10 raio-x quando a ED7 rodar.
- **Marcos:** ler a regra do PostgreSQL no `contratos.md` (já na `main`, PR #13). MA2 na `main`, agora com o PostgreSQL: branch `marcos-postgres`, a partir da
  `main`, trazendo o `5508116` para a estrutura da `main` (`raiox/dados.py` e `scripts/`, sem `src/`), com o CSV padrão (C2). Prazo sáb 31/10. Trazer o `avaliar_corte_receita.py` para a MA3,
  já lendo o CSV padrão, e dar o OK (ou não) no corte de R$ 10 mi. Dizer se a `tratamento_dados` pode ser apagada depois disso.
- **Miguel:** `git merge main` na `docs-docker-e-terraform`, acertar os 7 pontos acima e abrir o PR até sex 30/10 (MG2 e MG3; o Eduardo revisa).
  Com o PostgreSQL, o Docker vira um `docker-compose.yml` com 2 contêineres (tela + PostgreSQL, com volume para o banco);
  o Terraform cria os dois (ou é cortado, seção 7). Na MG4: trocar `USAR_DADOS_FALSOS` por `RAIOX_DADOS`, corrigir o aviso e
  voltar sozinho para o modo sem IA.
  Terminar a MG1 (a aprovação obrigatória já saiu): marcar o check `testes` como obrigatório, "Automatically delete head branches",
  e deixar só "Allow merge commits" (PLANO, seção 2).
- **Eduardo: a ordem** (uma coisa de cada vez; o Claude Code faz o Git):
  1. **agora:** mandar a mensagem ao grupo (o Claude escreve): tudo na `main`, o fluxo novo (`/inicio-de-sessao` e `/fim-de-sessao`),
     a regra do PostgreSQL, os ajustes do Docker, o custo novo (US$ 0,0012 por raio-x) e a ED7 (~US$ 0,012);
  2. **agora, 2 min:** `git stash drop` (a formatação do editor, guardada) e desligar "Format On Save" para Markdown no VS Code;
  3. **hoje:** `/inicio-de-sessao ED7`: a avaliação com IA nos 10 casos, que o Claude roda e resume para a Náthally;
  4. **hoje ou amanhã:** perguntar ao professor a data da banca e se há **outras regras além do guia** (anotar no REQUISITOS);
  5. **sex 30/10:** pedir ao Claude para revisar e testar os PRs da MA2 e do Docker quando chegarem; sem PR do Docker, plano B (seção 7);
  6. **sáb 31/10:** sem PR da MA2, plano B (o Claude porta o PostgreSQL e o Marcos confere); começar a ED8;
  7. **dom 01/11:** ED8 (você escreve; o Claude confere com arquivo e linha);
  8. **seg 02 e ter 03/11:** demo ponta a ponta com `docker compose` (tela + PostgreSQL + `data/` real) e tag `v0.1-demo`;
  9. no meio disso: `/explicar raiox/ia.py regras` (ED3) e `/explicar raiox/segmentos.py segmentar` (ED4), seção 8.

**Decisões em aberto:**
- data e horário da banca;
- `scripts/dados.py` e `raiox/dados.py`: ficar com um só (Marcos decide);
- nome da pasta da infraestrutura: `infra/` ou `terraform/` (Miguel, no PR do Docker);
- apagar `tratamento_dados` e `feat/metricas` (Marcos e Náthally);
- corte de receita mínima de R$ 10 mi (Marcos, MA3);
- as 3 notas do código vão para a v3 das regras? (Náthally).
- ✅ decidido em 29/10: Suzano S.A. (13986) e Localiza Rent a Car (19739) nos casos (Náthally).
- ✅ decidido em 29/10: **PostgreSQL**, porque o professor disse que SQLite não vale (Eduardo, com o grupo; PR #13).

**Já feito, para consulta:** ED1 (3 raio-x reais, 27/10), ED4 (k = 4, silhueta 0,30; os 4 grupos estão na linha R5 do
[REQUISITOS.md](REQUISITOS.md) e no commit `bed72c5`), PRs #3 a #9 (`gh pr list --state all`). Pasta para quem está
aprendendo: [aprender/](../aprender/README.md).

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
| Criar a branch | `/inicio-de-sessao` faz: `git switch main` → `git pull` → `git switch -c pessoa-tarefa` | sempre a partir da `main` atual |
| Quando abrir PR | quando o "pronto quando" da sessão passa e `python -m pytest -q` está verde | PR pequeno é revisado no mesmo dia |
| Quem revisa | o CI (os testes) e o Claude Code, que lê o diff no `/fim-de-sessao`. Uma pessoa só quando o PR mexe no `contratos.md` ou na pasta dela: o ok vem no grupo, não no GitHub | combinado em 29/10: o clique de "aprovar" travava tudo e ninguém lia o diff de verdade; quem recebe o contrato continua avisado |
| Quem faz o merge | o autor (o `/fim-de-sessao` faz), com o CI verde, depois de um "pode" | até 29/10, os 10 merges foram todos do Miguel |
| Tipo de merge | **merge commit**. O Miguel desliga squash e rebase e liga "apagar branch após o merge" | guarda os commits pequenos (prova do processo para a banca) e não quebra quem continua na branch |
| Proteção da `main` | **MG1, Miguel (só ele é admin):** em Settings → Branches → regra da `main`: manter "Require a pull request", tirar "Require approvals", ligar "Require status checks" com o `testes`; em Settings → General: só "Allow merge commits" e ligar "Automatically delete head branches". Em 29/10 a `main` exige 1 aprovação e nenhum check (`gh pr view 13 --json reviewDecision`) | sem pedir aprovação, o CI vira a trava de verdade: nada entra com teste vermelho |
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
- **Começo de toda sessão:** `/inicio-de-sessao` (`.claude/skills/inicio-de-sessao/SKILL.md`).
- **Fim de toda sessão:** `/fim-de-sessao` (`.claude/skills/fim-de-sessao/SKILL.md`): testes → `git status` → seção 0, REQUISITOS e
  HISTORICO → commit → push → PR → CI → leitura do diff → "pode" → merge.

### Calendário

| data | Eduardo | Marcos | Miguel | Náthally |
|---|---|---|---|---|
| ter 27/10 | ✅ ED0, ED1, ED2, ED5, ED4 (código), ED6; portes MA1 e NA1 | — | — | — |
| qua 28/10 | ED4 consertar a segmentação | revisar o #4; MA2 | MG1 revisar e mesclar o #3 | revisar o #5; NA1 regras v2 |
| qui 29/10 | ✅ ED3 (adiantada); portes NA1 e NA2 (PRs #10 e #11); teste do Docker e do Terraform | MA2: PostgreSQL na `main` + C2 | MG2 Docker + PostgreSQL | ✅ NA1 e NA2 entregues; revisar o #11 |
| sex 30/10 | ED7 (se o #11 entrou); revisões | MA2 | MG2 (`docker-compose.yml`) | NA3 tempo manual |
| sáb 31/10 | revisões; ED8 começa; plano B da MA2 se precisar | **MA2 (prazo)**; MA3 | MG3 Terraform | NA3 tempo manual; marcar testes |
| dom 01/11 | ED7 (prazo final) | MA4 EDA | **MG3: se o Terraform não subiu, fica só o Docker**; MG4 | NA3 |
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
| ED3 | qui 29/10 | ✅ PR #11 | regras v2 da Náthally no prompt: `regras()` lê `avaliacao/regras_prompt.md` | `raiox/ia.py`, `tests/` | Manual | 3 chamadas reais sem item removido por dígito (feito: 0 removidos, US$ 0,0036) | `eduardo-regras-v2` → PR (Náthally lê) |
| ED4 | qua 28/10 | ✅ PR #9 | numa branch nova a partir da `main`: consertar a segmentação real: receita mínima de R$ 10 mi (combinar com o Marcos) e corte dos extremos em 5/95 em `matriz()`; só aceitar o k cujo menor grupo tenha pelo menos 5% das empresas; teste novo para isso; olhar 2 grupos; explicar `matriz()` e o PCA. Os gráficos de antes estão em `data/ed1/*_antes_ed4.png` e servem para a banca ("a silhueta alta enganava") | `raiox/segmentos.py`, `tests/`, `docs/graficos/*.png`, REQUISITOS (k, silhueta) | Plan | nenhum grupo com menos de 5% das empresas; "parecidas" de 3 empresas conhecidas fazem sentido; 2 PNG reais | `eduardo-segmentacao` → PR |
| ED5 | 27/10 | ✅ PR #6 | `avaliacao/avaliar.py` (C4) | `avaliacao/`, `tests/` | — | `python -m avaliacao.avaliar` grava o C4 | `eduardo-ia-testes` |
| ED6 | 27/10 | ✅ PR #6 | teste ponta a ponta (pula sem `data/`) | `tests/test_ponta_a_ponta.py` | — | pula no CI; roda local com dados reais | `eduardo-ia-testes` |
| ED7 | sex 30/10–dom 01/11 | — | `python -m avaliacao.avaliar --com-ia` nos 10 casos (avisar o grupo), depois do #11 | `avaliacao/resultados.csv` | Manual | 10 linhas; custo anotado (~US$ 0,012; limite US$ 0,05) | PR |
| ED8 | qua 04/11 | — | justificativa técnica para o PDF + README "Como usamos IA" | `docs/justificativa.md`, `README.md` | Manual (você escreve; a IA confere com arquivo e linha) | o Marcos lê e entende | PR |
| ED9 | sex 06/11 | — | congelar | só bugs | Plan | CI verde + ponta a ponta verde | **tag `v1.0`** |
| ED10 | sáb 07/11 | — | teste do zero em outra máquina, só com o README | consertos | Manual | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisar |
| ED11 | sex 06/11 | — | avaliação final na `v1.0` (só se a IA mudou depois do ED7) + ensaio de defesa | `resultados.csv` | Plan | 10 perguntas da banca respondidas sem consulta | PR |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 na `main` (27/10) | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | 🟡 PostgreSQL pronto na `tratamento_dados` (`5508116`), fora da `main` | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 | — | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | — | montar o `documentacao.pdf` | `docs/documentacao.pdf` | fora do Claude | BPMN + justificativa + ética + arquitetura | PR |

### Miguel (Claude Code desde 28/10)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | 🟡 aprovação obrigatória tirada (29/10); falta o check `testes` obrigatório, apagar branch após o merge e só merge commit | revisar e mesclar o #3; configurar o GitHub (só merge commit, apagar branch, check `testes`); rodar a tela local | configurações | só leitura | #3 na `main`; print da tela no grupo | merge do #3 |
| MG2 | qui 29–sex 30/10 | 🟡 funciona (Eduardo testou em 29/10: build, testes, health, tela); sem PR; 7 ajustes na seção 0 | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | 🟡 `apply`, `destroy` e `apply` funcionam (29/10); falta montar a `data/` | Terraform (provider docker) com os 2 contêineres (tela + PostgreSQL), **só se o Docker estiver pronto**. Prazo: dom 01/11; senão, corta | `infra/` | Plan | `terraform apply` sobe; `destroy` + `apply` mantém `data/` e o banco | PR |
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
| NA1 | qua 28–qui 29/10 | ✅ regras v2 em 29/10 (na `main` pelo PR #11) | revisar o #5; regras v2 alinhadas ao código (`aprender/seguindo-o-projeto.md`, item 7) | `avaliacao/regras_prompt.md` | PR aberto |
| NA2 | sex 30/10 | ✅ códigos em 29/10 (na `main` pelo PR #10; ela ainda confere) | preencher o `cd_cvm` dos 10 casos (busca da tela ou `indicadores.csv` do Drive; WEG = 5410) | `avaliacao/casos_avaliacao.csv` | `tests/test_ponta_a_ponta.py` passa (o Eduardo roda) |
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
| `tests/test_raio_x.py` | validador (regra de ouro), contrato C3, fonte, modo sem IA nas 30 empresas falsas, prompt (lê as regras da Náthally, chaves preservadas, só marcadores de indicador), texto sem IA na forma da v2, `RAIOX_DADOS`, segmentação (k = 3, 29 de 30; menor grupo ≥ 5%; empresas pequenas fora do treino; `segmentos.csv` refeito quando o código muda), gráficos, checador | Eduardo | sim |
| `tests/test_avaliar.py` | `avaliar.py`: colunas do C4, casos válidos, caso com erro, formato do `casos_avaliacao.csv` (5 colunas, `cd_cvm` inteiro em todos) | Eduardo | sim |
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py` (PR #4) | regras de limpeza, carga da DFP (rede simulada), catálogo e C1 (SQLite hoje; PostgreSQL na MA2) | Marcos | sim; com o PostgreSQL, só se o CI tiver o serviço postgres (senão pulam) |
| `tests/test_contratos.py` (MA2) | C1 e C2 com os falsos: CSV padrão, `cd_cvm` int | Marcos | sim |
| `tests/test_tela.py` (MG4) | a tela com os falsos: busca, gerar, 6 métricas, sem erro | Miguel | sim |
| `tests/test_ponta_a_ponta.py` | C2 real, raio-x sem IA de 3 setores, `cd_cvm` dos casos (todos preenchidos e na tabela real) | Eduardo | **não**: pula sem `data/`. Rodar local antes de `v0.1-demo`, `v1.0` e no teste do zero |
| `tests/test_aprender.py` | o notebook `aprender/passo_a_passo.ipynb` roda inteiro e vai para o Git sem saídas | Eduardo | sim |
| Docker | `curl localhost:8501/_stcore/health` → `ok` | Miguel | não (checklist da demo) |

---

## 5. Pontos de integração

| data | quem | o que sincroniza | o que congela |
|---|---|---|---|
| qua 28/10 | Miguel → todos | #3 na `main`; os outros PRs fazem `git merge main` | arquivos de padronização |
| qua 28/10 | Eduardo → Náthally | 3 raio-x reais | — |
| sáb 31/10 | Marcos → todos | PostgreSQL na `main` e C2 cumprido (MA2) | formato e colunas do C2; `DATABASE_URL` |
| sex 30/10 | Marcos → todos | `data/` v1 no Drive | — |
| ✅ qui 29/10 | Náthally → Eduardo | regras v2; casos com `cd_cvm` (PRs #10 e #11) | texto das regras e formato do C4 |
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
| qua 28/10 | o `carregar_dfp.py` não roda na máquina do Eduardo | o Marcos manda a `data/` dele; em último caso, 3 raio-x com a tabela falsa |
| sáb 31/10 | a MA2 (PostgreSQL na `main`) atrasa | o Eduardo porta o `5508116` com o Claude Code e o Marcos revisa (dupla de reserva); prazo final ter 03/11, quando as interfaces congelam. **SQLite não é plano B** (regra do professor) |
| ter 03/11 | o PostgreSQL não sobe no Docker na demo | `docker compose up` ensaiado no teste do zero (ED10); vídeo gravado (MG6/MG7); a busca falsa (`falsos/`) ainda mostra a tela sem banco |
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
No Claude Code, `/explicar raiox/segmentos.py matriz` (por exemplo) segue esse método e termina com 3 perguntas como as da banca (`.claude/skills/explicar/SKILL.md`).

---

## Se começássemos do zero (para aprender, não para refazer)

1. **Matriz do guia com dono** no dia 1, antes de qualquer código.
2. **Contratos com o formato do arquivo** e falsos no mesmo formato. Os bugs do CSV com `;` e do `cd_cvm` como texto são de contrato.
3. **Repositório-esqueleto** feito por uma pessoa, de onde todos clonam, com CI e versões fixas desde o início.
4. **Docker "olá mundo"** na primeira semana.
5. **Cada um trabalhando contra os falsos**, com integração semanal e tag.
