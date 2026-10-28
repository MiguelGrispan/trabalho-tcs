# Plano até a banca (versão acelerada)

Versão de **ter 27/10/2026, noite** (seção 0 atualizada em qua 28/10). Meta: **feito, não perfeito**. O código congela na **sex 06/11** e tudo fica pronto
para entregar na **qua 11/11**, com folga até a entrega de seg 16/11. Se a banca cair na semana de 09–15/11, já estamos prontos.

A matriz do que o guia exige está em [REQUISITOS.md](REQUISITOS.md). Os detalhes técnicos do que estava quebrado, com
comandos de prova, estão em [aprender/seguindo-o-projeto.md](../aprender/seguindo-o-projeto.md).

**Como usar este plano:**
- Cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (por exemplo, MA2).
- Para começar, abra o Claude Code e diga:
  > Leia o CLAUDE.md e faça a sessão MA2 do docs/PLANO.md.
- **Ao terminar uma sessão:**
  1. atualize a seção 0 (situação atual) e a coluna "status" da sessão, no mesmo PR;
  2. se a sessão fecha uma linha do REQUISITOS.md, atualize essa linha também.

**Hipóteses deste plano:**
- Cada pessoa tem de 6 a 12 h por semana, fora a aula.
- Eduardo, Marcos e Miguel usam Claude Code (o Miguel desde 28/10). A Náthally não usa IA para programar: ela sobe arquivos pelo navegador.
- Banca prevista para **qua 18/11 (a confirmar)**.

---

## 0. Situação atual (atualize a cada sessão)

**Em qua 28/10, 11h30** (sessão do Eduardo com o Claude Code: documentos, guia e skills do Claude Code, ED4, plano da Náthally).

**Retomando numa sessão nova do Claude Code?**
1. Cole: "Leia o CLAUDE.md e a seção 0 do docs/PLANO.md. Confira o estado real com `gh pr list --state all` e
   `git log --oneline -15`. Depois faça a sessão ED3" (só se as regras v2 da Náthally já chegaram; se não, adiante a ED8,
   que não depende de ninguém). Guia de como usar o Claude Code: `aprender/claude-code.md`.
2. Antes de mexer em qualquer coisa, a sessão deve dizer o que mudou desde esta nota.

**O que mudou desde 27/10, noite:**
- **ED4 feito (PR #9, `eduardo-segmentacao`; depende do #7).** Os grupos com os dados reais agora fazem sentido:
  - o modelo aprende só com as empresas com receita a partir de R$ 10 mi (562 de 595), corta os extremos em 5/95 e só aceita
    um k cujo menor grupo tenha pelo menos 5% das empresas (`raiox/segmentos.py`: `treino()`, `matriz()`, `escolher_k()`);
  - resultado: k = 4, silhueta 0,30, grupos de 330, 99, 74 e 59 empresas no treino (`python -m raiox.segmentos`);
  - as 33 empresas menores continuam com raio-x: entram no grupo mais perto e recebem parecidas do treino;
  - os 4 grupos: **grandes e estáveis** (333 empresas, receita mediana R$ 3,3 bi, margem EBIT 14%), **crescimento acelerado**
    (65; +126% em 2 anos: Minerva, Aegea, Eneva), **no prejuízo** (90; margem EBIT −8%: Braskem, Oncoclínicas) e **margem muito
    alta** (107; margem EBIT 55%: energia elétrica, concessões, B3, Itaúsa);
  - **decisão sobre o setor:** as parecidas têm o mesmo perfil financeiro, não o mesmo setor (WEG → Cemig, Copel; Magazine Luiza →
    Ultrapar, Vibra, BRF). O filtro de setor já estava cortado (seção 7); isso se explica na banca;
  - gráficos de antes e depois em `docs/graficos/` (a silhueta 0,77 de antes "enganava");
  - o `data/segmentos.csv` agora é refeito quando o código do modelo muda;
  - o notebook `aprender/passo_a_passo.ipynb` chama as funções em vez de copiar o código;
  - **falta:** o Marcos confirmar o corte de R$ 10 mi (constante `RECEITA_MINIMA`), na MA3.
- **Claude Code para o time (PR #8):** o guia `aprender/claude-code.md` (frase de abertura, modos, limites, fim de sessão) e as
  skills `/explicar` (treino para a banca) e `/fim-de-sessao` (regra 3 do CLAUDE.md), em `.claude/skills/`.
- **O Miguel passou a usar o Claude Code** (28/10): os 3 que programam usam a mesma ferramenta.
- **Merge simulado em 28/10, na ordem #7 → #8 → #9:** sem conflito. Revisão: #7 e #8, Miguel ou Marcos; #9, Marcos (corte de R$ 10 mi).
- **Os PRs #3 a #6 entraram na `main`** em 27/10 (o Miguel fez o merge). O CI ficou verde nos 4 merges.
- **Testes:**
  - no CI, sem `data/`: 61 passed e 3 skipped (rodada 40544159668);
  - na máquina do Eduardo, com a `data/` real: 64 passed na `main` e 68 passed com o #9 (4 testes novos da segmentação). O erro do teste do C3 sumiu.
- **Branches apagadas em 28/10**, porque já estavam inteiras na `main` (`git branch -r --merged origin/main`): `eduardo`, `fundacao`,
  `eduardo-padronizacao`, `eduardo-ia-testes`, `marcos-porta-dados` e `nathally-produto`. Se precisar de uma, o botão
  "Restore branch" fica na página do PR.
- **Ficaram 3 branches:**
  - `tratamento_dados` (Marcos) e `feat/metricas` (Náthally): o conteúdo foi portado pelos #4 e #5, mas o Git não as vê
    como mescladas, porque não têm história em comum com a `main`. Só apagar com o OK do dono.
  - `docs-docker-e-terraform` (Miguel, 27/10): `Dockerfile`, `.dockerignore`, `terraform/` e uma mudança no `.gitignore`.
    **Ainda sem PR.** O conteúdo não foi revisado. Na revisão, conferir: a pasta é `terraform/`, mas CLAUDE.md, README e
    este plano dizem `infra/` (escolher um nome e acertar os documentos no mesmo PR); o `.gitignore` é arquivo comum.
- **Configuração do GitHub (MG1) ainda pendente:** "apagar branch após o merge" está desligado e squash e rebase continuam permitidos
  (`gh api repos/MiguelGrispan/trabalho-tcs`). A proteção da `main` só o Miguel consegue ver (precisa ser admin).
- **README:** pedia Python 3.10; agora pede 3.14, igual ao CI e ao `requirements.txt` (este PR).

**Progresso estimado** (Eduardo, 27/10; não mudou, porque nenhum código novo entrou desde então):

| parte | feito | falta |
|---|---|---|
| núcleo do produto: dados, ML, IA, validador, avaliação | ~75% | MA2, ED3, ED7 (ED4 feito em 28/10) |
| tela e infraestrutura | ~25% | MG2 a MG4 (Docker e Terraform começaram na branch do Miguel, sem PR) |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~10% | quase tudo, mas não depende de código novo |
| **total** | **~40%** | com 8 de 26 dias usados (~31%): ainda à frente no código e atrás na infra |

**Folga:** o plano termina na qua 11/11. Sobram 4 dias de reserva (12 a 15/11) antes da entrega de seg 16/11, e mais 2 até a banca.
Regra: atraso come a folga; **nunca** se acrescenta escopo. Se a folga acabar, use a lista de cortes da seção 7.

**Para quem está aprendendo:** a pasta [aprender/](../aprender/README.md) reúne os comandos (o que rodar, em qual pasta),
os guias e o notebook `passo_a_passo.ipynb`, que segue uma empresa do começo ao fim. Nada nela é usado pelo código.

**Dados reais (ED1, 27/10):**
- **Carga:** os scripts do Marcos rodaram em 22 s e geraram 595 empresas, todas com DFP 2025.
- **Conferência:** a receita da WEG bate com a conferência do Marcos.
- **Formato:** o `indicadores.csv` ainda sai com `;` e vírgula decimal (`scripts/indicadores.py:24`). O Eduardo converteu só na `data/` dele, até a MA2.
- **Raio-x:** 3 gerados com IA (Camil, Magazine Luiza, WEG), sem nenhum item removido pelo validador, por US$ 0,0026 no total. Estão em `data/ed1/` (fora do Git, só na máquina do Eduardo).
- **Problema achado (resolvido no ED4, 28/10):**
  - com os dados reais, o K-means escolhe k = 4 com silhueta 0,77, mas um grupo tem 567 das 595 empresas e os outros têm 9, 9 e 10;
  - a silhueta alta só mede a separação das empresas extremas (margens de −10.000%);
  - com isso, o "grupo" vira quase todas as empresas, e as "parecidas" não fazem sentido.
- **Conserto:** veja o ED4 em "O que mudou", acima.

**Pendências da revisão de 27/10:**
- **Regra de ouro:** o validador já barra número por extenso, ½, ² e produto numérico (`test_regra_de_ouro_*`, na `main` desde o #6).
  **Falta:** o prompt (`REGRAS` em `raiox/ia.py`) ainda não proíbe número por extenso; a regra 1 da v1 da Náthally já proíbe (`avaliacao/regras_prompt.md:49`). Fazer na ED3.
- **Testes que não pegaram o código estragado de propósito** (consertar quem é dono):
  - Eduardo: o `tests/test_aprender.py` exige exatamente "5 passed" no notebook (a célula 9 já chama as funções, desde o ED4).
  - Marcos: `test_resolver_conflitos_trata_valor_vazio_como_divergente` passa só pela ordem das linhas; `test_obter_indicadores_deixa_ausente_…` não olha o `ativo_total`; `test_calcular_exporta_…` não tem receita de 2 anos antes igual a zero.
  - Eduardo: `test_casos_avaliacao_do_repositorio_segue_o_c4` não confere a coluna `empresa`; `test_casos_de_avaliacao_existem_na_tabela_real` passa sem testar nada enquanto os `cd_cvm` estiverem vazios.
- **Outros achados:** com dados reais, a tela mostra "empresas e números inventados" (MG4); o C4 diz que o `conferencia.csv` é da Náthally, mas quem escreve é o Marcos.

**Próximo passo de cada um:**
- **Miguel:** abrir o PR da `docs-docker-e-terraform` (MG2; o Eduardo revisa) e terminar a MG1 (só merge commit, apagar branch após o merge, check `testes` obrigatório).
- **Marcos:** MA2 (CSV padrão e `cd_cvm` int). Dizer se a `tratamento_dados` pode ser apagada. Na MA3, decidir o corte de receita mínima junto com o Eduardo.
- **Náthally:** só 2 coisas travam o código, as duas até sex 30/10:
  1. **regras v2** (NA1, `avaliacao/regras_prompt.md`), com base no `data/ed1/raiox_para_nathally.md` (fora do Git: o Eduardo manda).
     O que mudar, conferido no código:
     - a IA não recebe o nome da empresa nem o ano (`raiox/ia.py:96`);
     - a posição tem 4 valores: acima, abaixo, em linha e sem dado (`raiox/ia.py:85-87`);
     - o resumo tem 2 ou 3 frases no código e de 2 a 4 na v1;
     - o valor do grupo vira "do grupo ({x_grupo})";
     - as lacunas num formato só;
     - decidir se limita adjetivos;
  2. **OK nos `cd_cvm` dos 10 casos** (NA2). O Eduardo levantou os códigos na `data/` real e preenche com o OK dela:
     Camil 24228, CSN 4030, Magazine Luiza 22470, Petrobras 9512, Embraer 20087, Suzano S.A. 13986 (ou a holding 9067),
     RD Saúde 5258, Localiza Rent a Car 19739 (ou a Fleet 24813), WEG 5410, Telefônica 17671.
  - O resto é entrega dela e não trava o código: tempo manual e ROI, testes com usuários, revisão dos 10 raio-x (depois da ED7),
    texto de ética (o Marcos precisa até 07/11) e o deck. Dizer se a `feat/metricas` pode ser apagada.
- **Eduardo:**
  1. ✅ 28/10: mensagem enviada à Náthally e revisão dos PRs pedida ao grupo. Confirmar se o `data/ed1/raiox_para_nathally.md` foi junto;
  2. preencher o "Eu conferi" dos PRs #7, #8 e #9 e pedir as revisões; depois do merge, `git switch main` e `git pull`;
  3. pedir ao Marcos o OK do corte de R$ 10 mi;
  4. adiantar a ED8 (justificativa técnica), que não depende de ninguém, enquanto as regras v2 não chegam;
  5. estudar o ED4 com `/explicar raiox/segmentos.py segmentar` (seção 8), depois do merge do #9;
  6. revisar o PR do Docker quando o Miguel abrir; ED3 quando chegarem as regras v2; ED7 quando os `cd_cvm` estiverem preenchidos.

**Decisões em aberto:**
- data e horário da banca;
- `scripts/dados.py` e `raiox/dados.py`: ficar com um só (Marcos decide);
- nome da pasta da infraestrutura: `infra/` ou `terraform/` (Miguel, no PR do Docker);
- apagar `tratamento_dados` e `feat/metricas` (Marcos e Náthally);
- Suzano e Localiza nos casos de avaliação: qual das duas empresas de cada uma (Náthally).

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
| ED4 | qua 28/10 | ✅ PR #9 | numa branch nova a partir da `main`: consertar a segmentação real: receita mínima de R$ 10 mi (combinar com o Marcos) e corte dos extremos em 5/95 em `matriz()`; só aceitar o k cujo menor grupo tenha pelo menos 5% das empresas; teste novo para isso; olhar 2 grupos; explicar `matriz()` e o PCA. Os gráficos de antes estão em `data/ed1/*_antes_ed4.png` e servem para a banca ("a silhueta alta enganava") | `raiox/segmentos.py`, `tests/`, `docs/graficos/*.png`, REQUISITOS (k, silhueta) | Plan | nenhum grupo com menos de 5% das empresas; "parecidas" de 3 empresas conhecidas fazem sentido; 2 PNG reais | `eduardo-segmentacao` → PR |
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
| MA1 | 27/10 | ✅ PR #4 na `main` (27/10) | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qua 28–qui 29/10 | — | cumprir C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `tests/test_contratos.py` | Plan | `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-csv-padrao` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 | — | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | — | montar o `documentacao.pdf` | `docs/documentacao.pdf` | fora do Claude | BPMN + justificativa + ética + arquitetura | PR |

### Miguel (Claude Code desde 28/10)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | 🟡 #3 na `main` (27/10); falta configurar o GitHub | revisar e mesclar o #3; configurar o GitHub (só merge commit, apagar branch, check `testes`); rodar a tela local | configurações | só leitura | #3 na `main`; print da tela no grupo | merge do #3 |
| MG2 | qui 29–sex 30/10 | 🟡 branch `docs-docker-e-terraform`, sem PR | `Dockerfile` + `.dockerignore` (tela, `data/` como volume, chave por variável) | `Dockerfile`, `.dockerignore` | Plan | `docker build`, `docker run -p 8501:8501 …`, `curl localhost:8501/_stcore/health` → `ok` | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | 🟡 `terraform/` na mesma branch, sem PR | Terraform (provider docker), **só se o Docker estiver pronto**. Prazo: dom 01/11; senão, corta | `infra/` | Plan | `terraform apply` sobe; `destroy` + `apply` mantém `data/` | PR |
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
| NA1 | qua 28–qui 29/10 | 🟡 PR #5 na `main` (27/10); faltam as regras v2 | revisar o #5; regras v2 alinhadas ao código (`aprender/seguindo-o-projeto.md`, item 7) | `avaliacao/regras_prompt.md` | PR aberto |
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
| `tests/test_raio_x.py` | validador (regra de ouro), contrato C3, fonte, modo sem IA nas 30 empresas falsas, `RAIOX_DADOS`, segmentação (k = 3, 29 de 30; menor grupo ≥ 5%; empresas pequenas fora do treino; `segmentos.csv` refeito quando o código muda), gráficos, checador | Eduardo | sim |
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
| `raiox/segmentos.py`, `treino()` e `matriz()` | por que só receita a partir de R$ 10 mi, por que a receita entra em log, por que cortar extremos em 5/95, por que a mediana nos nulos, o que o `StandardScaler` faz |
| `raiox/segmentos.py`, `segmentar()` e `escolher_k()` | K-means, silhueta, por que k vai de 3 a 8, por que a silhueta 0,77 enganava e a regra dos 5%, `NearestNeighbors` com 6 vizinhos |
| `raiox/segmentos.py`, `grafico_grupos()` | o que o PCA faz e o que significa "39% + 20% da variação" nos eixos |
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
