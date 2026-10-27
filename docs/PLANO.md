# Plano até a banca

Versão de **ter 27/10/2026**. A matriz do que o guia exige está em [REQUISITOS.md](REQUISITOS.md).
Os detalhes técnicos do que está quebrado (com comandos de prova) estão em [seguindo-o-projeto.md](seguindo-o-projeto.md).

**Como usar:**
- Cada linha das tabelas da seção 3 é uma sessão de trabalho, com um código (por exemplo, MA2).
- Para começar, abra o Claude Code (ou o Codex) e diga:
  > Leia o CLAUDE.md e faça a sessão MA2 do docs/PLANO.md.
- Quando terminar, marque a sessão como feita aqui e atualize a linha correspondente no REQUISITOS.md, no mesmo PR.

**Hipóteses deste plano:**
- Cada pessoa tem de 6 a 12 h por semana, fora a aula.
- Eduardo e Marcos usam Claude Code. O Miguel usa Codex ou Claude Code. A Náthally não usa IA para programar: ela sobe arquivos pelo navegador.
- Banca prevista para **qua 18/11 (a confirmar)**, com entrega na seg 16/11.

---

## 1. Fundação: arquivos iguais para todos

Entram no PR de padronização do Eduardo (sessão ED0), exceto os da última linha.

| arquivo | conteúdo mínimo | por quê |
|---|---|---|
| `docs/REQUISITOS.md`, `docs/PLANO.md` | a matriz do guia e este plano | um só lugar para "o que falta" e "quem faz quando" |
| `CLAUDE.md` | data da banca, leitura do PLANO, regras de Git | é o que o Claude Code lê em toda sessão |
| `AGENTS.md` (novo) | aponta para CLAUDE.md, REGRAS-IA.md e contratos.md; regras que não podem ser quebradas | o Codex lê `AGENTS.md`, não `CLAUDE.md`; sem ele, o agente do Miguel não conhece as regras |
| `REGRAS-IA.md` | §5 Git: branch curta por tarefa, `merge` em vez de `rebase`, PR pelo navegador | as branches pessoais longas criaram duas histórias separadas |
| `contratos.md` | C2: CSV padrão e `cd_cvm` int; C3: fonte igual ao código; C4: casos com `cd_cvm` e `empresa` | contrato antes de código: o Marcos e a Náthally escrevem contra este texto |
| `requirements.txt` | versões fixas (`==`) que passam nos testes, Python 3.14 | sem versão, o build do Docker na véspera pode trazer outro LangChain e quebrar a demo |
| `pytest.ini` (novo) | `testpaths = tests`, `pythonpath = .` | todos e o CI rodam `python -m pytest -q` da raiz, do mesmo jeito |
| `.gitignore` | mais `*.db`, `*.zip`, `*.parquet`, `myenv/` | um banco ou zip salvo fora de `data/` não entra por engano |
| `.github/workflows/testes.yml` (novo) | roda os testes em todo PR e em todo push na `main` | é o que garante que nada entra com teste falhando, sem depender de memória |
| `.github/pull_request_template.md` (novo) | checklist do REGRAS-IA e "Feito com IA / Eu conferi" | a regra vira automática; essas linhas viram a seção "Como usamos IA" do README |
| `Dockerfile`, `.dockerignore`, `infra/` | Miguel, sessões MG2 e MG3 | dono da infra |

---

## 2. Git

| tema | combinado | por que, e não a alternativa óbvia |
|---|---|---|
| Modelo | `main` + **uma branch curta por sessão**, com nome `pessoa-tarefa` (ex.: `marcos-porta-dados`) | branch pessoal longa acumula diferença e vira PR gigante; uma por tarefa vira PR pequeno, que um iniciante consegue revisar. Hífen, não barra: o Git não deixa criar `eduardo/...` enquanto existir a branch `eduardo` |
| Criar a branch | `git switch main` → `git pull` → `git switch -c pessoa-tarefa` | sempre a partir da `main` atual: nunca mais história separada |
| Quando abrir PR | quando o "pronto quando" da sessão passa e `python -m pytest -q` está verde. Uma sessão, um PR. PR em rascunho pode abrir antes | PR pequeno é revisado no mesmo dia |
| Quem revisa | quem **recebe** o contrato. Marcos → Eduardo (C2), e também o Miguel se mexer no C1. Eduardo → Marcos, ou o Miguel se mexer no C3. Miguel → Eduardo. Náthally → Eduardo | quem recebe é quem percebe quando quebra |
| Quem faz o merge | o autor, depois de 1 aprovação e com o CI verde | tira o Miguel do gargalo |
| Tipo de merge | **merge commit** (o que já usamos). O Miguel desliga squash e rebase e liga "apagar branch após o merge" | guarda cada commit pequeno para a banca ver o processo, e não quebra quem continua na mesma branch depois do merge |
| Proteção da `main` | o Miguel olha em Settings → Branches. **Se der:** PR obrigatório, 1 aprovação, check `testes` obrigatório, sem force push. **Se não der** (repositório privado em conta gratuita): pacote de estudante do GitHub, ou a regra do time mais o CI no PR | a API respondeu 404 em 27/10; não deu para saber se é falta de permissão ou do plano |
| Trazer a `main` para a sua branch | `git switch main` → `git pull` → `git switch pessoa-tarefa` → `git merge main` → `python -m pytest -q` → `git push`. Se der conflito: `git merge --abort` e fale com o dono do arquivo | o `rebase` reescreve a história e exige `push --force`, o jeito mais comum de apagar trabalho do colega |
| Quando trazer | antes de abrir o PR, e sempre que entrar na `main` um PR que mexe em contrato ou em arquivo comum | — |
| Tags | `v0.1-demo` na sex 06/11 (demo rodou) e `v1.0` na ter 10/11 (congelado). Depois, só `v1.0.1`, `v1.0.2`… com consertos. Quem cria é o Eduardo: `git tag -a v1.0 -m "versão da banca"` e `git push origin v1.0` | avaliação final, vídeo e teste do zero rodam na mesma versão |
| Arquivo comum (`README`, `contratos`, `requirements`, `tests/`, `docs/`) | um PR por vez; avise no grupo antes | evita conflito |
| Limpeza | apagar `eduardo` e `fundacao` (já estão na `main`); `tratamento_dados` e `feat/metricas` só depois de portadas | ninguém perde nada |

---

## 3. Sessões, em ordem, por pessoa

**Regras de sessão** (Claude Code; quem usa Codex segue o mesmo pelo `AGENTS.md`):
- **Uma sessão = uma linha das tabelas abaixo = uma branch = um PR.**
- **Modo Plan** quando a sessão mexe em mais de um arquivo, em contrato ou em arquivo comum.
- **Manual** (você aprova cada edição) quando mexe em um arquivo só, ou quando você mesmo escreve o código.
- No Codex, comece com: "proponha um plano, não altere arquivos".
- **Sessão nova** para cada tarefa.
- **`/clear`**:
  - depois do commit ou do PR da tarefa, antes de começar outra no mesmo terminal;
  - quando a conversa mudou de assunto;
  - quando o Claude começa a esquecer as instruções do início.
  - Nunca use `/clear` com mudança sem commit: anote antes onde parou.
- **Fim de toda sessão:** `python -m pytest -q` → `git status` (leia a lista) → commit → push → PR.

### Calendário

| data | Eduardo | Marcos | Miguel | Náthally |
|---|---|---|---|---|
| ter 27/10 | ED0 padronização (PR) | MA1 portar dados | — | — |
| qua 28/10 | ED1 3 raio-x reais | MA1 | MG1 entrar + revisar o PR ED0 | NA1 portar + regras v2 |
| qui 29/10 | ED2 testes independentes | MA2 cumprir C1/C2 | MG2 Docker | NA1 |
| sex 30/10 | revisões | MA2 | MG2 | NA2 casos C4 |
| sáb 31/10 | ED3 regras v2 no prompt | MA3 dados reais | MG3 Terraform | NA2 |
| dom 01/11 | ED4 segmentos reais + PCA | MA3 (Drive) | MG3 | NA2 (entrega) |
| seg 02/11 | feriado | feriado | feriado | feriado |
| ter 03/11 | ED5 `avaliar.py` | MA4 EDA | MG4 tela com dados reais | NA3 tempo manual e testes |
| qua 04/11 | ED6 teste ponta a ponta | MA4 | MG4 | NA3 |
| qui 05/11 | ED7 rodada com IA | MA5 BPMN | MG5 arquitetura + README | NA3 |
| sex 06/11 | **demo ponta a ponta · tag `v0.1-demo`** | | MG6 demo + vídeo v0 | NA3 (3 testes feitos) |
| 07–08/11 | ED8 justificativa + "Como usamos IA" | MA5 | — | NA4 revisão + métricas |
| 09–10/11 | ED9 congelar · **tag `v1.0`** | só bugs | só bugs | NA5 ética + deck |
| qua 11/11 | ED10 teste do zero | | | (empresta a máquina) |
| qui 12/11 | ED11 avaliação final + ensaio de defesa | MA6 PDF | | recebe o conteúdo dos slides |
| sex 13/11 | | MA6 | MG7 vídeo final | NA6 deck |
| 14–15/11 | **2 ensaios de 20 min (todos)** | | | |
| seg 16/11 | **entrega** (48 h antes de qua 18/11) | | | |

### Eduardo (Claude Code)

| # | data | objetivo | lê | altera | modo | testes | pronto quando | git |
|---|---|---|---|---|---|---|---|---|
| ED0 | ter 27/10 | arquivos comuns + PLANO + REQUISITOS | guia, repositório | lista da seção 1 | Plan | `pytest -q`; CI no PR | PR aberto com CI verde; Marcos aprova o `contratos.md`; Miguel aprova o CI | `eduardo-padronizacao` → PR |
| ED1 | qua 28/10 | 3 raio-x reais para a Náthally | `scripts/carregar_dfp.py`, `scripts/indicadores.py`, `raiox/ia.py` | nada no Git (converte o CSV só na sua `data/`) | Manual | `python -m raiox.ia … --sem-ia` e 3 chamadas com IA (≈ US$ 0,003) | 3 empresas de setores diferentes, `removidos` conferido, enviado | nenhum |
| ED2 | qui 29/10 | testes que não dependem de `data/`; "balanço consolidado" | `tests/test_raio_x.py`, `raiox/ia.py`, `raiox/segmentos.py` | os mesmos | Manual (você escreve o teste) | `pytest -q` com e sem `data/indicadores.csv` | verde nas duas situações | `eduardo-testes-isolados` → PR (Marcos) |
| ED3 | sáb 31/10 | regras v2 da Náthally no `REGRAS` | `avaliacao/regras_prompt.md`, `raiox/ia.py` | `raiox/ia.py` | Manual | `pytest` + 3 chamadas reais | 3 raio-x sem item removido por dígito e com a posição certa | PR (a Náthally lê o texto no GitHub) |
| ED4 | dom 01/11 | segmentos com dados reais + gráfico 2D (PCA) | `raiox/segmentos.py`, `data/indicadores.csv` | `raiox/segmentos.py`, `docs/graficos/*.png` | Manual (PCA à mão) | `pytest`; olhar 2 grupos | `segmentos.csv` real; k e silhueta no REQUISITOS; 2 PNG; 2 linhas sobre cada grupo | PR (Marcos) |
| ED5 | ter 03/11 | `avaliacao/avaliar.py` (C4) | C4, `casos_avaliacao.csv`, `raiox/ia.py` | `avaliacao/avaliar.py`, `tests/test_avaliar.py` | Plan | 2 casos falsos sem IA → colunas do C4 | `python -m avaliacao.avaliar --sem-ia` grava o `resultados.csv` do C4 | PR (Marcos) |
| ED6 | qua 04/11 | teste ponta a ponta com dados reais | `scripts/`, `raiox/` | `tests/test_ponta_a_ponta.py` (pulado se não houver `data/`) | Plan | carregar → indicadores → segmentos → raio-x sem IA de 3 empresas | verde local, pulado no CI | PR (Miguel) |
| ED7 | qui 05/11 | rodada de avaliação com IA (avisar o grupo: mais de 10 chamadas) | `avaliacao/avaliar.py` | `avaliacao/resultados.csv` | Manual | — | N casos e custo total anotados (esperado < US$ 0,05) | PR |
| ED8 | 07–08/11 | justificativa técnica para o PDF + README "Como usamos IA" | `raiox/ia.py`, `raiox/segmentos.py`, PRs | `docs/justificativa.md`, `README.md` (uma seção) | Manual (você escreve; a IA confere cada frase com arquivo e linha) | — | o Marcos lê e entende; toda afirmação tem prova | PR |
| ED9 | 09–10/11 | congelar | tudo | só bugs | Plan | CI + ponta a ponta | tudo mesclado e verde | **tag `v1.0`** |
| ED10 | qua 11/11 | teste do zero em outra máquina, só com o README | `README.md` | consertos numa sessão Manual curta | — | seguir o README | rodou sem ajuda, ou cada falha virou PR | `v1.0.1` se precisou de conserto |
| ED11 | qui 12/11 | avaliação final na `v1.0` + ensaio de defesa (o Claude faz perguntas da banca, sem editar nada) | — | `resultados.csv` final | Plan | — | 10 perguntas respondidas em voz alta, sem consulta | PR (só o CSV) |

### Marcos (Claude Code)

| # | data | objetivo | lê | altera | modo | testes | pronto quando | git |
|---|---|---|---|---|---|---|---|---|
| MA1 | 27–28/10 | trazer a branch `tratamento_dados` para a estrutura da `main` | `origin/tratamento_dados`: `src/limpeza.py`, `src/dados.py`, `scripts/`, `tests/` | `raiox/limpeza.py` (novo), `scripts/carregar_dfp.py`, `scripts/indicadores.py`, `raiox/dados.py` (manter a normalização de `cd_cvm`), `tests/test_limpeza.py`, `tests/test_carregar_dfp.py`, `tests/test_dados.py` (trocar `src.` por `raiox.`). **Não trazer:** `graficos.py`, `contracts.md`, `verificar_automatico.py` (usa yfinance), `conferencia.csv` da raiz. **Não mexer** no `requirements.txt` | Plan | `pytest -q` (os 8 + os seus) | tudo verde; `git status` sem dados | `marcos-porta-dados` → PR (Eduardo) |
| MA2 | 29–30/10 | cumprir C1 e C2: CSV padrão, `cd_cvm` int, tabela `indicadores` no banco, busca só com empresas ativas e com indicadores | `contratos.md`, `raiox/dados.py`, `scripts/indicadores.py` | os mesmos + `tests/test_contratos.py` (C1 e C2, com `falsos/contas_falsas.csv`) | Plan | teste de contrato | `pd.read_csv('data/indicadores.csv')` tem 13 colunas e `cd_cvm` int | PR (Eduardo + Miguel) |
| MA3 | 31/10–01/11 | dados reais + checagem + conferência | `raiox/checagem.py` | `avaliacao/conferencia.csv`; consertos que a checagem pedir | Manual | `python -m raiox.checagem …` (`--com-ia` uma vez, avisando o grupo) | 5 empresas com diferença < 1% do site de RI (confirma o separador decimal); nenhum "erro" sobrando; `data/` v1 no Drive com o link no grupo | PR |
| MA4 | 03–04/11 | EDA | `data/` | `notebooks/eda.ipynb`, `docs/graficos/*.png` | Manual (você escreve; a IA explica) | "Restart & Run All" | sem erro; 4 a 6 gráficos (nulos, distribuições, extremos, cobertura, setores, o que o checador apontou) | PR |
| MA5 | 05–08/11 | BPMN 2.0, hoje e com o Raio-X (bpmn.io) | `docs/entenda-o-projeto.md` | `docs/bpmn/*.bpmn` e `.png` | Plan (o Claude só revisa a notação) | abrir no bpmn.io | raias Vendedor, Sistema e LLM; decisões "tem dados?" e "passou no validador?" | PR |
| MA6 | 12–13/11 | montar o `documentacao.pdf` | BPMN, justificativa, ética, arquitetura | `docs/documentacao.pdf` | fora do Claude | — | PDF com as 3 partes que o guia pede | PR |

### Miguel (Codex hoje; Claude Code se migrar, com as mesmas sessões)

| # | data | objetivo | lê | altera | modo | testes | pronto quando | git |
|---|---|---|---|---|---|---|---|---|
| MG1 | qua 28/10 | entrar no projeto, revisar o PR ED0, configurar o GitHub | `README.md`, `AGENTS.md`, `CLAUDE.md`, `app/` | configurações do GitHub | só leitura ("explique, não altere") | `pytest -q`; `cd app && streamlit run streamlit_app.py` | print da tela no grupo; PR ED0 aprovado; só merge commit; apagar branch após o merge; proteção ligada ou "não disponível" anotado aqui | aprova o PR |
| MG2 | 29–30/10 | `Dockerfile` + `.dockerignore`: tela com falsos, `data/` como volume, chave por variável | `app/`, `requirements.txt` | `Dockerfile`, `.dockerignore` | Plan | `docker build`; `docker run -p 8501:8501 …`; `curl localhost:8501/_stcore/health` → `ok` | os comandos funcionam e estão no README | `miguel-docker` → PR (Eduardo) |
| MG3 | 31/10–01/11 | Terraform (provider docker): imagem, contêiner, porta 8501, volume, `GOOGLE_API_KEY` como `sensitive` | `Dockerfile` | `infra/main.tf`, `infra/variables.tf` | Plan | `terraform apply`; `destroy` e `apply` de novo | a tela sobe; `data/` sobrevive; `git status` sem `tfstate` | PR. **Se não estiver pronto até ter 03/11, fica só o Docker** |
| MG4 | 03–04/11 | tela com dados reais: variável `RAIOX_DADOS` no lugar da constante; volta sozinha para o modo sem IA, com aviso; `registrar_consulta` dentro do `try` | `app/streamlit_app.py`, C1, C3 | `app/streamlit_app.py`, `.env.example`, `tests/test_tela.py` (AppTest com falsos) | Plan | `test_tela` no CI | 3 empresas de setores diferentes geram raio-x dentro do contêiner | PR (Eduardo) |
| MG5 | qui 05/11 | diagrama de arquitetura + README (arquitetura, pré-requisitos com Python 3.14, rodar local, Docker e Terraform) | tudo | `docs/arquitetura.png`, `README.md` | Manual | — | um colega lê o README e entende o fluxo | PR |
| MG6 | sex 06/11 | demo ponta a ponta via `terraform apply`; roteiro de 6 min; vídeo v0 | — | — | — | roteiro com 3 empresas escolhidas e testadas | vídeo salvo em 2 lugares | (o Eduardo cria a tag `v0.1-demo`) |
| MG7 | sex 13/11 | vídeo final na `v1.0` | — | — | — | — | vídeo salvo em 2 lugares | — |

### Náthally (sem IA de código: GitHub pelo navegador)

Como subir um arquivo:
1. No GitHub, "Add file → Upload files".
2. Escolha "Create a new branch" e dê o nome `nathally-tarefa`.
3. Abra o PR. O Eduardo revisa.

| # | data | objetivo | altera | pronto quando | git |
|---|---|---|---|---|---|
| NA1 | 28–29/10 | trazer a `feat/metricas` (20 min com o Eduardo) e escrever as regras v2 alinhadas ao código (ver `seguindo-o-projeto.md`, item 7) | `docs/produto/` (persona, roteiro, glossário, comparação de LLMs, pitch); `avaliacao/regras_prompt.md` | PR aberto | `nathally-produto` → PR (Eduardo) |
| NA2 | 30/10–01/11 | `casos_avaliacao.csv` no formato C4: os 10 casos que já existem, com o `cd_cvm` achado pela busca da tela ou no `indicadores.csv` do Drive | `avaliacao/casos_avaliacao.csv` | todo `cd_cvm` existe no `indicadores.csv` (o Eduardo confere com um comando) | PR |
| NA3 | 03–06/11 | `tempo_manual.csv` (3 empresas), 3 testes com usuários (sem nome), conta do ROI | `avaliacao/tempo_manual.csv`, `avaliacao/testes_usuarios.csv` | 3 testes feitos; ROI com números medidos | PR |
| NA4 | 07–08/11 | `revisao.csv` a partir do `resultados.csv`; métricas; comparação com ChatGPT e Gemini (o caso Camil já existe) | `avaliacao/revisao.csv`, `docs/produto/metricas.md` | % de comparações certas, % de perguntas ligadas ao produto, utilidade, custo, tempo de resposta | PR |
| NA5 | 09–12/11 | texto de governança e ética; deck com o tempo de cada parte | `docs/etica.md`, deck | o Marcos recebe o texto de ética para o PDF; os slides de todos chegaram | PR (o texto) |
| NA6 | 13–15/11 | deck final; 2 ensaios cronometrados | deck | ensaio abaixo de 20 min | — |

---

## 4. Testes

| módulo | unitário | contrato | ponta a ponta | quem escreve | sessão |
|---|---|---|---|---|---|
| limpeza, `carregar_dfp`, `indicadores` | `test_limpeza`, `test_carregar_dfp` (já existem na branch do Marcos) | C2: lido com o pandas padrão → 13 colunas, `cd_cvm` int | ✔ | Marcos | MA1, MA2 |
| `raiox/dados.py` | `test_dados` (já existe) | C1: `cd_cvm` int, só empresas com indicadores | ✔ | Marcos (Miguel revisa) | MA1, MA2 |
| `raiox/segmentos.py` | `test_segmentar_aguenta_receita_zero` | — | ✔ | Eduardo | ED2 |
| `raiox/ia.py` | 5 testes do validador | C3 com os falsos, sem depender de `data/` | ✔ | Eduardo | ED2 |
| `avaliacao/avaliar.py` | `test_avaliar` | C4: colunas do `resultados.csv`; todo `cd_cvm` dos casos existe (pulado sem dados reais) | — | Eduardo | ED5 |
| tela | `test_tela` (AppTest com falsos) | usa só C1 e C3 | ✔ | Miguel | MG4 |
| Docker e Terraform | — | — | `curl …/_stcore/health` + roteiro da demo | Miguel | MG2, MG3 |
| sistema inteiro | — | — | `test_ponta_a_ponta.py` com dados reais (só local) | Eduardo | ED6 |

- **Quando rodam:**
  - na sua máquina, antes de todo commit;
  - no CI, em todo PR e em todo push na `main`;
  - o teste ponta a ponta, antes das tags `v0.1-demo` e `v1.0` e no teste do zero.
- **Nenhum teste chama a API do Gemini.** Antes de cada demo, uma chamada real feita à mão.
- **Nada entra com teste falhando:**
  - o CI roda no PR, e quem revisa não aprova com CI vermelho (está no modelo de PR);
  - se o GitHub permitir proteção da `main`, o check `testes` vira obrigatório.

---

## 5. Pontos de integração

| data | quem | o que sincroniza | o que congela |
|---|---|---|---|
| ter 27/10 | Eduardo ↔ Marcos | formato do C2 (PR ED0) | formato e tipos do C2 |
| qua 28/10 | Eduardo → Náthally | 3 raio-x reais | — |
| qui 29/10 | Miguel → todos | PR ED0 na `main`; todos criam as próximas branches a partir dela | arquivos de padronização |
| sex 30/10 | Náthally → Eduardo | regras v2 | texto das regras (até ED3) |
| dom 01/11 | Marcos → todos | `data/` v1 no Drive; `indicadores.csv` real | colunas do C2 |
| dom 01/11 | Náthally → Eduardo | casos no formato C4 | formato do C4 |
| ter 03/11 | os 4 | C1, C3 e variáveis de ambiente da tela e do Docker | **interfaces**: só mudam com os 4 de acordo |
| sex 06/11 | os 4 | demo ponta a ponta; tag `v0.1-demo` | escopo: nada novo depois daqui |
| ter 10/11 | os 4 | tag `v1.0` | código |
| qua 11/11 | Eduardo + Náthally | teste do zero | README |
| qui 12/11 | todos → Náthally | conteúdo dos slides | roteiro |

**Como os dados chegam a cada um:**
- O Marcos publica um zip da pasta `data/` no Drive em dom 01/11 e ter 10/11. Esse é o caminho oficial.
- Os scripts continuam reproduzíveis, para o teste do zero e para a banca.
- **Por que não "cada um roda os scripts":** baixar 3 anos da CVM em cada máquina multiplica os pontos de falha e pode deixar cada pessoa com dados diferentes.
- **Por que não pôr no Git:** quebraria a regra 5 do CLAUDE.md e o REGRAS-IA §2.

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
| D5 20 minutos | NA6 + ensaios de 14–15/11 |

---

## 7. Riscos e plano B

| marco | risco | plano B |
|---|---|---|
| qua 28/10 | o `carregar_dfp.py` não roda na máquina do Eduardo, ou a CVM está lenta | 3 raio-x com a tabela falsa + 1 empresa real calculada à mão; as regras v2 dependem do formato, não dos números |
| dom 01/11 | o `indicadores.csv` real não sai | o Eduardo assume os indicadores; o Marcos vai para SQL, EDA e BPMN |
| dom 01/11 | o Terraform não sobe | prazo final ter 03/11; depois disso, fica só o Docker (o guia aceita "Terraform ou conteinerização") |
| ter 03/11 | algum módulo não passa no "pronto quando" | voltar ao mínimo; a tela usa os falsos; nada de extra |
| sex 06/11 | a demo não roda inteira | seg e ter 09–10/11 só para isso; o vídeo vira obrigatório; demo por `docker run` ou `streamlit run` local |
| dia da banca | a API falha ou o crédito acaba (erro 402) | a tela volta sozinha para o modo sem IA, com aviso (MG4); vídeo; saldo conferido em 12/11 |
| qualquer dia | a banca é **antes** (semana de 09–15/11) | `v1.0` = `v0.1-demo` com consertos; cortar Terraform, PCA, BPMN "hoje" e casos de 20 para 10; PDF e deck até 48 h antes |
| qualquer dia | a banca é **depois** | nada novo; o tempo vai para ensaio e teste do zero |
| qualquer dia | alguém fica indisponível | duplas de reserva: Marcos ↔ Eduardo (dados), Miguel ↔ Eduardo (infra), Náthally ↔ Marcos (deck e PDF); os falsos deixam seguir sem a peça |
| qualquer dia | conflito em arquivo comum | um PR por vez em arquivo comum, avisando no grupo |

**O que cortar.** Com 6 a 12 h por semana por pessoa, sobram de 12 a 24 h até 10/11.

**Fora já:**
- `verificar_automatico.py` (yfinance) e `graficos.py` da branch do Marcos;
- gráfico de receita em 3 anos;
- filtro "parecidas do mesmo setor";
- RAG, nome dos grupos pelo LLM, exportar o raio-x, número de empregados;
- refatorar as duplicações (são risco baixo).

**Se faltar tempo, cortar nesta ordem:**
1. Terraform (fica só o Docker)
2. casos de 20 para 10
3. BPMN "hoje" (fica só o "com o Raio-X")
4. gráfico PCA
5. testes com usuários de 5 para 3

---

## 8. Sessões do Eduardo: o que ele escreve à mão e o que a IA só explica

| escreve à mão (a IA revisa) | a IA escreve; ele lê e explica de volta | a IA só explica (sem código) |
|---|---|---|
| a correção do teste do C3 (ED2) | YAML do CI, `pytest.ini`, modelo de PR (ED0) | K-means, silhueta, `StandardScaler`, `NearestNeighbors` (ED4) |
| o gráfico PCA, cerca de 10 linhas (ED4) | versões do `requirements.txt` (ED0) | `with_structured_output`, Pydantic, `include_raw` (ED3) |
| o laço do `avaliar.py`: ler CSV, chamar `preparar_raio_x`, gravar (ED5) | esqueleto do teste ponta a ponta (ED6) | por que o validador garante a regra de ouro (`validar_e_preencher()`) |
| justificativa técnica e "Como usamos IA" (ED8) | consertos do congelamento (ED9) | perguntas da banca (ED11) |
| mudanças de texto no `contratos.md` | — | — |

**Método:** ler o trecho → prever o resultado → rodar → só então pedir "explique". Se ele não consegue explicar uma linha, ela não entra.

---

## Se começássemos do zero (para aprender, não para refazer)

1. **Dia 1: matriz do guia, com dono e evidência para cada requisito.** Nada de código antes disso.
2. **Contratos com o formato do arquivo** (separador, decimal, tipos) e **falsos** no mesmo formato. Os dois maiores bugs de hoje (CSV com `;` e `cd_cvm` como texto) são de contrato, não de código.
3. **Um repositório-esqueleto, feito por uma pessoa, de onde todos clonam.** Ele já traz:
   - pastas e README;
   - CLAUDE.md, AGENTS.md e REGRAS-IA.md;
   - versões fixas e config do pytest;
   - CI e modelo de PR;
   - proteção da `main`.

   Assim não existiriam duas branches sem história em comum.
4. **Docker "olá mundo" na primeira semana.** Infra é o que quebra no fim; começar cedo mostra os problemas de versão do Python e de caminhos.
5. **Cada um trabalha contra os falsos:**
   - Marcos: limpeza com testes → C2 → SQL e C1;
   - Eduardo: ML e IA → avaliação;
   - Miguel: tela no contêiner → Terraform;
   - Náthally: persona e tempo manual → regras → casos → testes com usuários.
6. **Integração toda semana, com tag**; depois congelar e documentar.
