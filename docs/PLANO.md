# Plano até a banca (versão acelerada)

Meta: **feito, não perfeito**. O congelamento estava previsto para **06/11/2026**; a versão **`v1.0` foi validada e publicada em 07/11/2026**, no commit `2c3e942` (merge do PR #67). Tudo deve ficar pronto na **11/11/2026**, com folga
até a entrega de **ter 17/11** (banca em qui 19/11, dita pelo professor; horário a confirmar). Se a banca vier antes, já estamos prontos.

**O que o projeto precisa ter** vem dos arquivos do professor, em `docs/professor/` (`requisitos_projeto.MD` e
`guia_projeto_final.pdf`). Eles valem mais que este plano: nada que esteja neles pode ser cortado (seção 7).

**Onde está cada coisa:** o que fazer agora → seção 0; quem faz o quê e quando → seção 3; o que o professor exige e o status de
cada item → [REQUISITOS.md](REQUISITOS.md); o que já aconteceu → [HISTORICO.md](HISTORICO.md).

**Como usar:** cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (ex.: MA2). No Claude Code, comece
com `/inicio-de-sessao MA2` e termine com `/fim-de-sessao`: ele faz o Git, escreve no PR o que mudou, abre o PR, espera o CI e
faz o merge depois do seu "pode". **Desde 10/11, cada pessoa registra a própria sessão** (a linha dela na seção 3, uma linha no HISTORICO e a linha do requisito
no REQUISITOS) no PR dela, pelo `/fim-de-sessao`; **a seção 0 é do Eduardo**, que consolida. De 05 a 09/11 só ele editava, para evitar conflito. Guia: [aprender/claude-code.md](../aprender/claude-code.md).

**Hipóteses:** cada pessoa tem de 6 a 12 h por semana, fora a aula. Eduardo, Marcos e Miguel usam o Claude Code;
a Náthally não programa com IA e sobe arquivos pelo navegador do GitHub (seção 3).

---

## 0. Situação atual

**Em 10/11/2026, ~11h30 (Brasília)**

**Foco: validar as fontes na aplicação e fechar a documentação; ROI e ética continuam pendentes.**
Último PR levado: **#79** (10/11, MA8). Os PRs #75, #76, #77 e #79 estão na `main` com CI verde; a tag `v1.0.1` continua como plano B
até a integração real e a conferência final.
A fotografia detalhada de 07/11 permanece no Git: `git show 45686db:docs/PLANO.md`.

### Revisão final (09/11, issue #69)

Três revisores em paralelo (aplicação e infra, IA e ML, dados e documentação), só lendo; cada achado foi reproduzido antes de entrar aqui.
- **Certo:** 259 testes com o PostgreSQL ligado, nenhum pulado (sem o banco, 16 pulam); CI verde nos 5 últimos merges; desde a `v1.0`, só
  documentos mudaram; nenhum dado nem segredo no Git; Terraform `fmt` e `validate` aprovados; tela e banco só em `127.0.0.1`; médias do
  `resultados.csv` iguais às do documento; SQL parametrizado; BPMN 2.0; justificativa (RAG × fine-tuning, chain, memória) e ética completas.
- **Consertado nesta branch (`v1.0.1`):** o validador barra também "bilionária", "milionária" e "uma vez e meia"; o erro de formato do Gemini
  não leva mais o texto dele, com números, para "Detalhes técnicos". Três frases e um teste novos; nenhum dos 10 textos reais seria barrado.
  263 testes, nenhum pulado. No documento: legenda da Figura 1 ("zero ou negativa") e caminho do "8 de 10" (`Semana_02/revisao_manual.md`).
- **Bloqueio fora do código:** o repositório é privado e o professor não é colaborador. O grupo vai dar o acesso (Miguel é o admin).
- **Com dono:** Miguel conserta o exemplo do `README.md:296` (`--cvm 90001` só existe em `falsos/`; com a `data/` real dá `ValueError`) e põe
  na lista de antes da demo `docker compose up -d` e `docker compose ps` com os 2 `healthy` (depois de reiniciar o Docker, só o banco volta
  sozinho). Náthally mede o ROI hoje (NA3). Eduardo regera o PDF quando o ROI e a ética chegarem e tira o "Versão para revisão".
- **Não conferido:** `docker compose config` (a trava bloqueia: o comando imprime o `.env`), tela no navegador, Gemini real, deck, vídeo e ensaio.
- **Cuidado em revisão só leitura:** `python -m raiox.checagem --teste` grava `anomalias.csv` na raiz (ignorado pelo Git).

### Fontes dos números: trecho do DFP + link da CVM (10/11, pedido da Náthally)

A Náthally pediu (ROI: "como faríamos o ROI sem os links?") que o usuário possa conferir de onde vem cada número. Decidido com ela em 10/11: **as duas coisas**.
- **A · trecho:** em "De onde vem cada número", as contas usadas (código, descrição, ano, valor) de cada indicador, lidas da tabela `contas` do PostgreSQL.
- **B · link:** "Baixar DFP (CVM)" por indicador. O `LINK_DOC` vem do arquivo principal de cada zip anual da CVM (`dfp_cia_aberta_AAAA.csv`) e **baixa um `.zip`**, não abre uma página (testado em 10/11 com a AXIA).
- **Desenho:** campo novo `conferir` no C3 (`contratos.md`); módulo novo `raiox/fontes.py` (Eduardo); `scripts/carregar_links.py` grava `data/links_dfp.csv` e a tabela `links_dfp` (Marcos). **Não muda o C2, o `indicadores.csv` nem o K-means e não recarrega as contas.** O texto vem do banco; o LLM não escreve nada disso (regra de ouro).
- **Cuidado:** o link se casa pelo **ano do exercício** (`ano_do_exercicio`, `raiox/limpeza.py:42`), não pelo ano do calendário: a Camil fecha em fev. e um cruzamento por calendário a liga ao DFP errado (fev./2025). Inclui o zip de 2026. Duas empresas (CD_CVM 26239 e 26824) têm dois documentos para a mesma chave; a MA7 ficou com o `ID_DOC` mais recente.
- **Exceção ao congelamento:** a `v1.0.1` continua sendo o plano B. Só entra a `v1.1` se ED17, MA7 e MG8 estiverem na `main` com o CI verde até **qui 12/11, 18h**; senão, corta-se e a Náthally usa o ROI pelo tempo (sem o link). Se o banco estiver fora do ar, `conferir` vem vazio e a demo continua (regra 6).
- **Sessões:** ED17, MA7, MG8, NA7 e ED18 (seção 3). ED17, MA7 e MG8 já estão na `main`. **Prova ponta a ponta com PostgreSQL feita em 10/11 (ED18)**, no Docker: `scripts/carregar_links.py` no contêiner → 2.520 links, 595 de 595 empresas; `preparar_raio_x(..., usar_ia=False)` traz o `conferir` com contas e link para a WEG (5410), a Camil (24228) e uma empresa só com balanço individual (22179): 10 linhas de conta cada, nenhum indicador sem conta. Testes: 287 passed no Mac com o banco; 267 passed e 20 skipped no contêiner. PDF regerado (22 páginas). **Falta:** o print do botão na tela (MG8, Miguel), o ROI (NA7) e a tag `v1.1` até qui 12/11, 18h.

### Fechamento do Eduardo

| sessão | estado verificável em 07/11 | falta para encerrar |
|---|---|---|
| ED15 · instruções Python, issue #57 | ✅ na `main`, PR #67, issue #57 fechada: Python 3.14 nos seis pontos; atalhos param se a criação do ambiente falhar; três testes novos | nada nesta sessão |
| ED9 · congelamento | ✅ `v1.0` publicada no commit `2c3e942`; CI do PR #67 verde e 259 testes locais aprovados. 09/11: `v1.0.1` com o conserto do validador da revisão final | só consertos indispensáveis; nenhum recurso novo |
| ED10 · instalação do zero | venv vazio com Python 3.14.10, dependências instaladas e 256 testes aprovados; imagem Docker reconstruída | outra pessoa seguir o README em outro computador; não foi feito nesta sessão |
| ED11 · avaliação e defesa | avaliação existente conferida: dez casos, zero removidos, 2,15 s; conteúdo e perguntas em [conteudo_eduardo.md](conteudo_eduardo.md) | o Eduardo ensaiar e responder em voz alta; não declarado concluído pela IA |
| MA6 · documento | rascunho 4; BPMN, arquitetura, EDA, justificativa e limites presentes; EDA reexecutada em 07/11 | ROI e ética final da Náthally; revisão do Marcos; respostas do professor |

**Evidências de execução (Mac do Eduardo, 07/11):**
- `python -m pytest -q`, com `~/bootcamp/bin` no PATH e PostgreSQL ligado: **259 passed, nenhum pulado**, incluindo os três testes novos dos atalhos (mais dois subtestes; um aviso de depreciação de uma dependência).
- Mesmo comando no venv criado do zero: **256 passed, nenhum pulado** antes dos três testes novos; `python -m pip check`: sem dependência quebrada.
- Docker reconstruído pelo README: tela e banco `healthy`, health `ok`; testes dentro da imagem: **239 passed, 20 skipped** (conferências que dependem do Git não rodam na imagem).
- Ensaio **funcional com Streamlit AppTest**, dados reais: WEG, Embraer e Ambev geram seis indicadores e cinco parecidas; falha de IA simulada gera texto sem IA. Quatro consultas gravadas no PostgreSQL. **Sem chamada paga e sem inspeção visual da demo**: a automação de entrada no navegador falhou.
- `terraform fmt -check` e `terraform validate`: aprovados. O `apply` com dados reais já foi conferido em 03/11; não foi refeito em 07/11.
- README no GitHub: o Mermaid aparece renderizado na árvore de acessibilidade do Chrome, com tela, banco, CVM, Gemini e Terraform. Isso confirma renderização; não é revisão visual do layout.

**EDA do Marcos reconferida (07/11):** notebook com 15 células de código executadas com os dados reais, quatro gráficos gerados e inspecionados. Base: 595 empresas, 384.591 linhas de contas, 30 crescimentos vazios, 51 setores. O notebook original e os quatro PNG versionados permaneceram idênticos (hashes conferidos); a execução de auditoria salvou as figuras fora do repositório. A EDA já foi incorporada ao PDF; não é pendência de desenvolvimento do Marcos.

**Auditoria geral:** inventário de 114 arquivos versionados, sintaxe dos 33 Python válida, notebooks JSON válidos e links Markdown locais existentes; testes e verificação dos artefatos descritos no PR. Isso não substitui o ensaio humano nem as respostas do professor.

Backups, recibos e logs locais: `../fechamento-2026-11-07/`, com a auditoria em `auditoria-final/` (fora do repositório). O PR registra os arquivos alterados e a reversão.

### Próxima entrega de cada pessoa

| pessoa | próximo resultado concreto |
|---|---|
| Eduardo | entregar os dois slides e falas de [conteudo_eduardo.md](conteudo_eduardo.md); perguntar data/horário e perguntas 2–3 ao professor; finalizar MA6 quando as contribuições chegarem |
| Marcos | subir o `links_dfp.csv` no Drive (MA7); EDA pronta e verificada; ler o documento e a justificativa; preparar a fala de dados, EDA e BPMN. As limpezas do código e a conferência das travas no Windows já entraram no #64 |
| Miguel | dar acesso ao professor no GitHub privado; roteiro e vídeo da demo na `v1.0.1`, guardado em dois lugares; conteúdo da infraestrutura para o deck; depois da MA7, ver o botão "Baixar DFP (CVM)" com a WEG real e mandar o print à Náthally (MG8, NA7) |
| Náthally | ROI hoje, 09/11 (preparação manual × ferramenta, incluindo digitar, ler e conferir); link do deck; ética final e slide de métricas; confirmar a conta de EBIT usada no Magalu |

Todos enviam conteúdo à Náthally até **08/11/2026**. PDF/deck finais previstos para **09/11/2026**; ensaios em **10 e 11/11/2026**.
Entrega em **17/11/2026**, 48 h antes da banca de **19/11/2026** (dita pelo professor ao Eduardo; guia §6; horário a confirmar).

### Progresso: separar produto de entrega

| parte | estado | o que resta |
|---|---|---|
| aplicação | **código congelado: `v1.0.1`** (a `v1.0` mais o conserto do validador, 09/11) | conferir instalação por outra pessoa (ED10); não ampliar o produto |
| documento | **~80%** (estimativa de esforço) | ROI, ética final, revisão e respostas externas |
| slides e ensaios | **não verificado** | deck relatado fora do repositório, sem link; vídeo e tempos de ensaio não apresentados |

Não calcular percentual total sem conferir o deck. A estimativa antiga de ~61% e os ~15% de entregáveis eram de 03/11 e foram retirados.

### Limites e pendências que não pedem novo desenvolvimento

- Issue **#60**, Eduardo: os dez casos caem no mesmo grupo de 312 empresas; limite já declarado na ética e no documento. Levar ao deck e à defesa; **não retreinar antes da banca**.
- O validador barra números, mas não garante sentido correto do texto. A revisão humana permanece necessária.
- ROI sem medição comparável, ética final, link do deck, vídeo e ensaio não podem ser marcados como concluídos por inferência.
- O repositório continua privado; só os quatro integrantes aparecem como colaboradores em 09/11 (`gh api repos/MiguelGrispan/trabalho-tcs/collaborators`). O acesso do professor depende do Miguel e do aceite do professor.
- Perguntas externas: data/horário da banca; se os prompts digitados também são exigidos; se a tabela da CVM atende à expressão “base de conhecimento”. Rascunho **não enviado** em [conteudo_eduardo.md](conteudo_eduardo.md).
- Melhorias de estilo, novas funções, alterações de contrato e refatorações ficam para depois da banca; **a única exceção é a das fontes dos números (bloco acima), com prazo qui 12/11 18h**. Continuam valendo os requisitos do professor e os cortes da seção 7.

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
| Arquivo comum (`README`, `contratos`, `requirements`, `tests/`, `docs/`) | ninguém espera ninguém: o `/fim-de-sessao` mostra quem tem PR aberto e se ele mexe no mesmo arquivo. Só nesse caso, quem terminar primeiro faz o merge e o outro faz `git merge main` | o conflito só acontece no mesmo arquivo; esperar todos os PRs travava o time |

---

## 3. Sessões, em ordem, por pessoa

**Regras de sessão:**
- **Uma sessão = uma linha abaixo = uma branch = um PR.** Começa com `/inicio-de-sessao` e termina com `/fim-de-sessao`.
- **Modo Plan** para mais de um arquivo, para contrato ou para arquivo comum; **manual** para um arquivo só, ou quando você mesmo escreve o código.
- **`/clear`** entre uma tarefa e outra, nunca com mudança sem commit. Detalhes: [aprender/claude-code.md](../aprender/claude-code.md).

### Calendário original (previsões; estado atual na seção 0)

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
| qui 05/11 | ✅ só bugs: #43, #45 e #50 (#63); ✅ processo enxuto (#62) | ✅ MA3b (#51); ✅ MA5 (adiantada, 04/11); ✅ MA4b (#53) | **MG5b: issue #56**; MG6 vídeo v0 | NA3 (prazo do ROI mínimo) |
| sex 06/11 | **ED9: código congelado · tag `v1.0`**; ED11 avaliação final | | | |
| sáb 07/11 | ED10 teste do zero; MA6 rascunho (`docs/documentacao.md`) | revisar o rascunho do MA6 | MG7 vídeo final na `v1.0` (no Mac do Eduardo) | NA5 ética |
| dom 08/11 | **todos mandam o conteúdo dos slides à Náthally** | | | NA5 deck |
| seg 09/11 | MA6 final (o `.md` e o PDF gerado dele) | trocar a citação do `raiox/limpeza.py`; o PDF velho sai | | NA6 deck final |
| ter 10/11 | **ensaio 1 (alvo 15 min, máx. 18, todos)** | | | |
| qua 11/11 | **ensaio 2; tudo pronto para entregar** | | | |
| 12–16/11 | reserva (e prontos, se a banca vier antes) | | | |
| ter 17/11 | **entrega** (48 h antes de qui 19/11) | | | |

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
| ED9 | sex 06/11 | ✅ PR #67 mesclado; `v1.0` publicada em 07/11, commit `2c3e942` | congelar | só bugs | Plan | CI verde + ponta a ponta verde | **tag `v1.0`** |
| ED10 | sáb 07/11 | 🟡 venv vazio e Docker no mesmo Mac, 07/11; falta outro computador | teste do zero em outra máquina, só com o README | consertos | Manual | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisar |
| ED11 | sex 06/11 | 🟡 avaliação conferida, material em `docs/conteudo_eduardo.md`; falta treino pessoal | avaliação final na `v1.0` (só se a IA mudou depois do ED7) + ensaio de defesa | `resultados.csv` | Plan | 10 perguntas da banca respondidas sem consulta | PR |
| ED13 | qua 04/11 | ✅ PR #63 (05/11) | consertar a **issue #43**: a tela aberta antes de carregar a CVM não acha a empresa (cache de `_base()`, `raiox/ia.py:51`). Guia §5: "funciona de ponta a ponta?" | `raiox/ia.py`, `tests/test_raio_x.py` | Manual | o passo a passo da #43 gera o raio-x da WEG; teste novo com essa ordem | PR que fecha #43 |
| ED14 | qui 05/11 | ✅ PR #63; Windows conferido pelo Marcos no #64 (144 passed) | consertar a **issue #45**: no Windows, o `guarda.py` lê a saída do Git em cp1252 (`.claude/hooks/guarda.py:89`), bloqueia commit e merge com `”` ou emoji no diff, e 8 testes das travas falham. Guia §2: "agentic coding" | `.claude/hooks/guarda.py`, `tests/test_guarda.py` | Manual | no Windows do Marcos, sem `PYTHONUTF8`: `python -m pytest -q tests/test_guarda.py` sem falhas e um commit com `”` no diff passa pela trava | PR que fecha #45 |
| ED15 | sex 06/11 | ✅ PR #67 mesclado em 07/11; #57 fechada | consertar a **issue #57**: o `CLAUDE.md:142` e o `aprender/entenda-o-projeto.md:167` mandam `python -m venv .venv` (no Linux do Miguel não existe `python`); o `aprender/COMANDOS.md:16` e os 3 atalhos `.command` usam `python3 -m venv`, que lá é o 3.12. O README já usa `python3.14` (#55). `requisitos_projeto.MD`, Documentação: "instruções para executar" | `CLAUDE.md` (ok no grupo), `aprender/` | Manual | os 6 lugares com `python3.14 -m venv .venv` (Windows: `py -3.14`); antes do ED10 (sáb 07/11) | PR que fecha #57 |
| ED16 | qui 05/11 | ✅ PR desta sessão | 10 raio-x para a Náthally com a Camil corrigida (#46), com o Gemini; K-means e PNG refeitos com os dados do #46 e do #59; diferenças da RD e do Magalu explicadas | `avaliacao/resultados.csv`, `docs/graficos/`, `data/nathally_05_11/` (só no Mac) | Manual | 8 de 10 batem com a conferência dela; 0 removidos; números do K-means trocados nos docs | `eduardo-raiox-nathally` |
| ED12 | sáb 31/10 | ✅ PR #30 (na `main` em 02/11) | travas do Claude Code (R14 e guia §2, agentic coding): `.claude/settings.json`, `.claude/hooks/guarda.py`, subagent `revisor`, import do `requisitos_projeto.MD` | `.claude/`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `aprender/claude-code.md`, `tests/test_guarda.py` | Plan | testes verdes; o hook bloqueia de verdade numa sessão | `eduardo-claude-config` |
| ED17 | ter 10–qua 11/11 | ✅ PR #75 (10/11): `raiox/fontes.py`, campo `conferir` no C3; 255 passed; WEG e Camil conferidas com o `contas.csv` real em SQLite (PostgreSQL real fica no ED18) | **fontes dos números, lado da IA** (pedido da Náthally, R10/R11; guia §2 "confiabilidade" e §7 ROI): (1) campo `conferir` no C3 de `contratos.md` (`contas`: conta, descricao, ano, valor; `link`: URL ou null); (2) `raiox/fontes.py`: lê as contas da tabela `contas` (PostgreSQL) ou de `falsos/contas_falsas.csv` e o link de `links_dfp`; se não achar, `conferir` vai vazio, sem erro; (3) `montar()` em `raiox/ia.py` preenche `conferir` por indicador (3.01; 3.01 de ano e ano−2; 3.05 e 3.01; 3.11 e 3.01; 2.03 e 1; 1); (4) testes. **Duração ~1h30 · energia média · 1º passo: escrever o campo `conferir` no `contratos.md`** | `contratos.md` (ok do grupo), `raiox/fontes.py`, `raiox/ia.py`, `tests/` | Manual | o `conferir` aparece nos 6 indicadores da WEG com dados reais; sem banco ou sem link, o raio-x sai igual ao da `v1.0.1`; o texto do LLM e o validador não mudam; testes verdes | `eduardo-fontes-ia` |
| ED18 | qui 12/11 | 🟡 PR #78 (10/11): prova com PostgreSQL feita (WEG, Camil e a 22179, individual, com contas e link); PDF regerado; 287 passed. **Falta:** tag `v1.1` depois do print (MG8) e do ROI (NA7) | **fechar as fontes:** integração com dados reais (ED17 + MA7 + MG8), documento (`docs/documentacao.md`), README ("como conferir um número"), `docs/roteiro_demo.md`, REQUISITOS/HISTORICO e tag `v1.1`. Se passar das 18h de qui 12/11: não taguear, registrar o corte. **Duração ~40 min · energia baixa · 1º passo: listar os documentos que citam "fonte"** | `docs/`, `README.md`, tag | Manual | WEG, Camil e uma empresa individual mostram trecho e link; PDF regerado | PR + tag `v1.1` |
| ED19 | qui 12/11 (depois de MA7, MG8 e NA7) | — | **consolidar as notas** (nova regra de 10/11: cada um registra a própria sessão): conferir os registros que Marcos e Miguel fizeram sozinhos no PLANO §3, no HISTORICO e no REQUISITOS contra o que está na `main` (✅ sem PR mesclado é erro); levar as 3 linhas da Náthally (ela não usa terminal) e as issues de "Para o Eduardo"; atualizar a seção 0 ("último PR levado") e o R10/R11; resolver conflito de nota, se houver; se a regra nova der problema, reverter no `CLAUDE.md` e nas duas skills. **Duração ~30 min · energia baixa · 1º passo: `gh pr list --state merged --limit 10`** | `docs/PLANO.md` (§0), `docs/REQUISITOS.md`, `docs/HISTORICO.md` | Manual | todos os PRs desde o #74 aparecem na seção 0 e cada sessão nova está ✅ ou 🟡 com prova; nenhuma linha de outra pessoa apagada | PR |

### Marcos (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MA1 | 27/10 | ✅ PR #4 | revisar o #4: o código é seu, só os imports mudaram; decidir sobre o `scripts/dados.py` | — | — | #4 aprovado | `marcos-porta-dados` |
| MA2 | qui 29–sáb 31/10 | ✅ PR #21 (Marcos, 29/10) e PR #22 (Eduardo, 30/10, com o ok do Marcos): o "pronto quando" passa. Sobram para a MA3: `cd_cvm` int e só ativas no C1, tabela `indicadores` (seção 0) | **PostgreSQL na `main`** (regra do professor): trazer o `5508116` para a estrutura da `main` (sem `src/`), `DATABASE_URL` e `TEST_DATABASE_URL` no `.env.example`, serviço postgres no CI (`.github/workflows/testes.yml`) para os testes do banco não pularem; e o C1/C2: CSV padrão (sem `sep=";"` e sem `decimal=","` na **escrita**), `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `scripts/`, `raiox/dados.py`, `requirements.txt`, CI, `tests/` | Plan | CI verde **rodando** os testes do banco (não pulados); `python -m pytest -q tests/test_ponta_a_ponta.py` passa com os seus dados reais | `marcos-postgres` → PR (Eduardo + Miguel) |
| MA3 | sex 30–sáb 31/10 (atrasada) | ✅ PR #46 (mesclado em 03/11): C1 e C2, S1, S2 (13 linhas, 0,00%), #17 (o ano do exercício: Camil = DFP de 28/02/2026), corte de R$ 10 mi ok, `checagem` sem "erro". Zip da `data/` no Drive, com o link no grupo (04/11) | dados reais + checagem + 5 empresas conferidas no RI; zip da `data/` no Drive | `avaliacao/conferencia.csv`; consertos | Manual | diferença < 1%; nenhum "erro"; link no grupo | PR |
| MA3b | qui 05/11 | ✅ PR #51 (na `main` em 04/11): `chmod(0o644)` e teste novo; conferido pelo Miguel no Linux (`-rw-r--r--`, Camil sem `chmod`); #48 fechada | consertar a **issue #48**, achada pelo Miguel em 04/11: o `publicar()` grava a `data/indicadores.csv` com permissão só do dono (`NamedTemporaryFile`), e no Docker do Linux a tela não lê o arquivo (todo raio-x falha). Guia §5: "A aplicação funciona de ponta a ponta na demonstração?" (20%) | `scripts/indicadores.py`, `tests/test_dados.py` | Manual | depois de `docker compose run --rm --user "$(id -u):$(id -g)" tela python scripts/indicadores.py`, `ls -la data/indicadores.csv` → `-rw-r--r--` e a tela gera o raio-x sem o `chmod`; teste novo da permissão; antes do vídeo v0 (MG6) | PR que fecha #48 |
| MA4 | dom 01–ter 03/11 (feita em 04/11) | ✅ PR #54 na main; notebook real reexecutado sem erro em 07/11 (15 células de código, quatro gráficos; originais preservados). Entrega de 04/11: notebook montado pelo Claude Code a partir do `scripts/graficos.py`; "Restart & Run All" com a `data/` real sem erro; `tests/test_eda.py` roda o notebook com os falsos no CI; achado da NTS → issue #53 | EDA com 4 gráficos (nulos, distribuições, extremos, cobertura) | `notebooks/eda.ipynb`, `docs/graficos/` | Manual | "Restart & Run All" sem erro | PR |
| MA4b | qui 05/11 | ✅ PR da branch `marcos-escala-primeiro-ano` (05/11): o primeiro ano comparado com o seguinte, pela receita e pelo ativo juntos; 2 testes novos (o 1º falhava antes); recarga: NTS +107.154% → +7,3%, só ela mudou; notebook rodado de novo. JBS N.V. fica de fora (receita zero em 2023): limite no MA6 | consertar a **issue #53**, achada pela EDA em 04/11: o `encontrar_escala_errada` (`raiox/limpeza.py:165-192`) só compara cada ano com o anterior, e o erro de escala no primeiro ano da base passa (NTS: 2023 de 1.000 a 2.000 vezes menor, crescimento de +107.154%; o JBS N.V. tem o mesmo salto no ativo, com receita zero em 2023). Guia §2 (limpeza com Pandas) e §5 (qualidade técnica, 30%) | `raiox/limpeza.py`, `tests/test_limpeza.py`; recarga da `data/` | Manual | teste novo com o primeiro ano marcado (e que falha sem o conserto); depois da recarga, o crescimento da NTS perto de +7% e o notebook rodado de novo; o grupo avisado para recarregar. Se não der até o congelamento (sex 06/11): limite no documento (MA6) e a NTS fora da demo | PR que fecha #53 |
| MA5 | qua 04–qui 05/11 | ✅ PR #52 (na `main` em 04/11): `docs/bpmn/raio-x-comercial.bpmn` e `.png`, desenhados pelo Claude Code a partir do código; o bpmn-js abre com 0 avisos (falta abrir no demo.bpmn.io) e tem as 2 decisões. O de hoje não foi feito (corte 1, seção 7) | BPMN 2.0 com o Raio-X (obrigatório) e o de hoje (se der tempo), no bpmn.io | `docs/bpmn/` | Plan (o Claude só revisa) | abre no bpmn.io; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | sáb 07–seg 09/11 | ➡️ com o **Eduardo** (decidido em 04/11); o Marcos revisa o rascunho no sáb 07/11 | montar o documento do projeto, escrito em markdown e gerado em PDF (o R aceita markdown; o G §6 pede PDF: vão os dois) | `docs/documentacao.md`, `docs/documentacao.pdf` | Manual | etapas desenvolvidas no processo (R Documentação; a base é o `docs/HISTORICO.md`) + BPMN + justificativa + ética + arquitetura + seção "Dados e limpeza" (as regras do `raiox/limpeza.py`, no lugar do `docs/Raio-X Comercial.pdf`); o Marcos revisou | PR (Eduardo) |
| MA7 | qua 11/11 | 🟡 PR #77 mesclado; falta apenas o arquivo no Drive · branch `marcos-links-dfp` (10/11): `data/links_dfp.csv` e tabela `links_dfp` com 2.520 linhas; `python scripts/carregar_links.py` mostra "Cobertura: 595 de 595 empresas com link" (nenhuma sem link); Camil = `02422820260228401.zip` (fim em 28/02/2026), exercício 2025; duplicatas 26239 e 26824: fica o `ID_DOC` mais recente; 13 testes em `tests/test_links.py`; 284 passed e 3 skipped (só macOS), com PostgreSQL, no Windows do Marcos. **Falta:** subir o `links_dfp.csv` no Drive | **links da CVM:** `scripts/carregar_links.py` lê o arquivo principal (`dfp_cia_aberta_AAAA.csv`: `CD_CVM`, `DT_REFER`, `VERSAO`, `ID_DOC`, `LINK_DOC`) dos zips de 2023 a 2026 (o de 2026 pode dar 404, como no `carregar_dfp.py`); calcula o ano com `ano_do_exercicio(DT_REFER)`, troca `http` por `https`, resolve as duplicatas (CD_CVM 26239 e 26824) e grava `data/links_dfp.csv` + tabela `links_dfp` (`cd_cvm` int, `ano`, `versao`, `id_doc`, `link_doc`). **Duração ~1h30 · energia média · 1º passo: baixar o zip de 2026 e abrir o CSV principal** | `scripts/carregar_links.py`, `tests/test_links.py`, `aprender/COMANDOS.md` | Manual | teste com um zip pequeno falso; cobertura conferida empresa por empresa contra o `indicadores.csv` (Camil = fim em fev./2026); lista das sem link; `links_dfp.csv` no zip do Drive; não mexe em `contas.csv` nem em `indicadores.csv` | `marcos-links-dfp` |
| MA8 | 10/11 | 🟡 PR da branch `marcos-bpmn-fontes` (10/11): tarefa "Anexar as fontes" entre montar os indicadores e "IA ligada?", depósito "PostgreSQL: contas e links_dfp" e nota; o bpmn-js 17.11.1 abre com 0 avisos e o PNG tem 3900 × 1125. **Falta:** o Eduardo gerar de novo o `docs/documentacao.pdf` | BPMN igual ao código das fontes (`raiox/ia.py:313`, `raiox/fontes.py`); documento e falas acertados | `docs/bpmn/`, `docs/documentacao.md`, `docs/roteiro_fala.md` | Claude Code | o diagrama mostra o passo das fontes | `marcos-bpmn-fontes` |

### Miguel (Claude Code)

| # | data | status | objetivo | altera | modo | pronto quando | git |
|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | ✅ conferido em 30/10: PR e check `testes` obrigatórios, só merge commit, apagar branch após o merge; tela rodando no Docker (o print vai para o grupo) | configurar o GitHub (seção 2, "Proteção da `main`"); rodar a tela local | configurações | só leitura | as 3 configurações feitas; print da tela no grupo | — |
| MG2 | qui 29–sex 30/10 | ✅ PR #24 (30/10): os 2 contêineres `healthy`, health `ok`, `carregar_dfp.py` no banco do contêiner, 87 passed no contêiner | `Dockerfile` + `.dockerignore` + `docker-compose.yml` (tela + PostgreSQL com volume do banco; `data/` como volume; chave e `DATABASE_URL` por variável) | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Plan | `docker compose up` sobe os 2; `curl localhost:8501/_stcore/health` → `ok`; `scripts/carregar_dfp.py` grava no PostgreSQL do contêiner | `miguel-docker` → PR (Eduardo) |
| MG3 | sáb 31/10–dom 01/11 | ✅ PR #29 (31/10): `apply` sobe os 2 `healthy`; `destroy` + `apply` mantém o banco e a `data/`; 87 passed no contêiner; 2º `plan` sem mudanças. IA pelo Terraform vista pelo Miguel. Portas padrão e Mac conferidos pelo Eduardo em 03/11 (seção 0) | **Terraform na `main`, obrigatório** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform"): provider docker com os 2 contêineres (tela + PostgreSQL), a partir do `terraform/` da branch `docs-docker-e-terraform`. Prazo: dom 01/11; reserva: seg 02/11 com o Eduardo. Não pode ser cortado | `infra/` | Plan | `terraform apply` sobe a tela e o banco; `destroy` + `apply` mantém a `data/` e o banco | PR |
| MG4 | dom 01–ter 03/11 | ✅ PR #36 (02/11): WEG, Embraer e Ambev geram o raio-x no contêiner, e as 3 consultas estão na `consultas`; 8 testes em `tests/test_tela.py`. Gemini de verdade conferido em 03/11 (WEG). Volta para o modo sem IA com o Gemini fora do ar conferida em 03/11 (chave inválida, WEG): funciona; os 2 problemas de aparência viraram a MG4b | tela com dados reais e **com o banco** (R Aplicação: banco de dados): `RAIOX_DADOS` (`falsos`/`real`) no lugar do `USAR_DADOS_FALSOS`, e com `real` a busca e o `registrar_consulta` usam o PostgreSQL (`raiox/dados.py`); volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try`; `tests/test_tela.py` | `app/`, `.env.example`, `tests/` | Plan | 3 empresas reais geram raio-x no contêiner, e cada consulta aparece na tabela `consultas` | PR (Eduardo) |
| MG4b | qua 04/11 | ✅ PR #47 (03/11, adiantada): com a chave falsa, a WEG mostra o aviso curto e "Texto montado sem IA: o Gemini não respondeu."; 3 testes novos e o do rodapé em `tests/test_tela.py`; `docker compose ps` → `127.0.0.1:8501`. Junto: os avisos de banco vazio e desligado citam o Terraform | consertar as issues **#38** (o aviso de falha da IA mostra o JSON inteiro do Google), **#39** (o topo diz "Texto escrito pelo Gemini" quando o texto foi montado sem IA) e **#44** (o compose abre a tela para a rede toda: `127.0.0.1:8501:8501`, como o Terraform), achadas pelo Eduardo em 03/11. Guia §5: "a interface é amigável ao usuário?" (protótipo, 20%) | `app/streamlit_app.py`, `tests/test_tela.py`, `docker-compose.yml` | Manual | com `GOOGLE_API_KEY=chave-falsa-teste RAIOX_IA_REAL=1 docker compose up -d --build`, a WEG mostra um aviso curto e o topo não diz "escrito pelo Gemini"; teste novo para cada issue; `docker ps` mostra `127.0.0.1:8501`; antes do vídeo v0 (MG6) e do congelamento (sex 06/11) | PR que fecha #38, #39 e #44 |
| MG5 | qua 04/11 | ✅ PR #55 (04/11): seção "Arquitetura" no README (diagrama em Mermaid + 6 frases), `docs/arquitetura.png`, seção "Pré-requisitos", `python3.14 -m venv`; 3 testes em `tests/test_readme.py`. Falta um colega ler o README (o "pronto quando") | diagrama de arquitetura + README (tema, objetivo e tecnologias já estão; pré-requisitos com Python 3.14; rodar local, Docker e Terraform) | `docs/arquitetura.png`, `README.md` | Manual | um colega entende o fluxo lendo o README; o README cobre o que o R pede em "Documentação" | PR |
| MG5b | qui 05/11 | ✅ PR #61, na main desde 05/11 | consertar a **issue #56**: com os dados reais, a tela diz "Empresas e números da CVM (DFP), buscados no banco PostgreSQL." (`app/streamlit_app.py:71`), mas os números vêm da `data/indicadores.csv`; só a busca e o registro usam o banco. Achada pelo `revisor` no #55. Guia §3 (a frase aparece na demo) e §2, "Governança e Ética" (confiabilidade) | `app/streamlit_app.py`, `tests/test_tela.py` (se algum teste procura o texto) | Manual | a legenda diz de onde vem cada coisa, igual ao README ("Arquitetura"); tela aberta depois da mudança; antes do vídeo v0 (MG6) e do congelamento (sex 06/11) | PR que fecha #56 |
| MG6 | qui 05/11 | — | roteiro de 6 min da demo + vídeo v0 | — | — | vídeo salvo em 2 lugares | — |
| MG7 | sáb 07/11 | — | vídeo final na `v1.0` | — | — | vídeo salvo em 2 lugares | — |
| MG8 | qua 11/11 (depois do C3 do ED17) | 🟡 PR #76 mesclado; falta o print real para o deck: em "De onde vem cada número", uma aba por indicador com as contas do DFP e o botão "Baixar DFP (CVM)" quando há link (`app/streamlit_app.py`, `mostrar_fonte`); sem `conferir`, a tela fica como na `v1.0.1`; 3 testes novos em `tests/test_tela.py`; 274 passed com o PostgreSQL (Linux do Miguel); WEG real no navegador (Docker): contas 3.01 e 3.05 batem com a tabela `contas`. **Falta, depois da MA7:** ver o botão com a WEG real e salvar o print para o deck (NA7) | **tela das fontes:** em "De onde vem cada número", por indicador, uma tabela com as contas (`conferir.contas`) e o botão "Baixar DFP (CVM)" (`conferir.link`; explicar em uma linha que baixa um `.zip`); sem `conferir`, a tela fica como na `v1.0.1`; print novo para o deck. **Duração ~45 min · energia baixa · 1º passo: abrir `app/streamlit_app.py:189`** | `app/streamlit_app.py`, `tests/test_tela.py` | Manual | WEG mostra tabela e botão; sem `conferir` (modo `falsos` ou banco fora) a tela não quebra; teste novo; print salvo | `miguel-tela-fontes` |

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
| NA6 | seg 09–qua 11/11 | — | **Obrigatório: o deck final** (`requisitos_projeto.MD`, Documentação; guia §6) e ensaios cronometrados (guia §3 diz 20 min, mas vale a regra de 09/11: máx. 18 min + 12 de banca, alvo 15; guia §7 pede o ensaio; o grupo marcou 2) | deck | ensaio de 15 min, nunca acima de 18 |
| NA7 | qua 11/11 | — | **ROI com as fontes:** refazer 1 vez o tempo do passo "conferir" com a tela nova (trecho + link) e escrever no ROI "fonte em 1 clique"; slide de métricas ganha o print do Miguel (MG8). **Duração ~20 min · energia baixa · 1º passo: cronometrar 1 conferência** | `docs/produto/`, deck | Manual | 1 tempo medido e 1 frase no ROI | PR |

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
| `tests/test_limpeza.py`, `test_carregar_dfp.py`, `test_dados.py`, `test_banco.py` (PRs #4 e #21; `test_verificar_automatico.py` saiu no #64) | regras de limpeza, carga da DFP (rede simulada), catálogo e C1 em PostgreSQL (banco de teste separado: `tests/banco_teste.py`); o C2 (CSV padrão, `cd_cvm` int, mesma tabela no banco) em `test_publicar_grava_o_mesmo_c2_no_csv_e_no_banco` (#46; era `test_calcular_grava_csv_padrao_com_cd_cvm_inteiro`, do #22) | Marcos | sim: o CI sobe um PostgreSQL desde o #22 (sem ele, os testes do banco pulam; `-rs` mostra quais) |
| C1 e C2 no banco, ano do exercício (MA3, PR #46) | `test_busca_exige_cadastro_ativo_e_indicadores`, `test_sem_a_tabela_indicadores_a_busca_volta_vazia`, `test_publicar_grava_o_mesmo_c2_no_csv_e_no_banco` (`tests/test_dados.py`); `test_ano_do_exercicio_e_o_ano_com_mais_meses` e `test_limpar_demo_usa_o_ano_do_exercicio_e_nao_o_do_arquivo` (`tests/test_limpeza.py`); `test_main_usa_o_exercicio_de_quem_fecha_fora_de_dezembro`, `test_main_segue_sem_o_arquivo_do_ano_seguinte` e `test_main_para_se_falta_o_arquivo_de_um_dos_anos` (`tests/test_carregar_dfp.py`); `test_desiste_rapido_se_o_banco_nao_responde` (`tests/test_banco.py`) | Marcos | sim |
| `tests/test_tela.py` (MG4, MG4b) | a tela com os falsos: busca, gerar, 6 métricas, sem erro; com a IA fora do ar, aviso de uma frase (o erro em "Detalhes técnicos" e no log) e o topo e o rodapé sem "escrito pelo Gemini"; os avisos do banco com os comandos do Terraform | Miguel | sim |
| `tests/test_ponta_a_ponta.py` | C2 real, raio-x sem IA de 3 setores, `cd_cvm` dos casos (todos preenchidos e na tabela real) | Eduardo | **não**: pula sem `data/`. Rodar local antes de `v0.1-demo`, `v1.0` e no teste do zero |
| `tests/test_aprender.py` | o notebook `aprender/passo_a_passo.ipynb` roda inteiro e vai para o Git sem saídas; os três atalhos param se não criarem o ambiente (esses três testes pulam no Windows) | Eduardo | sim |
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
| sáb 07/11/2026 (previsto: 06/11) | os 4 | tag `v1.0` publicada no merge do #67 (`2c3e942`) | código |
| dom 08/11 | todos → Náthally | conteúdo dos slides | roteiro |
| qua 11/11 | os 4 | tudo pronto para entregar | entregáveis |
| qui 12/11, 18h | Eduardo, Marcos, Miguel | fontes dos números na `main` (ED17, MA7, MG8) e tag `v1.1`, ou corte | código (volta a congelar) |

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
| R10 Governança e ética | NA5, ED8, MG4, MG4b, ED17, MA7, MG8 |
| R11 ROI | NA1, NA3, NA7 |
| R12 Métricas | NA2, ED5, ED7, NA4, ED11 |
| R13 Backend, frontend e banco na aplicação | MG4, MG4b (pergunta ao professor respondida em 02/11: Streamlit vale, em 2 contêineres) |
| R14 Prompts do vibecoding | ED8 |
| D1 Repositório | ED0, MA1, NA1, ED9 |
| D1b README | MG5, ED8, ED10 |
| D1c Infra (Terraform) e notebooks | MG2, MG3, MA4 |
| D2 Documento (etapas, BPMN, justificativa, ética) | MA6, do Eduardo desde 04/11 (com MA5, ED8, NA5, MG5) |
| D3 Deck | NA5, NA6 |
| D4 Vídeo | MG6, MG7 |
| D5 18 minutos (alvo 15) | NA6 + ensaios de 10–11/11 |

---

## 7. Riscos, plano B e o que cortar

| marco | risco | plano B |
|---|---|---|
| sex 30/10 | o Miguel não abre o PR do Docker | no sáb 31/10, o Eduardo abre o PR com os 7 ajustes e o `docker-compose.yml` com o PostgreSQL (seção 0) e o Miguel revisa |
| dom 01/11 | o Terraform não sobe | a dupla de reserva da infra (Miguel ↔ Eduardo) termina na seg 02/11 (feriado). **Não pode ser cortado**: o `requisitos_projeto.MD` exige o Terraform (o guia aceitava "ou conteinerização", mas vale o mais exigente) |
| ter 03/11 | o PostgreSQL não sobe no Docker na demo | `docker compose up` ensaiado no teste do zero (ED10); vídeo gravado (MG6/MG7); a busca falsa (`falsos/`) ainda mostra a tela sem banco |
| ter 03/11 | a demo não roda inteira | qua e qui 04–05/11 só para isso; o vídeo vira obrigatório; demo por `docker run` ou `streamlit run` local |
| dia da banca | a API falha ou o crédito acaba (erro 402) | a tela volta sozinha para o modo sem IA, com aviso (MG4); vídeo; saldo conferido em 08/11 |
| qualquer dia | a banca é **antes** | o código está congelado na `v1.0` (07/11); meta de entregáveis prontos em 11/11 |
| resolvido em 03/11 | MA3 (#42 e #17) antes do congelamento | PR #46 mesclado; C1 e C2 atendidos, sem cortar requisito |
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
