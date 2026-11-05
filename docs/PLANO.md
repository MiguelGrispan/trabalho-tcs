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

**Em qui 05/11, ~10h (Brasília)** (fim da ED16, Eduardo com o Claude Code: os 10 raio-x da Náthally com a Camil corrigida,
depois do merge da MA4b, #59; as notas da MA4b, da MG5, da MA4, da MA5 e da MG4b, e da MA3, de 03/11, continuam abaixo).
Na `main`: PRs #1 a #16, #19 a #41, o #46 (MA3, fechou #17 e #42), o #47 (MG4b, fechou #38, #39 e #44), o #51 (MA3b; a #48 foi
fechada à mão, depois da conferência do Miguel no Linux), o #52 (MA5, BPMN), o #54 (MA4, EDA), o #55 (MG5, arquitetura) e o #59
(MA4b, fechou a **#53**). **Abertos:** o #49 (Eduardo, rascunho do MA6) e o #58 (Eduardo, ED16, o PR desta nota).
Issues abertas: #43, #45, #50 e #60 (Eduardo; a #60: os 10 casos de avaliação caem no mesmo grupo do K-means; a #50: o validador deixa passar "dobrou", "triplicou", "um quarto"); do revisor no #55:
**#56 (Miguel)**, a tela diz que os números vêm do PostgreSQL, mas vêm da `data/indicadores.csv`; e **#57 (Eduardo)**, os guias
criam o ambiente com `python` ou `python3`, que pode não ser o 3.14.
**Depois do merge da MA4b, todos recarregam a `data/`** (`python scripts/carregar_dfp.py`, `python scripts/indicadores.py` e
`python -m raiox.segmentos`; o Miguel também no banco do compose). A NTS muda, e com ela os grupos do K-means (abaixo, ED16).
Testes na branch da ED16, com a `main` (e o #59) mesclada: 252 passed, nenhum pulado (Mac do Eduardo, PostgreSQL do compose ligado, 05/11).
A versão longa desta seção, com o detalhe de cada PR até 03/11, ficou no Git: `git show 9f85bc9:docs/PLANO.md`.
O resumo de cada dia está no [HISTORICO.md](HISTORICO.md).

**Falta 1 dia para o código congelar (sex 06/11) e 11 para a entrega (seg 16/11).**

### O que já funciona (conferido)
- **ED16 (Eduardo, 05/11): os 10 raio-x da Náthally de novo, com a Camil corrigida (#46) e o Gemini respondendo nos 10.**
  No Mac do Eduardo, a `data/` ainda era de 30/10 (Camil com R$ 12,3 bi e +20%): `carregar_dfp.py` (384.591 linhas, 660 ativas),
  `indicadores.py` e `python -m raiox.segmentos` de novo, com o PostgreSQL do compose, e outra vez depois do merge do #59 (MA4b),
  que mudou os grupos (o raio-x da manhã citava as medianas velhas e foi refeito). Camil (24228): R$ 11,1 bi e −1,2%.
  Mesmos 10 casos da branch dela (`feat/metricas`, `Semana_02/casos_avaliacao.csv` = `avaliacao/casos_avaliacao.csv`).
  **8 de 10 batem com a conferência dela nos 6 indicadores** (era 7 de 10; critério: receita e ativo com até 1% de diferença; os 4 percentuais com até 0,15 ponto percentual); Magalu (5 de 6) e RD Saúde (3 de 6; com 0,1 ponto, seria 2 de 6) seguem
  diferentes dela e iguais à DFP (S2 do Marcos); as 2 diferenças são de definição, não de dado (conferido nos PDFs que ela usou, 05/11): na RD Saúde, a conferência usou a tabela "Pré-IFRS 16" do Relatório da Administração, dentro do PDF da DFP 2025 (p. 48 da DFP; sem os aluguéis das lojas: ativo R$ 20.630,8 mi, PL R$ 7.749,6 mi, EBIT ajustado R$ 2.331,9 mi, lucro R$ 1.362,5 mi, os 4 números dela), e o sistema usa a DFP oficial, com IFRS 16; no Magalu, os 5,81% saem exatamente do EBIT oficial (R$ 1.918,7 mi) sem as perdas de créditos esperadas e sem a equivalência patrimonial (R$ 2.247,2 mi; reconstrução nossa, falta ela confirmar). 0 trechos removidos, nenhum número fora da tabela no texto (conferido por fora,
  com regex), US$ 0,0118 no total, 2,2 s por caso em média (rodada depois do #59). O `avaliacao/resultados.csv` foi trocado por essa rodada.
  O arquivo para ela (`raiox_para_nathally.md`, os 10 JSON e o script) fica só na `data/nathally_05_11/` do Mac do Eduardo.
  **K-means com os dados do #46 e do #59:** k = 4, silhueta 0,29 (0,286), grupos de 60, 310, 88 e 106 no treino (66, 312, 103 e 114 com as 595);
  `docs/graficos/silhueta.png` e `grupos.png` refeitos; números trocados no REQUISITOS (R5 e R12) e na `docs/justificativa.md` §2.
  O `docs/documentacao.md` do #49 ainda cita os números de 30/10 (327, 76, 59 e 102): trocar no MA6.
- **Demo ponta a ponta** no `docker compose` e no Terraform (Mac do Eduardo, 03/11), tag `v0.1-demo` (`9689db9`): busca no
  PostgreSQL, raio-x sem IA (Vale, Embraer, Ambev) e com o Gemini (WEG, US$ 0,0011), cada consulta gravada na `consultas`.
  Com o Gemini fora do ar (chave falsa), a tela cai no modo sem IA, avisa e grava a consulta com custo 0.
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
  **Achado: issue #48 (Marcos)**: o `indicadores.py` novo gravava a `data/indicadores.csv` como `-rw-------`, e a tela (`appuser` no
  contêiner) não lia: todo raio-x falhava com `Permission denied`.
- **MA3b (Marcos, PR #51, na `main` em 04/11): conserto da #48.** `temporario.chmod(0o644)` antes do `replace` em `publicar()`
  (`scripts/indicadores.py`) e o teste `test_publicar_deixa_o_csv_legivel_para_outros_usuarios` (`tests/test_dados.py`).
  **Conferido pelo Miguel no Linux** (na branch do PR, antes do merge; relato dele, não refeito aqui): com o CSV trancado
  (`-rw-------`), o `indicadores.py` pelo Docker deixou `-rw-r--r--`; a tela reiniciada gerou a Camil sem o `chmod` (R$ 11,1 bi,
  −1%); o teste falha sem a linha do conserto; 245 passed. A #48 foi fechada com esse relato.
- **MA5 (Marcos, 04/11): BPMN 2.0 do processo com o Raio-X** em `docs/bpmn/raio-x-comercial.bpmn` e `.png`, desenhado pelo
  Claude Code a partir do código (o PLANO previa o Marcos desenhando e o Claude revisando). Raias "Vendedor" e "Aplicação",
  o Gemini como pool à parte, PostgreSQL e `data/` como armazenamentos; as decisões "Tem dados da empresa?" e "Passou no
  validador?" (item por item: o resumo, cada pergunta e cada lacuna, `raiox/ia.py:263-281`), "IA ligada?" e o erro "Gemini
  falhou" (→ texto sem IA). O bpmn-js 17.11.1 (o motor do bpmn.io), numa página local, abre o arquivo com 0 avisos de importação, e o
  PNG saiu dele; no site demo.bpmn.io ainda ninguém abriu. Os erros raros (falha ao gerar mesmo sem IA, `app/streamlit_app.py:117-120`)
  ficaram fora do desenho. Revisor: ATENÇÃO; 8 dos 9 itens corrigidos no PR (o de erros raros em parte; o
  `__targetRef_placeholder` fica, porque é o nome que o próprio bpmn-js usa). O BPMN "hoje" (sem o Raio-X) não foi feito: é o corte 1 da seção 7 (o `requisitos_projeto.MD`
  pede o BPMN "do processo da regra de negócio da aplicação", e esse está feito).
- **MA4 (Marcos, 04/11): a EDA** em `notebooks/eda.ipynb`, montada pelo Claude Code a partir do `scripts/graficos.py`, com os
  4 gráficos em `docs/graficos/eda_*.png` (nulos, distribuições, extremos, cobertura) e o texto do que cada um mostra e da
  decisão do projeto que saiu dele (`guia_projeto_final.pdf` §1 e §2: EDA e "Visualização explicativa dos dados").
  O "Restart & Run All" com a `data/` real roda sem erro (nbconvert, Windows do Marcos). Os limites vêm do código
  (`raiox/checagem.py` e `RECEITA_MINIMA`, `raiox/segmentos.py`). Sem a `data/`, ou com `RAIOX_DADOS=falsos`, usa `falsos/` e não
  grava PNG; `tests/test_eda.py` roda o notebook inteiro assim, então o CI confere o "Run All" em todo PR. Números (dados de
  04/11): só o crescimento tem vazios (30 de 595: 23 sem receita de 2023, 7 com ela zero); 24 dos 51 setores têm menos de 5
  empresas. **Achado:** a NTS tem 2023 de 1.000 a 2.000 vezes menor (receita 987 vezes, ativo 1.923 vezes), e o
  `encontrar_escala_errada` só comparava cada ano com o anterior: o primeiro ano passava. Virou a **issue #53**, consertada na
  MA4b (abaixo).
- **MA4b (Marcos, 05/11, PR da branch `marcos-escala-primeiro-ano`): conserto da #53** (`guia_projeto_final.pdf` §2: "Python
  e Pandas para limpeza"; §5, qualidade técnica, 30%). Em `encontrar_escala_errada()` (`raiox/limpeza.py`), o primeiro ano de
  cada empresa agora é comparado com o **seguinte** e só é corrigido quando a receita (DRE 3.01) **e** o ativo (BPA 1) estão
  ~1.000 vezes menores juntos (decisão do Marcos: um salto só na receita pode ser empresa que começou a operar). 2 testes
  novos em `tests/test_limpeza.py`: o 1º falhou antes do conserto; o 2º falha se a condição do ativo sai (conferido tirando-a
  de propósito). **Recarga com a `data/` real (Windows do Marcos, 05/11):** a única marcação nova é a NTS (24708, 2023); o
  crescimento dela foi de +107.154% para +7,3%; as outras 594 empresas ficaram iguais (comparado com uma cópia do
  `indicadores.csv` de antes); `checagem`: 179 "atenção" (eram 180), nenhum "erro". O notebook rodou de novo sem erro: extremos
  do crescimento 15 → 14, saltos de 500 vezes 7 → 5; só o `eda_2_distribuicoes.png` mudou. **Fica de fora, de propósito:** o
  JBS N.V. (salto no ativo, receita zero em 2023: falta o 2º sinal), FASA, TRV XLIII e Azevedo & Travassos; nenhum foi olhado na
  CVM. Vão como limite conhecido no MA6 (seção "Dados e limpeza"), com mais um (achado do `revisor`, já era assim antes do PR):
  se o 1º **e** o 2º ano vêm em milhares e só o 3º vem certo, nenhum dos dois é pego. O efeito no K-means foi conferido na ED16 (#58), que refez
  os grupos depois deste merge (60, 310, 88 e 106 no treino); o crescimento da NTS é cortado no percentil 95, e o p95 caiu de 1,33 para 1,30.
  Na máquina do Marcos, o `carregar_dfp.py` levou mais de 10 min (no Linux do Miguel, ~1 min 30 s).
- **MG5 (Miguel, PR #55, 04/11): a arquitetura no README** (`guia_projeto_final.pdf` §6: "README.md detalhando a arquitetura,
  pré-requisitos e instruções de execução"; §3, minutos 3–6). Seção "Arquitetura" com o diagrama em Mermaid (o GitHub desenha
  sozinho): os 2 contêineres (tela com `app/` e `raiox/`; banco com o PostgreSQL 17), a `data/` (pasta do computador montada na
  tela), a API do Gemini, a CVM e o Terraform que cria tudo (o compose faz o mesmo); linhas cheias a cada raio-x, tracejadas
  antes da demo; 6 frases embaixo. O mesmo desenho em `docs/arquitetura.png` (4872×2172, gerado do bloco do README com o
  Mermaid 11.4.1), para o MA6 e o deck. Seção "Pré-requisitos" com os 3 jeitos de rodar, o Terraform como a infraestrutura
  exigida (`requisitos_projeto.MD`, Aplicação). **Conserto:** o README mandava `python -m venv`, mas no Linux do Miguel `python`
  não existe e o `python3` é o 3.12; agora é `python3.14 -m venv .venv` (os outros guias: #57). `tests/test_readme.py` (3 testes):
  o diagrama só cita arquivos que existem e o modelo de `raiox/ia.py:28`; estragado de propósito, falha. **Revisor: ATENÇÃO**,
  corrigido no PR: a seta do Terraform sumia sob o rótulo; a `data/` parecia dentro do Docker; "escolha um" lia o Terraform como
  opcional; a referência de linha no HISTORICO. Fora do PR: #56 e #57. **Não conferido:** o desenho do Mermaid na página do
  GitHub (por isso a R9 fica 🟡) e o "pronto quando" (um colega entender o fluxo lendo o README).
- **Testes:** 252 passed, nenhum pulado (Windows do Marcos, `PYTHONUTF8=1`, PostgreSQL 17 local, branch da MA4b, 05/11); na
  branch da MG5, 250 passed (Linux do Miguel, 04/11). No Windows, sem `PYTHONUTF8=1`, 8 testes das travas falham: issue #45 (abaixo).
- **Textos-base prontos:** `docs/justificativa.md` (ED8; falta o Marcos ler) e `docs/etica.md` (base da NA5).
- No Mac, o Terraform só acha o Docker com `export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock` (`README.md:235`).

### MA3 (Marcos, 03/11): PR #46, que fechou as issues #42 e #17 (mesclado em 03/11)
- **C1 e C2** (os 3 commits de 10h09 da branch `marcos-corrige-s1-s2`): a busca devolve só companhias ativas e com indicadores,
  com o `cd_cvm` como número (`raiox/dados.py`); a tabela `indicadores` existe no PostgreSQL (`publicar()` em `scripts/indicadores.py`).
  As 2 notas "Pendente" do `contratos.md` saíram. **S1:** `scripts/verificar_dfp.py` acha as mesmas 595 empresas.
- **Camil (#17): a opção 3 da issue.** O "ano" passou a ser o do exercício, e não o do arquivo da CVM
  (`ano_do_exercicio()`, `raiox/limpeza.py`), e o `scripts/carregar_dfp.py` baixa também o arquivo de 2026. O "2025" da Camil é
  mar/2025 a fev/2026: receita de R$ 11,12 bi (era 12,26) e crescimento de −1,2% (era +20,2%), os números da conferência manual da Náthally.
  Os outros 4 indicadores dela para a Camil não conferi. Mudam só as 9 empresas que fecham fora de dezembro (açúcar e etanol, agro, têxtil);
  as 595 continuam (comparado com uma cópia do `indicadores.csv` de antes). O Eduardo chamava a opção 3 de "fora do escopo"; ela
  coube em 2 arquivos e 3 testes, e o formato do C2 não muda. **A Camil pode voltar à demo e ao slide.**
- **S2** (`avaliacao/conferencia.csv`): 13 linhas de 5 empresas (WEG, Camil, Magalu, RD Saúde, CSN), todas com diferença de 0,00% contra
  o PDF do RI. A da Camil é a DFP de 28/02/2026 ("DFs 4T25 e 2025", PDF p. 27, conferida pelo Marcos). Magalu e RD Saúde: o sistema
  bate com o RI (margem EBIT de 4,96% e 6,20%); a diferença da conferência manual vem da fonte usada nela (suposição: não sei qual ela usou).
  `python -m raiox.checagem data/indicadores.csv data/contas.csv` → nenhum "erro", 180 "atenção" em 98 empresas.
- **Corte de R$ 10 mi: ok do Marcos.** `scripts/avaliar_corte_receita.py` com os dados de hoje: abaixo, 31 empresas, 52% com
  |margem EBIT| > 100%; acima, 564 e 4%.
- **Banco desligado:** a conexão desiste em 5 s (`TEMPO_LIMITE_S`, `raiox/banco.py`). Sem limite, o psycopg espera 130 s (medido no
  Windows), e a tela ficava parada antes do aviso. Sem a tabela `indicadores`, a tela agora diz "O banco está vazio" (com os comandos
  de carga), e não "o banco está ligado?" (pedido da #42).
- **Travas no Windows (issue #45, Eduardo):** o `guarda.py` lê o Git em cp1252 e bloqueia commit e merge com `”` ou emoji no diff. O
  Marcos usa `PYTHONUTF8=1` no `.claude/settings.local.json` dele, que não vai para o Git: a conferência continua, só que lendo em UTF-8.

### Revisão de 03/11 (Eduardo): o que estava errado nas notas e no GitHub
- A MA3 estava pronta numa branch sem PR, e a nota dizia que ela não existia (issue #42; resolvida pelo #46, acima).
- **Bug (Eduardo):** a tela aberta antes de carregar a CVM não acha a empresa até ser reiniciada (cache em `raiox/ia.py:51`).
  É exatamente o caminho do teste do zero (ED10) → **issue #43**, sessão ED13.
- **Segurança (Miguel):** o compose abria a tela para a rede toda (`0.0.0.0:8501`); o Terraform já fechava em `127.0.0.1` →
  **issue #44**, consertada no PR da MG4b (#47).
- Frases velhas corrigidas: o CLAUDE.md e o README diziam que a tela ainda usava `falsos/` (usa o banco desde a MG4).
- O `/fim-de-sessao` passa a listar as branches sem PR antes de reescrever esta seção (passo 4), para não repetir o caso da MA3.

### Caminho crítico (o que trava os outros)
1. **A recarga dos dados depois do #46 (MA3, na `main` desde 03/11).** Todos rodam de novo `python scripts/carregar_dfp.py` e
   `python scripts/indicadores.py` (os dois precisam do PostgreSQL ligado) e reiniciam a tela (o cache da #43 guarda a tabela velha).
   Sem a tabela `indicadores`, a busca não acha nada e a tela diz "O banco está vazio" (o banco do compose do Miguel não tinha a
   tabela até a recarga de 04/11). No Linux, o `chmod 644 data/indicadores.csv` à mão não é mais preciso desde o #51 (MA3b, 04/11).
2. **Os entregáveis.** O código está perto do fim; o que falta é documento: PDF (MA6; o BPMN da MA5, a EDA da MA4 e o diagrama
   de arquitetura da MG5 já existem),
   deck (NA5 e NA6) e vídeo (MG6 e MG7). Hoje, quase tudo isso está com o Marcos e a Náthally.
3. **Proposta da revisão: congelar também o processo.** Até 16/11, nenhuma regra, trava ou guia novo para o time: só o que fecha
   uma linha do [REQUISITOS.md](REQUISITOS.md). Dos PRs de 02 e 03/11, a maioria foi de notas e regras; a banca avalia os entregáveis.

### Próximo passo de cada um
- **Marcos:** ✅ MA5 BPMN (#52; falta abrir o `.bpmn` no demo.bpmn.io e treinar a explicação para os minutos 3–6 da banca) →
  ✅ MA4 EDA (#54, 04/11) → ✅ MA4b, a #53 (05/11; depois do merge, avisar o grupo para recarregar a `data/`) →
  revisar o rascunho do MA6 do Eduardo (sáb 07/11) → trocar a citação do `raiox/limpeza.py` para a seção "Dados e limpeza" do
  `docs/documentacao.md` e tirar o `docs/Raio-X Comercial.pdf` (depois do MA6). Um PR pequeno, com o ok do Eduardo, tirando
  `verificar_automatico.py` e `yfinance` (cortados na seção 7) e o `scripts/graficos.py` (a EDA já cobre o que ele fazia); no mesmo
  PR, sai a linha do `verificar_automatico.py` do README ("Como rodar", `README.md:269`). Ler a `docs/justificativa.md` (ED8).
- **Miguel:** ✅ MG4b (#47: #38, #39 e #44) → ✅ recarga da CVM no banco do compose (04/11, com o contorno da #48) → ✅ MG5 diagrama
  e README (#55, 04/11; pedir a um colega que leia a seção "Arquitetura" e conferir o desenho na página do PR) → **MG5b: issue
  #56** (a frase da tela sobre a origem dos números; qui 05/11, antes do vídeo) → MG6 roteiro e vídeo v0 (qui 05/11),
  gravado no Mac do Eduardo (o computador da banca). Avisar o grupo das mudanças em pastas comuns: `README.md`,
  `docs/arquitetura.png` e `tests/test_readme.py` (MG5), `tests/test_tela.py` (MG4b) e, da MG4, `.env.example` e `aprender/`.
- **Náthally (obrigatório):** NA3 ROI mínimo (até qui 05/11) → NA4 slide de métricas (o "8 de 10" da rodada de 05/11, ED16, com a explicação da S2 para
  Magalu e RD Saúde; a Camil bate nos 6 indicadores) → NA5 ética (base: `docs/etica.md`) → NA6 deck. Sugestões, se der tempo: seção 3.
- **Eduardo:** ED13, a #43 (qua 04/11) → ED14, a #45 (travas no Windows, qui 05/11) → a #50 (validador e quantidade sem
  algarismo; regra de ouro, antes do congelamento) → ✅ K-means e PNG com os dados do #46 e do #59 (ED16) → ED9 tag `v1.0` e ED11
  (sex 06/11) → **ED15: issue #57** (`python3.14 -m venv` no `CLAUDE.md` e no `aprender/`, antes do teste do zero) → ED10 teste do zero (sáb 07/11) → **MA6** (agora dele): rascunho do
  `docs/documentacao.md` no sáb 07/11 para o Marcos revisar; final e PDF na seg 09/11. O "[PENDENTE: diagrama · MG5, Miguel]"
  da seção 5 do rascunho (#49) já pode usar o `docs/arquitetura.png` (depois do merge do #55).
  Mandar ao grupo a mensagem da revisão; perguntar ao professor a data da banca e as perguntas 2 e 3 do REQUISITOS;
  treinar a defesa com `/explicar` (seção 8).

### Decisões em aberto
- Decidido no grupo em qua 04/11 (Marcos e Eduardo):
  - **o MA6 passa para o Eduardo.** Ele escreve em `docs/documentacao.md` e gera o PDF a partir dele (o PR tem diff e os números
    podem ser conferidos). O documento terá uma seção "Dados e limpeza" com as regras atualizadas. O Marcos continua lendo a
    `docs/justificativa.md` e revisa o rascunho no sáb 07/11. O Marcos fica com MA3, MA5 e MA4;
  - **a demo na banca roda no Mac do Eduardo**, o único conferido com compose, Terraform e Gemini (03/11). Os vídeos v0 (MG6) e
    final (MG7) são gravados nele também. Reserva: o Linux do Miguel (compose e Terraform com a tela nova, 03/11; o Gemini de
    verdade, só pelo Terraform em 31/10, visto pelo Miguel).
- Data e horário da banca; perguntas 2 e 3 ao professor (Eduardo).
- `scripts/dados.py` ou `raiox/dados.py` (ficar com um só; Marcos).
- Decidido pelo Marcos em 03/11:
  - o `verificar_automatico.py` e o `yfinance` saem num PR separado (falta o ok do Eduardo, porque mexe em `tests/` e no
    `requirements.txt`);
  - o `scripts/graficos.py` **fica até a MA4**: são gráficos exploratórios em Matplotlib que podem virar a base do
    `notebooks/eda.ipynb` (`guia_projeto_final.pdf` §2: "Visualização explicativa dos dados"; §1: EDA). Só o script pode sair;
    a visualização é obrigatória. (04/11: a EDA da MA4 cobre o que ele fazia; ele sai no PR pequeno do Marcos, acima);
  - o `docs/Raio-X Comercial.pdf` fica até a MA6, porque o `raiox/limpeza.py` o cita como a fonte das regras de limpeza (ele ainda
    fala de SQLite). Quando o `docs/documentacao.md` entrar, com a seção "Dados e limpeza" (04/11), o Marcos troca a citação do
    `limpeza.py` para ela e o PDF velho sai;
  - a `tratamento_dados` será apagada (feito: em 04/11 ela não aparece em `git branch -r`).
- Apagar a `feat/metricas` (Náthally; antes, subir o `revisao_manual.md`, se ela quiser).
- As 3 notas do código (`NOTAS_DO_CODIGO`, em `raiox/ia.py`) vão para a v3 das regras? (Náthally).

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

### Progresso estimado (Claude, 03/11: estimativa pelo esforço que falta, não medida)

| parte | feito | falta | horas que faltam |
|---|---|---|---|
| núcleo: dados, ML, IA, validador, avaliação | ~94% (Claude, 03/11 ~12h, com o #46) | #43, #45 | 2 a 3 h |
| tela e infraestrutura | ~97% (Claude, 04/11, depois da MG5) | um colega ler o README; o desenho na página do GitHub | até 1 h |
| entregáveis: BPMN, EDA, PDF, deck, vídeo, ensaios | ~15% (justificativa e ética prontas como base) | quase tudo | 25 a 35 h |
| **total** | **~61%** | 14 de 27 dias usados (21/10 a 16/11): no ritmo, **se** os entregáveis começarem esta semana | **27 a 42 h**, para uns 40 a 80 h de capacidade do grupo até 16/11 |

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
| qua 04/11 | **ED13: issue #43** (~30 min); ✅ ED8 (feita em 02/11) | ~~PR da MA3 e #17~~ (PR #46, 03/11); ✅ zip da `data/`; ✅ MA5 BPMN; ✅ MA4 EDA (atrasada; achou a #53) | ~~MG4b~~ (#47, merge em 04/11); recarga da CVM; ✅ MG5 arquitetura + README (#55) | NA4 slide de métricas |
| qui 05/11 | só bugs; **ED14: issue #45** (travas no Windows) | ✅ MA3b (#51); ✅ MA5 (adiantada, 04/11); ✅ MA4b (#53) | **MG5b: issue #56**; MG6 vídeo v0 | NA3 (prazo do ROI mínimo) |
| sex 06/11 | **ED9: código congelado · tag `v1.0`**; ED11 avaliação final | | | |
| sáb 07/11 | ED10 teste do zero; MA6 rascunho (`docs/documentacao.md`) | revisar o rascunho do MA6 | MG7 vídeo final na `v1.0` (no Mac do Eduardo) | NA5 ética |
| dom 08/11 | **todos mandam o conteúdo dos slides à Náthally** | | | NA5 deck |
| seg 09/11 | MA6 final (o `.md` e o PDF gerado dele) | trocar a citação do `raiox/limpeza.py`; o PDF velho sai | | NA6 deck final |
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
| ED15 | sex 06/11 | — | consertar a **issue #57**: o `CLAUDE.md:142` e o `aprender/entenda-o-projeto.md:167` mandam `python -m venv .venv` (no Linux do Miguel não existe `python`); o `aprender/COMANDOS.md:16` e os 3 atalhos `.command` usam `python3 -m venv`, que lá é o 3.12. O README já usa `python3.14` (#55). `requisitos_projeto.MD`, Documentação: "instruções para executar" | `CLAUDE.md` (ok no grupo), `aprender/` | Manual | os 6 lugares com `python3.14 -m venv .venv` (Windows: `py -3.14`); antes do ED10 (sáb 07/11) | PR que fecha #57 |
| ED16 | qui 05/11 | ✅ PR desta sessão | 10 raio-x para a Náthally com a Camil corrigida (#46), com o Gemini; K-means e PNG refeitos com os dados do #46 e do #59; diferenças da RD e do Magalu explicadas | `avaliacao/resultados.csv`, `docs/graficos/`, `data/nathally_05_11/` (só no Mac) | Manual | 8 de 10 batem com a conferência dela; 0 removidos; números do K-means trocados nos docs | `eduardo-raiox-nathally` |
| ED12 | sáb 31/10 | ✅ PR #30 (na `main` em 02/11) | travas do Claude Code (R14 e guia §2, agentic coding): `.claude/settings.json`, `.claude/hooks/guarda.py`, subagent `revisor`, import do `requisitos_projeto.MD` | `.claude/`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `aprender/claude-code.md`, `tests/test_guarda.py` | Plan | testes verdes; o hook bloqueia de verdade numa sessão | `eduardo-claude-config` |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | ✅ PR #21 (Marcos, 29/10) e PR #22 (Eduardo, 30/10, com o ok do Marcos): o "pronto quando" passa. Sobram para a MA3: `cd_cvm` int e só ativas no C1, tabela `indicadores` (seção 0) | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 (atrasada) | ✅ PR #46 (mesclado em 03/11): C1 e C2, S1, S2 (13 linhas, 0,00%), #17 (o ano do exercício: Camil = DFP de 28/02/2026), corte de R$ 10 mi ok, `checagem` sem "erro". Zip da `data/` no Drive, com o link no grupo (04/11) | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA3b | qui 05/11 | ✅ PR #51 (na `main` em 04/11): `chmod(0o644)` e teste novo; conferido pelo Miguel no Linux (`-rw-r--r--`, Camil sem `chmod`); #48 fechada | consertar a **issue #48**, achada pelo Miguel em 04/11: o `publicar()` grava a `data/indicadores.csv` com permissão só do dono (`NamedTemporaryFile`), e no Docker do Linux a tela não lê o arquivo (todo raio-x falha). Guia §5: "A aplicação funciona de ponta a ponta na demonstração?" (20%) | `scripts/indicadores.py`, `tests/test_dados.py` | Manual | depois de `docker compose run --rm --user "$(id -u):$(id -g)" tela python scripts/indicadores.py`, `ls -la data/indicadores.csv` → `-rw-r--r--` e a tela gera o raio-x sem o `chmod`; teste novo da permissão; antes do vídeo v0 (MG6) | PR que fecha #48 |
| MA4 | dom 01–ter 03/11 (feita em 04/11) | ✅ PR da branch `marcos-eda` (04/11): notebook montado pelo Claude Code a partir do `scripts/graficos.py`; "Restart & Run All" com a `data/` real sem erro; `tests/test_eda.py` roda o notebook com os falsos no CI; achado da NTS → issue #53 | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA4b | qui 05/11 | ✅ PR da branch `marcos-escala-primeiro-ano` (05/11): o primeiro ano comparado com o seguinte, pela receita e pelo ativo juntos; 2 testes novos (o 1º falhava antes); recarga: NTS +107.154% → +7,3%, só ela mudou; notebook rodado de novo. JBS N.V. fica de fora (receita zero em 2023): limite no MA6 | consertar a **issue #53**, achada pela EDA em 04/11: o `encontrar_escala_errada` (`raiox/limpeza.py:165-192`) só compara cada ano com o anterior, e o erro de escala no primeiro ano da base passa (NTS: 2023 de 1.000 a 2.000 vezes menor, crescimento de +107.154%; o JBS N.V. tem o mesmo salto no ativo, com receita zero em 2023). Guia §2 (limpeza com Pandas) e §5 (qualidade técnica, 30%) | `raiox/limpeza.py`, `tests/test_limpeza.py`; recarga da `data/` | Manual | teste novo com o primeiro ano marcado (e que falha sem o conserto); depois da recarga, o crescimento da NTS perto de +7% e o notebook rodado de novo; o grupo avisado para recarregar. Se não der até o congelamento (sex 06/11): limite no documento (MA6) e a NTS fora da demo | PR que fecha #53 |
| MA5 | qua 04–qui 05/11 | ✅ PR #52 (na `main` em 04/11): `docs/bpmn/raio-x-comercial.bpmn` e `.png`, desenhados pelo Claude Code a partir do código; o bpmn-js abre com 0 avisos (falta abrir no demo.bpmn.io) e tem as 2 decisões. O de hoje não foi feito (corte 1, seção 7) | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | ➡️ com o **Eduardo** (decidido em 04/11); o Marcos revisa o rascunho no sáb 07/11 | montar o documento do projeto, escrito em markdown e gerado em PDF (o R aceita markdown; o G §6 pede PDF: vão os dois) | `docs/documentacao.md`, `docs/documentacao.pdf` | Manual | etapas desenvolvidas no processo (R Documentação; a base é o `docs/HISTORICO.md`) + BPMN + justificativa + ética + arquitetura + seção "Dados e limpeza" (as regras do `raiox/limpeza.py`, no lugar do `docs/Raio-X Comercial.pdf`); o Marcos revisou | PR (Eduardo) |

### Miguel (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | ✅ conferido em 30/10: PR e check `testes` obrigatórios, só merge commit, apagar branch após o merge; tela rodando no Docker (o print vai para o grupo) | configurar o GitHub (seção 2, "Proteção da `main`"); rodar a tela local | configurações | só leitura | as 3 configurações feitas; print da tela no grupo | — |
| MG2 | qui 29–sex 30/10 | ✅ PR #24 (30/10): os 2 contêineres `healthy`, health `ok`, `carregar_dfp.py` no banco do contêiner, 87 passed no contêiner | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | ✅ PR #29 (31/10): `apply` sobe os 2 `healthy`; `destroy` + `apply` mantém o banco e a `data/`; 87 passed no contêiner; 2º `plan` sem mudanças. IA pelo Terraform vista pelo Miguel. Portas padrão e Mac conferidos pelo Eduardo em 03/11 (seção 0) | **Terraform na `main`, obrigatório** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform"): provider docker com os 2 contêineres (tela + PostgreSQL), a partir do `terraform/` da branch `docs-docker-e-terraform`. Prazo: dom 01/11; reserva: seg 02/11 com o Eduardo. Não pode ser cortado | `infra/` | Plan | `terraform apply` sobe a tela e o banco; `destroy` + `apply` mantém a `data/` e o banco | PR |
| MG4 | dom 01–ter 03/11 | ✅ PR #36 (02/11): WEG, Embraer e Ambev geram o raio-x no contêiner, e as 3 consultas estão na `consultas`; 8 testes em `tests/test_tela.py`. Gemini de verdade conferido em 03/11 (WEG). Volta para o modo sem IA com o Gemini fora do ar conferida em 03/11 (chave inválida, WEG): funciona; os 2 problemas de aparência viraram a MG4b | tela com dados reais e **com o banco** (R Aplicação: banco de dados): `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`, e com `real` a busca e o `registrar_consulta` usam o PostgreSQL (`raiox/dados.py`); volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner, e cada consulta aparece na tabela `consultas` | PR (Eduardo) |
| MG4b | qua 04/11 | ✅ PR #47 (03/11, adiantada): com a chave falsa, a WEG mostra o aviso curto e "Texto montado sem IA: o Gemini não respondeu."; 3 testes novos e o do rodapé em `tests/test_tela.py`; `docker compose ps` → `127.0.0.1:8501`. Junto: os avisos de banco vazio e desligado citam o Terraform | consertar as issues **#38** (o aviso de falha da IA mostra o JSON inteiro do Google), **#39** (o topo diz "Texto escrito pelo Gemini" quando o texto foi montado sem IA) e **#44** (o compose abre a tela para a rede toda: `127.0.0.1:8501:8501`, como o Terraform), achadas pelo Eduardo em 03/11. Guia §5: "a interface é amigável ao usuário?" (protótipo, 20%) | `app/streamlit_app.py`, `tests/test_tela.py`, `docker-compose.yml` | Manual | com `GOOGLE_API_KEY=chave-falsa-teste RAIOX_IA_REAL=1 docker compose up -d --build`, a WEG mostra um aviso curto e o topo não diz "escrito pelo Gemini"; teste novo para cada issue; `docker ps` mostra `127.0.0.1:8501`; antes do vídeo v0 (MG6) e do congelamento (sex 06/11) | PR que fecha #38, #39 e #44 |
| MG5 | qua 04/11 | ✅ PR #55 (04/11): seção "Arquitetura" no README (diagrama em Mermaid + 6 frases), `docs/arquitetura.png`, seção "Pré-requisitos", `python3.14 -m venv`; 3 testes em `tests/test_readme.py`. Falta um colega ler o README (o "pronto quando") | diagrama de arquitetura + README (tema, objetivo e tecnologias já estão; pré-requisitos com Python 3.14; rodar local, Docker e Terraform) | `docs/arquitetura.png`, `README.md` | Manual | um colega entende o fluxo lendo o README; o README cobre o que o R pede em "Documentação" | PR |
| MG5b | qui 05/11 | — | consertar a **issue #56**: com os dados reais, a tela diz "Empresas e números da CVM (DFP), buscados no banco PostgreSQL." (`app/streamlit_app.py:71`), mas os números vêm da `data/indicadores.csv`; só a busca e o registro usam o banco. Achada pelo `revisor` no #55. Guia §3 (a frase aparece na demo) e §2, "Governança e Ética" (confiabilidade) | `app/streamlit_app.py`, `tests/test_tela.py` (se algum teste procura o texto) | Manual | a legenda diz de onde vem cada coisa, igual ao README ("Arquitetura"); tela aberta depois da mudança; antes do vídeo v0 (MG6) e do congelamento (sex 06/11) | PR que fecha #56 |
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
| NA4 | qua 04/11 | — | **Obrigatório: 1 slide de métricas** com os números do `avaliacao/resultados.csv` (10 casos, 0 trechos removidos, US$ 0,0012 por raio-x, 2,2 s; rodada de 05/11) e o acerto: **8 de 10 batem com o RI** na conferência manual dela; nas 2 que diferem, a diferença é de definição: RD Saúde em "Pré-IFRS 16", Magalu com outra conta do EBIT (ED16). Sem o acerto, o slide parece melhor que a realidade, que o Eduardo tira com o Claude Code. *Sugestão:* `revisao.csv`, com a nota dela para cada raio-x | deck (e `avaliacao/revisao.csv`, se fizer) | o slide de métricas existe |
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
| sex 06/11 | o PR da MA3 (#42) não entra antes do congelamento | a demo usa a busca da `main`, que já funciona; o C1 e o C2 ficam pela metade, e a ética diz isso |
| qualquer dia | uma pessoa com sessões demais (era o Marcos, com MA3, MA4, MA5 e MA6) | feito em 04/11: o Eduardo monta o documento (MA6) e o Marcos revisa |
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
