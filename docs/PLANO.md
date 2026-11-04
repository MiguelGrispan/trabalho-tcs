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

**Em qua 04/11, ~9h** (MA6, Eduardo com o Claude Code; antes, ~8h30, o fim da MG4b, Miguel com o Claude Code).
Na `main`: PRs #1 a #16, #19 a #41, #46 (MA3) e #47 (MG4b). Aberto: o da MA6 (branch `eduardo-documentacao`), que só entra
depois do ok do grupo.
A versão longa desta seção, até 03/11, ficou no Git: `git show 9f85bc9:docs/PLANO.md`. O resumo de cada dia está no [HISTORICO.md](HISTORICO.md).

**Faltam 2 dias para o código congelar (sex 06/11) e 12 para a entrega (seg 16/11).**

### O que já funciona (conferido)
- **Demo ponta a ponta** no `docker compose` e no Terraform (Mac do Eduardo, 03/11), tag `v0.1-demo` (`9689db9`): busca no
  PostgreSQL, raio-x sem IA (Vale, Embraer, Ambev) e com o Gemini (WEG, US$ 0,0011), cada consulta gravada na `consultas`.
  Com o Gemini fora do ar (chave falsa), a tela cai no modo sem IA, avisa e grava a consulta com custo 0.
- **MA3 na `main`** (PR #46, Marcos, 03/11; fecha as issues #42 e #17): a busca devolve só companhias ativas e com indicadores, com o
  `cd_cvm` como número; a tabela `indicadores` está no PostgreSQL; o "ano" é o do exercício (`ano_do_exercicio()`, `raiox/limpeza.py`):
  a Camil (mar/2025 a fev/2026) tem receita de R$ 11,12 bi e crescimento de −1,2%, e mudam só as 9 empresas que fecham fora de dezembro.
  13 valores de 5 empresas conferidos no RI, todos com 0,00% (`avaliacao/conferencia.csv`). Corte de R$ 10 mi confirmado pelo Marcos
  (`scripts/avaliar_corte_receita.py`: abaixo, 31 empresas, 52% com |margem EBIT| > 100%; acima, 564 e 4%). Com o banco desligado,
  a conexão desiste em 5 s (`raiox/banco.py`).
- **MG4b (PR #47, Miguel, 03/11): a tela não se contradiz quando a IA falha** (`guia_projeto_final.pdf` §5: "a interface é
  amigável ao usuário?", 20%; segurança de dados, 15%). Conferido no Linux do Miguel com
  `GOOGLE_API_KEY=chave-falsa-teste RAIOX_IA_REAL=1 docker compose up -d --build` e a WEG (0 tokens):
  - o aviso tem uma frase; o erro do Google fica em "Detalhes técnicos" e no `docker compose logs tela` (#38);
  - o topo diz "Texto montado sem IA: o Gemini não respondeu.", e o rodapé só diz "escrito por IA" quando o Gemini respondeu (#39);
  - o compose publica a tela só em `127.0.0.1`, como o Terraform (#44): `docker compose ps` → `127.0.0.1:8501->8501/tcp`; pelo IP da rede, não responde;
  - os avisos de banco vazio e de banco desligado também dão os comandos de quem subiu pelo Terraform (`infra/main.tf`).
- **Terraform no Linux do Miguel (03/11 de manhã, Claude Code; anotado na MG4b, não refeito nela):** a tela nova da MG4 sobe pelo
  `infra/` e avisa do banco vazio. Com `contas` e `empresas` copiadas do banco do compose (`pg_dump`, sem baixar a CVM), gera a WEG
  (receita R$ 40,8 bi) e grava a consulta na `consultas` do `raiox-banco`; `docker exec raiox-tela python -m pytest -q tests/test_tela.py` → 8 passed.
- **Recarga da CVM com o #46 no Linux do Miguel (04/11, branch da MG4b com a `main` mesclada):** `carregar_dfp.py` (2.567 empresas,
  660 ativas, 384.591 linhas, ~1 min 30 s com o download) e `indicadores.py` (595 linhas na tabela `indicadores`). Camil (24228):
  receita R$ 11,12 bi e crescimento −1,2%, no banco e na tela, e a consulta gravada na `consultas` com `cd_cvm` número.
  **Achado: issue #48 (Marcos)**: o `indicadores.py` novo grava a `data/indicadores.csv` como `-rw-------`, e a tela (`appuser` no
  contêiner) não lê: todo raio-x falha com `Permission denied`. Contorno até o conserto: `chmod 644 data/indicadores.csv` e
  `docker compose restart tela` depois de cada recarga.
- **Testes:** 244 passed, nenhum pulado (Linux do Miguel, com o PostgreSQL ligado, a branch da MG4b com o #46 mesclado, 04/11).
  No Windows do Marcos, 241 passed com `PYTHONUTF8=1` (03/11 ~12h, branch do #46); sem ele, 8 testes das travas falham (issue #45).
  No Mac do Eduardo, sem o PostgreSQL ligado (04/11, branch da MA6 com o #47 mesclado): 218 passed e 26 skipped (os do banco).
- **Textos-base:** `docs/justificativa.md` (ED8; falta o Marcos ler) e `docs/etica.md` (base da NA5; atualizado em 04/11 com o resultado da MA3).
- No Mac, o Terraform só acha o Docker com `export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock` (`README.md:158`).

### MA6 (Eduardo, 04/11): rascunho 1 do documento do projeto
- **`docs/documentacao.md`** (o texto, que se edita) e **`docs/documentacao.pdf`** (13 páginas, gerado do markdown). Atende o
  `requisitos_projeto.MD`, Documentação ("as etapas desenvolvidas durante o processo") e o guia §6, Documentação do Projeto (PDF):
  BPMN 2.0, justificativa técnica (RAG × fine-tuning) e análise de ética e segurança. Seções: problema, etapas (do HISTORICO), dados
  e limpeza (as 7 regras, conferidas no código de hoje), BPMN, arquitetura, justificativa (do `justificativa.md`), ética e segurança
  (do `etica.md`), métricas, vibecoding e lições. **Apêndice A:** de onde vem cada número e o comando que confere. **Apêndice B:** o que falta.
- **Números conferidos em 04/11:** K-means refeito em memória, sem gravar nada, com os dados locais de 30/10 (k = 4, silhueta 0,293,
  grupos de 327, 76, 59 e 102, 564 no treino); `avaliacao/resultados.csv` (10 casos, 0 removidos, US$ 0,0118, 2,19 s em média);
  `avaliacao/conferencia.csv` (13 linhas, todas 0,00%).
- **Achados, marcados no PDF:** os 10 raio-x do `resultados.csv` são de 29/10, antes da correção da Camil (o dela usou receita de
  R$ 12,3 bi; custo, tempo e removidos não mudam). Os PNG de `docs/graficos/` são de 28/10 (a legenda dos grupos diz 333, 65, 90 e 107).
- **Gerar o PDF de novo:** `~/bootcamp/bin/python ~/projeto_final_tcs/gerar_pdf_documentacao.py ~/projeto_final_tcs/trabalho-tcs`
  (o script fica fora do repositório, no Mac do Eduardo: `mistune` converte o markdown e o Chrome salva em PDF).
- **Quando entrar na `main`:** o Marcos troca a citação do `raiox/limpeza.py:3-4` (hoje aponta para o `docs/Raio-X Comercial.pdf`,
  de 20/10, que ainda fala de SQLite) pela seção 3 do `docs/documentacao.pdf`, e o PDF velho sai (combinado com ele em 04/11).

### Issues abertas
- **#43** (Eduardo, ED13): a tela aberta antes de carregar a CVM não acha a empresa até ser reiniciada (cache em `raiox/ia.py:51`).
- **#45** (Eduardo, ED14): no Windows, as travas leem o Git em cp1252 e bloqueiam commit e merge.
- **#48** (Marcos, MA3b, achada pelo Miguel em 04/11): o `indicadores.py` novo grava a `data/indicadores.csv` como `-rw-------`, e a
  tela no contêiner não lê: todo raio-x falha com `Permission denied`. Contorno: `chmod 644 data/indicadores.csv` e
  `docker compose restart tela` depois de cada recarga.
- As #38, #39 e #44 foram fechadas pelo #47 (MG4b).

### Caminho crítico (o que trava os outros)
1. **A recarga dos dados com o #46.** Cada um roda de novo `python scripts/carregar_dfp.py` e `python scripts/indicadores.py` (os dois
   precisam do PostgreSQL ligado) e reinicia a tela (o cache da #43 guarda a tabela velha). Sem a tabela `indicadores`, a busca não
   acha nada e a tela diz "O banco está vazio". **No Linux, até a #48 ser consertada:** depois da recarga, `chmod 644 data/indicadores.csv`,
   senão a tela não gera nenhum raio-x. Depois, o Eduardo refaz o `python -m raiox.segmentos`, os PNG e os números do K-means na
   seção 6 do PDF.
2. **Os entregáveis.** O código está perto do fim; o que falta é documento: BPMN (MA5), EDA (MA4, atrasada), diagrama de arquitetura
   (MG5), ética final (NA5), ROI (NA3), deck (NA6) e vídeo (MG6 e MG7). O PDF (MA6) já tem o rascunho 1: cada parte que chega entra
   no lugar marcado com [PENDENTE], sem refazer o resto.
3. **Proposta da revisão de 03/11: congelar também o processo.** Até 16/11, nenhuma regra, trava ou guia novo para o time: só o que
   fecha uma linha do [REQUISITOS.md](REQUISITOS.md).

### Próximo passo de cada um
- **Marcos:** **MA3b, a #48** (qui 05/11, antes do vídeo v0) → zip da `data/` no Drive, com o link no grupo (fecha a MA3) → MA5 BPMN (até qui 05/11; o `.png` entra na seção 4 do
  PDF) → MA4 EDA (os gráficos entram na seção 3). Ler a `docs/justificativa.md` e revisar o rascunho do PDF até sáb 07/11. Quando o
  PR da MA6 entrar: trocar a citação do `raiox/limpeza.py` e tirar o `docs/Raio-X Comercial.pdf`. Apagar a `tratamento_dados`
  pelo site do GitHub. Um PR pequeno, com o ok do Eduardo, tirando `verificar_automatico.py` e `yfinance` (cortados na seção 7).
- **Miguel:** ✅ MG4b (#47: #38, #39 e #44) → ✅ recarga da CVM no banco do compose (04/11, com o contorno da #48) → MG5 diagrama e
  README (o `docs/arquitetura.png` entra na seção 5 do PDF) → MG6 roteiro e vídeo v0 (qui 05/11), gravado no Mac do Eduardo.
  Avisar o grupo das mudanças em pastas comuns: `tests/test_tela.py` (MG4b) e, da MG4, `.env.example` e `aprender/`.
- **Náthally (obrigatório):** NA3 ROI mínimo (até qui 05/11; entra nas seções 1 e 7.7 do PDF) → NA4 slide de métricas (os números da
  seção 8 do PDF) → NA5 ética: reescrever a seção 7 do PDF a partir do `docs/etica.md` (sáb 07 a dom 08/11) → NA6 deck.
- **Eduardo:** merge do PR da MA6 quando o grupo liberar → ED13 (#43) → ED14 (#45) → recarga e K-means refeito → ED9 tag `v1.0` e
  ED11 (sex 06/11) → ED10 teste do zero (sáb 07/11) → MA6 final (seg 09/11): encaixar BPMN, arquitetura, ética e ROI, conferir o
  Apêndice A na `v1.0` e tirar o Apêndice B. Perguntar ao professor a data da banca e as perguntas 2 e 3 do REQUISITOS; treinar a
  defesa com `/explicar` (seção 8).

### Decisões
- **Decidido em 04/11** (mensagem do Marcos, aceita pelo Eduardo):
  - a MA6 (o documento) passa ao Eduardo; o Marcos fica com a MA5 (BPMN) e a MA4 (EDA);
  - a demo da banca roda no Mac do Eduardo, o único conferido com compose, Terraform e Gemini no mesmo dia (03/11; o Linux do Miguel
    tem compose e Terraform com a tela nova, mas o Gemini de verdade só pelo Terraform em 31/10); o Miguel grava nele o vídeo v0
    (qui 05/11) e o final (sáb 07/11, na `v1.0`), para a banca ver o mesmo que o vídeo;
  - o documento é escrito em markdown e o PDF é gerado dele: o PR mostra o que mudou e cada número pode ser conferido;
  - o `docs/Raio-X Comercial.pdf` sai quando o PDF novo entrar na `main`.
- **Em aberto:**
  - data e horário da banca; perguntas 2 e 3 ao professor (Eduardo);
  - `scripts/dados.py` ou `raiox/dados.py` (ficar com um só; Marcos);
  - apagar a `feat/metricas` (Náthally; antes, subir o `revisao_manual.md`, se ela quiser);
  - as 3 notas do código (`NOTAS_DO_CODIGO`, em `raiox/ia.py`) vão para a v3 das regras? (Náthally).
- **Decidido pelo Marcos em 03/11:** o `verificar_automatico.py` e o `yfinance` saem num PR separado (falta o ok do Eduardo, porque
  mexe em `tests/` e no `requirements.txt`); o `scripts/graficos.py` fica até a MA4 (pode virar a base do `notebooks/eda.ipynb`;
  `guia_projeto_final.pdf` §2: "Visualização explicativa dos dados"); a `tratamento_dados` será apagada.

### Pendências pequenas (não travam)
- Eduardo: `tests/test_aprender.py:19` exige exatamente "5 passed" no notebook.
- Marcos: 3 testes fracos: `test_resolver_conflitos_trata_valor_vazio_como_divergente` (`tests/test_limpeza.py`) passa só pela ordem
  das linhas; `test_obter_indicadores_deixa_ausente_indicador_de_conta_ausente` (`tests/test_dados.py`) não olha o `ativo_total`;
  `test_calcular_exporta_…` não tem receita de 2 anos antes igual a zero.
- O C4 (`contratos.md`) diz que o `avaliacao/conferencia.csv` é da Náthally, mas quem escreve é o Marcos: corrigir com o ok dos dois.
- Limite conhecido do ano do exercício (`raiox/limpeza.py`, `ano_do_exercicio`): quem muda a data de fechamento pode ter duas DFPs no
  mesmo ano, e aí os valores divergentes ficam vazios (o `carregar_dfp.py` avisa "contas repetidas"). Nos dados de 03/11, nenhum valor
  vazio a mais. Achado do `revisor` no #46; serve para a ética (limites).
- A fonte do raio-x da Camil diz "DFP 2025" (o exercício 2025 dela), mas o arquivo da CVM é o de 2026: mostrar a data de fim do
  exercício seria a opção 2 da #17, que muda o C2 e o C3 (Eduardo e Miguel; não decidido).
- PostgreSQL local: o do compose usa a porta 5432; quem ainda tem o `raiox-postgres` antigo (do `docker run` de 29/10) para um
  dos dois (`docker stop raiox-postgres`) ou usa `PORTA_BANCO=5433`.

### Progresso estimado (Claude, 04/11: estimativa pelo esforço que falta, não medida)

| parte | feito | falta | horas que faltam |
|---|---|---|---|
| núcleo: dados, ML, IA, validador, avaliação | ~94% (com o #46) | #43, #45, #48; recarga e gráficos do K-means refeitos | 2 a 3 h |
| tela e infraestrutura | ~90% (depois da MG4b) | MG5 (diagrama e README) | 2 a 3 h |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~25% (PDF no rascunho 1, com justificativa e ética como base) | BPMN, EDA, deck, vídeo, ensaios; PDF final | 20 a 30 h |
| **total** | **~63%** | 15 de 27 dias usados (21/10 a 16/11) | **24 a 36 h**, para uns 40 a 80 h de capacidade do grupo até 16/11 |

**Folga:** 4 dias de reserva (12 a 15/11) antes da entrega de seg 16/11, e mais 2 até a banca.
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
| ter 03/11 | ✅ **demo ponta a ponta · tag `v0.1-demo`** (compose e Terraform no Mac); revisão geral (issues #42 a #44) | MA4 (atrasada); ✅ MA3: PR #46 (#42, #17) | ~~MG4~~ (feita em 02/11); ✅ MG4b adiantada (#47) | NA3 ROI mínimo |
| qua 04/11 | 🟡 **MA6 rascunho 1** (PDF; merge quando o grupo liberar); **ED13: issue #43** (~30 min); ✅ ED8 (feita em 02/11) | ~~PR da MA3 e #17~~ (PR #46, 03/11); zip da `data/`; MA5 BPMN | ~~MG4b~~ (#47, merge em 04/11); recarga da CVM; MG5 arquitetura + README | NA4 slide de métricas |
| qui 05/11 | só bugs; **ED14: issue #45** (travas no Windows) | **MA3b: issue #48** (~20 min); MA5 | MG6 vídeo v0 | NA3 (prazo do ROI mínimo) |
| sex 06/11 | **ED9: código congelado · tag `v1.0`**; ED11 avaliação final | | | |
| sáb 07/11 | ED10 teste do zero | revisar o rascunho do PDF (MA6) | MG7 vídeo final na `v1.0` | NA5 ética |
| dom 08/11 | **todos mandam o conteúdo dos slides à Náthally** | | | NA5 deck |
| seg 09/11 | MA6 PDF final | | | NA6 deck final |
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
| ED13 | qua 04/11 | — | consertar a **issue #43**: a tela aberta antes de carregar a CVM não acha a empresa (cache de `_base()`, `raiox/ia.py:51`). Guia §5: "funciona de ponta a ponta?" | `raiox/ia.py`, `tests/test_raio_x.py` | Manual | o passo a passo da #43 gera o raio-x da WEG; teste novo com essa ordem | PR que fecha #43 |
| ED14 | qui 05/11 | — | consertar a **issue #45**: no Windows, o `guarda.py` lê a saída do Git em cp1252 (`.claude/hooks/guarda.py:89`), bloqueia commit e merge com `”` ou emoji no diff, e 8 testes das travas falham. Guia §2: "agentic coding" | `.claude/hooks/guarda.py`, `tests/test_guarda.py` | Manual | no Windows do Marcos, sem `PYTHONUTF8`: `python -m pytest -q tests/test_guarda.py` sem falhas e um commit com `”` no diff passa pela trava | PR que fecha #45 |
| MA6 | qua 04–seg 09/11 | 🟡 rascunho 1 em 04/11 (branch `eduardo-documentacao`; o merge espera o ok do grupo). Passou do Marcos ao Eduardo em 04/11 | montar o documento do projeto: etapas desenvolvidas (R Documentação; base: `docs/HISTORICO.md`) + BPMN (MA5) + arquitetura (MG5) + justificativa (ED8) + ética e segurança (`docs/etica.md` e NA5) + métricas (`avaliacao/resultados.csv` e `conferencia.csv`) (G §6) | `docs/documentacao.md`, `docs/documentacao.pdf` | Manual (o Claude monta a partir das fontes; o Eduardo lê e confere) | o PDF tem as partes acima, sem [PENDENTE], e cada número bate com o arquivo de onde veio (Apêndice A) | PR (rascunho) e PR (final, seg 09/11) |
| ED12 | sáb 31/10 | ✅ PR #30 (na `main` em 02/11) | travas do Claude Code (R14 e guia §2, agentic coding): `.claude/settings.json`, `.claude/hooks/guarda.py`, subagent `revisor`, import do `requisitos_projeto.MD` | `.claude/`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `aprender/claude-code.md`, `tests/test_guarda.py` | Plan | testes verdes; o hook bloqueia de verdade numa sessão | `eduardo-claude-config` |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | ✅ PR #21 (Marcos, 29/10) e PR #22 (Eduardo, 30/10, com o ok do Marcos): o "pronto quando" passa. Sobram para a MA3: `cd_cvm` int e só ativas no C1, tabela `indicadores` (seção 0) | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 (atrasada) | 🟡 PR #46 (03/11): C1 e C2, S1, S2 (13 linhas, 0,00%), #17 (o ano do exercício: Camil = DFP de 28/02/2026), corte de R$ 10 mi ok, `checagem` sem "erro". Mesclado em 03/11. Falta o zip da `data/` no Drive (link no grupo) e a #48 (MA3b) | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA3b | qui 05/11 | — | consertar a **issue #48**, achada pelo Miguel em 04/11: o `publicar()` grava a `data/indicadores.csv` com permissão só do dono (`NamedTemporaryFile`), e no Docker do Linux a tela não lê o arquivo (todo raio-x falha). Guia §5: "A aplicação funciona de ponta a ponta na demonstração?" (20%) | `scripts/indicadores.py`, `tests/test_dados.py` | Manual | depois de `docker compose run --rm --user "$(id -u):$(id -g)" tela python scripts/indicadores.py`, `ls -la data/indicadores.csv` → `-rw-r--r--` e a tela gera o raio-x sem o `chmod`; teste novo da permissão; antes do vídeo v0 (MG6) | PR que fecha #48 |
| MA4 | dom 01–ter 03/11 | — | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA5 | qua 04–qui 05/11 | — | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | — | passou ao Eduardo em 04/11 (tabela do Eduardo). O Marcos revisa o rascunho até sáb 07/11 e, quando o PDF novo entrar, troca a citação do `raiox/limpeza.py` | — | — | — | — | — |

### Miguel (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | ✅ conferido em 30/10: PR e check `testes` obrigatórios, só merge commit, apagar branch após o merge; tela rodando no Docker (o print vai para o grupo) | configurar o GitHub (seção 2, "Proteção da `main`"); rodar a tela local | configurações | só leitura | as 3 configurações feitas; print da tela no grupo | — |
| MG2 | qui 29–sex 30/10 | ✅ PR #24 (30/10): os 2 contêineres `healthy`, health `ok`, `carregar_dfp.py` no banco do contêiner, 87 passed no contêiner | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | ✅ PR #29 (31/10): `apply` sobe os 2 `healthy`; `destroy` + `apply` mantém o banco e a `data/`; 87 passed no contêiner; 2º `plan` sem mudanças. IA pelo Terraform vista pelo Miguel. Portas padrão e Mac conferidos pelo Eduardo em 03/11 (seção 0) | **Terraform na `main`, obrigatório** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform"): provider docker com os 2 contêineres (tela + PostgreSQL), a partir do `terraform/` da branch `docs-docker-e-terraform`. Prazo: dom 01/11; reserva: seg 02/11 com o Eduardo. Não pode ser cortado | `infra/` | Plan | `terraform apply` sobe a tela e o banco; `destroy` + `apply` mantém a `data/` e o banco | PR |
| MG4 | dom 01–ter 03/11 | ✅ PR #36 (02/11): WEG, Embraer e Ambev geram o raio-x no contêiner, e as 3 consultas estão na `consultas`; 8 testes em `tests/test_tela.py`. Gemini de verdade conferido em 03/11 (WEG). Volta para o modo sem IA com o Gemini fora do ar conferida em 03/11 (chave inválida, WEG): funciona; os 2 problemas de aparência viraram a MG4b | tela com dados reais e **com o banco** (R Aplicação: banco de dados): `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`, e com `real` a busca e o `registrar_consulta` usam o PostgreSQL (`raiox/dados.py`); volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner, e cada consulta aparece na tabela `consultas` | PR (Eduardo) |
| MG4b | qua 04/11 | ✅ PR #47 (03/11, adiantada): com a chave falsa, a WEG mostra o aviso curto e "Texto montado sem IA: o Gemini não respondeu."; 3 testes novos e o do rodapé em `tests/test_tela.py`; `docker compose ps` → `127.0.0.1:8501`. Junto: os avisos de banco vazio e desligado citam o Terraform | consertar as issues **#38** (o aviso de falha da IA mostra o JSON inteiro do Google), **#39** (o topo diz "Texto escrito pelo Gemini" quando o texto foi montado sem IA) e **#44** (o compose abre a tela para a rede toda: `127.0.0.1:8501:8501`, como o Terraform), achadas pelo Eduardo em 03/11. Guia §5: "a interface é amigável ao usuário?" (protótipo, 20%) | `app/streamlit_app.py`, `tests/test_tela.py`, `docker-compose.yml` | Manual | com `GOOGLE_API_KEY=chave-falsa-teste RAIOX_IA_REAL=1 docker compose up -d --build`, a WEG mostra um aviso curto e o topo não diz "escrito pelo Gemini"; teste novo para cada issue; `docker ps` mostra `127.0.0.1:8501`; antes do vídeo v0 (MG6) e do congelamento (sex 06/11) | PR que fecha #38, #39 e #44 |
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
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py`, `test_banco.py`, `test_verificar_automatico.py` (PRs #4 e #21) | regras de limpeza, carga da DFP (rede simulada), catálogo e C1 em PostgreSQL (banco de teste separado: `tests/banco_teste.py`); o C2 (CSV padrão, `cd_cvm` int, mesma tabela no banco) em `test_publicar_grava_o_mesmo_c2_no_csv_e_no_banco` (#46; era `test_calcular_grava_csv_padrao_com_cd_cvm_inteiro`, do #22) | Marcos | sim: o CI sobe um PostgreSQL desde o #22 (sem ele, os testes do banco pulam; `-rs` mostra quais) |
| C1 e C2 no banco, ano do exercício (MA3, PR #46) | `test_busca_exige_cadastro_ativo_e_indicadores`, `test_sem_a_tabela_indicadores_a_busca_volta_vazia`, `test_publicar_grava_o_mesmo_c2_no_csv_e_no_banco` (`tests/test_dados.py`); `test_ano_do_exercicio_e_o_ano_com_mais_meses` e `test_limpar_demo_usa_o_ano_do_exercicio_e_nao_o_do_arquivo` (`tests/test_limpeza.py`); `test_main_usa_o_exercicio_de_quem_fecha_fora_de_dezembro`, `test_main_segue_sem_o_arquivo_do_ano_seguinte` e `test_main_para_se_falta_o_arquivo_de_um_dos_anos` (`tests/test_carregar_dfp.py`); `test_desiste_rapido_se_o_banco_nao_responde` (`tests/test_banco.py`) | Marcos | sim |
| `tests/test_tela.py` (MG4, MG4b) | a tela com os falsos: busca, gerar, 6 métricas, sem erro; com a IA fora do ar, aviso de uma frase (o erro em "Detalhes técnicos" e no log) e o topo e o rodapé sem "escrito pelo Gemini"; os avisos do banco com os comandos do Terraform | Miguel | sim |
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
| R7 Interface | MG4, MG4b, MG6 |
| R8 Boas práticas e agentic coding | ED0, ED2, ED6, ED8, todos os PRs |
| R9 Arquitetura e infra com Terraform (obrigatório) | MG2, MG3, MG5 |
| R10 Governança e ética | NA5, ED8, MG4, MG4b |
| R11 ROI | NA1, NA3 |
| R12 Métricas | NA2, ED5, ED7, NA4, ED11 |
| R13 Backend, frontend e banco na aplicação | MG4, MG4b (pergunta ao professor respondida em 02/11: Streamlit vale, em 2 contêineres) |
| R14 Prompts do vibecoding | ED8 |
| D1 Repositório | ED0, MA1, NA1, ED9 |
| D1b README | MG5, ED8, ED10 |
| D1c Infra (Terraform) e notebooks | MG2, MG3, MA4 |
| D2 Documento (etapas, BPMN, justificativa, ética) | MA6, do Eduardo desde 04/11 (com MA5, ED8, NA5, MG5) |
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
| ~~sex 06/11~~ | ~~o PR da MA3 (#42) não entra antes do congelamento~~ | entrou em 03/11 (PR #46) |
| qualquer dia | uma pessoa com sessões demais (era o Marcos, com MA3, MA4, MA5 e MA6) | decidido em 04/11: o Eduardo monta o PDF (MA6) |
| qualquer dia | alguém fica indisponível | duplas de reserva: Marcos ↔ Eduardo (dados e PDF), Miguel ↔ Eduardo (infra), Náthally ↔ Marcos (deck) |

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
