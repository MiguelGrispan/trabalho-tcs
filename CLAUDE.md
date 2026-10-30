# Raio-X Comercial · contexto para o Claude Code

Projeto final da trilha IA Aplicada (SENAI/TCS). Equipe: Marcos (dados), Eduardo (IA e gestão),
Náthally (produto e métricas, deck), Miguel (tela e infraestrutura). Banca prevista para qua 18/11/2026
(**data e horário a confirmar**; professores + especialistas da TCS). Os entregáveis vão **48 h antes**: seg 16/11.

## Fonte da verdade: os arquivos do professor (leia antes de tudo)
O que o projeto precisa ter vem de dois arquivos do professor (André Santos, repositório do curso), guardados sem mudança em `docs/professor/`:
1. `docs/professor/requisitos_projeto.MD` (29/10/2026): o que deve ser entregue (documentação, ML ou IA de terceiro, aplicação com Terraform);
2. `docs/professor/guia_projeto_final.pdf` (07/10/2026, 10 páginas): requisitos técnicos mínimos, apresentação de 20 min, pesos da banca e entregáveis.

Mais as regras ditas em aula, anotadas em `docs/REQUISITOS.md` ("Regras do professor"), como o PostgreSQL.

**Em toda sessão, antes de qualquer tarefa, leia os dois arquivos inteiros** (o PDF com a ferramenta Read). Eles valem mais que este
arquivo, o PLANO e o REQUISITOS. Quando os dois diferem, vale o mais exigente: o guia diz "Terraform ou conteinerização", mas o
`requisitos_projeto.MD` exige "Infraestrutura automatizada com Terraform", então **o Terraform é obrigatório**.

**Contra alucinação (vale para o Claude Code e para quem lê):**
- Nunca diga que algo exigido nesses arquivos é opcional, extra, "já coberto por outra coisa" ou que pode ser cortado.
  Toda afirmação sobre o que o professor exige vem com o arquivo e o item (ex.: "`requisitos_projeto.MD`, Aplicação: Terraform").
- Se uma nota (PLANO, REQUISITOS, guias de `aprender/`) contradiz os arquivos do professor, a nota está errada: avise a pessoa e corrija a nota.
- Se o arquivo do professor não é claro (ex.: se o Streamlit conta como "Backend e Frontend"), diga que não sabe e anote a pergunta
  em `docs/REQUISITOS.md` para o Eduardo levar ao professor. Não decida sozinho.
- Cortar escopo (PLANO, seção 7) só vale para o que **não** está nos arquivos do professor.

**Depois,** leia o `docs/PLANO.md` (seção 0: o que está acontecendo agora; seção 3: a sessão da pessoa, ex.: "MA2"; seção 7: o que
foi cortado) e o `docs/REQUISITOS.md` (cada requisito do professor, onde está no projeto e o status).
O passado, resumido: `docs/HISTORICO.md`. Guias para iniciantes: `aprender/` (comece por `aprender/claude-code.md`).
**Sessão nova:** `/inicio-de-sessao` (ex.: `/inicio-de-sessao MA2`) atualiza a `main`, cria a branch, lê os arquivos do professor e
confere o estado real no GitHub, porque a nota da seção 0 pode estar velha. **Fim:** `/fim-de-sessao`.

## O produto
O vendedor escolhe uma companhia aberta da CVM, informa o produto e o objetivo da reunião e recebe:
6 indicadores com fonte (DFP), posição contra o grupo de empresas parecidas (K-means), 3 a 5 perguntas
ligadas ao produto, lacunas e 5 empresas parecidas para prospectar (vizinhos mais próximos).

## Regra de ouro
O LLM (Gemini via LangChain) nunca escreve números. Ele usa marcadores como {margem_ebit};
o validador remove qualquer dígito fora de marcador; o código troca os marcadores pelos valores da tabela.
Não quebre essa regra em nenhuma mudança.

## O que o professor exige (e onde fica no projeto)
Todo trabalho precisa servir a um destes itens. Se uma tarefa não serve a nenhum, pergunte antes de fazer.
Fonte: **G** = `guia_projeto_final.pdf` (seção) · **R** = `requisitos_projeto.MD` (seção) · **A** = regra dita em aula (`docs/REQUISITOS.md`).
O status de cada item, com a prova, fica no `docs/REQUISITOS.md`.

| Requisito | Fonte | Onde fica | Dono |
|---|---|---|---|
| BPMN 2.0 do processo da regra de negócio da aplicação | G §2; R Documentação | `docs/bpmn/` (`.bpmn` + `.png`) | Marcos |
| Python/Pandas: limpeza, nulos, estruturação de uma base pública | G §2; R Machine Learning | `scripts/carregar_dfp.py`, `scripts/indicadores.py`, `raiox/limpeza.py` | Marcos |
| SQL (consultas ou persistência) e banco de dados da aplicação, **em PostgreSQL** | G §2; R Aplicação; A (29/10: SQLite não vale) | `raiox/banco.py`, `raiox/dados.py`, `scripts/carregar_dfp.py`; endereço em `DATABASE_URL`, no `.env` | Marcos |
| Visualização explicativa (Matplotlib/Seaborn ou dashboard) | G §2 | `notebooks/`, `docs/graficos/`, gráfico da tela | Marcos, Eduardo |
| ML treinado com os dados limpos e usado na aplicação | G §2; R Machine Learning | `raiox/segmentos.py` (K-means + vizinhos) | Eduardo |
| GenAI: prompt engineering, LangChain, API, com uma base de conhecimento para a IA usar | G §2; R Integração com IA de terceiro | `raiox/ia.py` (+ auditoria em `raiox/checagem.py`); a base são os dados da CVM | Eduardo |
| Aplicação web com **backend e frontend** e interface funcional | R Aplicação; G §2 | `app/streamlit_app.py` (tela), `raiox/` (o que roda por trás) | Miguel |
| **Infraestrutura automatizada com Terraform** (local ou nuvem): obrigatória | R Aplicação; G §2 e §6 | `infra/` (Terraform, MG3), `Dockerfile`, `docker-compose.yml` | Miguel |
| Arquivos de prompts usados no vibecoding | R Aplicação | `CLAUDE.md`, `AGENTS.md`, `REGRAS-IA.md`, `.claude/skills/`, `.github/pull_request_template.md` | todos (coordena Eduardo) |
| Boas práticas e agentic coding | G §2 | `tests/`, `contratos.md`, CI, pull requests | todos |
| Governança e ética (viabilidade, limites, viés, confiabilidade, uso responsável) | G §2 | validador, texto de ética no PDF | Náthally, todos |

**Regras do professor ditas em aula** (valem como os arquivos; ficam em `docs/REQUISITOS.md`, seção "Regras do professor"):
- **O banco é PostgreSQL. SQLite não vale** (29/10). O `requisitos_projeto.MD` diz "banco de dados à sua escolha", mas em aula o
  professor fixou o PostgreSQL: vale o PostgreSQL. Nada novo com `sqlite3`; desde a MA2 (PRs #21 e #22) a `main` usa só o PostgreSQL.
  O endereço do banco (`DATABASE_URL`) tem senha: fica no `.env`, como a chave do Gemini.

**Entregáveis (48 h antes da banca; G §6 e R "Composição do projeto"):**
(1) repositório Git organizado, com README em markdown sobre o tema, o objetivo e as tecnologias, com a arquitetura, os pré-requisitos
e as instruções para rodar; os scripts de infraestrutura (Terraform), os notebooks e os arquivos de prompts do vibecoding;
(2) documento (PDF, ou markdown) com as etapas desenvolvidas no processo (R), o BPMN 2.0, a justificativa técnica das escolhas
(ex.: RAG × fine-tuning) e a análise de ética e segurança (G); (3) slides (deck em PDF ou PPTX) para no máximo 20 minutos.
Também: vídeo gravado da demo, como reserva (dica do G §3).

**Apresentação (20 min, tempo é avaliado; G §3):** contexto e problema 3 · BPMN e arquitetura 3 · demo ao vivo 6 ·
detalhe técnico (dados, ML/GenAI e infraestrutura com Terraform) 4 · governança e ética 2 · conclusão 2.
**Pesos da banca (G §5):** inovação e valor de negócio (ROI) 20% · qualidade técnica e arquitetura 30% (inclui "estrutura de
DevOps/Terraform") · protótipo funcional 20% · governança e ética 15% · comunicação e equipe 15%.

## Estrutura e donos

| caminho | dono |
|---|---|
| `raiox/ia.py`, `raiox/segmentos.py`, `avaliacao/avaliar.py`, `avaliacao/resultados.csv` | Eduardo |
| `scripts/`, `raiox/dados.py`, `raiox/checagem.py`, `docs/bpmn/`, `notebooks/` | Marcos |
| `app/`, `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `infra/` | Miguel |
| o resto de `avaliacao/` (regras do prompt, casos e planilhas do C4), `docs/produto/` | Náthally |
| `docs/professor/` | ninguém edita: são cópias dos arquivos do professor. Se ele publicar versão nova, troque o arquivo inteiro, avise o grupo e revise o CLAUDE.md e o REQUISITOS |

Pastas comuns (avise o grupo antes de mexer): `tests/`, `falsos/` (dados falsos no formato dos contratos;
os falsos chamam o código real sem IA), `docs/`, `aprender/` (guias e atalhos do Mac; nada ali é usado pelo código), `contratos.md`, `README.md`.
`data/`: dados da CVM e arquivos gerados; só o `.gitkeep` vai para o Git.
Caminhos: todo código que usa `data/` ou `docs/` aponta para a **raiz** do repositório (`Path(__file__).resolve().parent.parent`).

## Regras
1. **Não mexa em pasta de outro dono.** Precisa de mudança lá? Peça ao dono ou combine antes no grupo.
2. **Contrato antes de código.** Mudou um formato entre partes? Primeiro o `contratos.md`, avisando quem recebe; depois o código.
3. **Testes antes de dizer "pronto".** Rode `python -m pytest -q` e mostre o resultado. Mudou a tela? Abra a tela também.
   Toda mudança de comportamento vem com teste novo ou atualizado no mesmo PR (lista dos testes: `docs/PLANO.md`, seção 4).
4. **O LLM nunca escreve números** (regra de ouro). Acima/abaixo/em linha é calculado por código.
5. **Nada de dados nem `.env` no Git.** Antes de todo commit, rode `git status` e leia a lista.
6. **A demo não pode quebrar.** O modo sem IA (sem `RAIOX_IA_REAL`) é o plano B: precisa continuar funcionando.
7. **`main` só por pull request, com o CI verde.** Revisam o CI (os testes) e o Claude Code, que lê o diff no `/fim-de-sessao`;
   o autor faz o merge depois de um "pode". Uma pessoa só dá o ok (no grupo, não no GitHub) quando o PR mexe no
   `contratos.md` ou na pasta dela. No PR, 2 linhas: o que foi feito com IA e o que o autor entendeu ou conferiu
   (vale "ainda não li": o que não vale é inventar).
8. **Git: o Claude Code faz.** O `/inicio-de-sessao` cria a branch `pessoa-tarefa` a partir da `main`. O `/fim-de-sessao` roda os
   testes, atualiza a seção 0 do `docs/PLANO.md` (é por ela que a próxima sessão começa), o `docs/REQUISITOS.md` e o
   `docs/HISTORICO.md`, abre o PR, espera o CI e faz o merge. Para trazer a `main`, `git merge main`.
   Nunca `rebase`, `push --force` nem commit na `main`.

## Como responder ao time (iniciantes)
- Português simples. Explique o porquê de cada mudança, não só o quê.
- Toda afirmação sobre o código vem com a prova: arquivo e linha, ou um comando que a pessoa roda e vê o mesmo resultado.
- Separe "verifiquei" de "estou supondo". Se não abriu o arquivo, diga.
- Passos pequenos, um commit por passo.

## Como rodar (sempre a partir da raiz do repositório)
Lista completa, com o que deve aparecer: `aprender/COMANDOS.md`.
- Ambiente: `python -m venv .venv` e `pip install -r requirements.txt`. No Mac do Eduardo, sem `.venv`, use `~/bootcamp/bin/python`.
- Testes: `python -m pytest -q` (não chamam a API).
- Módulos: `python -m raiox.ia ... --sem-ia`, `python -m raiox.segmentos`, `python -m raiox.checagem --teste`.
- Tela: `cd app && streamlit run streamlit_app.py`. `RAIOX_IA_REAL=1` liga o Gemini. Até o `raiox/dados.py` ficar pronto, a tela usa `falsos/`.
- Docker (tela + PostgreSQL): `docker compose up -d --build` (tela em `http://localhost:8501`), `docker compose ps` (os 2 `healthy`),
  testes no contêiner com `docker compose run --rm tela python -m pytest -q`, e `docker compose down` para desligar.
  Os outros comandos estão no topo do `docker-compose.yml`.

## Cuidados
- Siga o `REGRAS-IA.md` (regras do time para uso de IA).
- Não leia, mostre nem envie o conteúdo de `.env` (chave do Gemini, plano pré-pago).
- Toda chamada ao Gemini gasta crédito (≈ US$ 0,0012 por raio-x). Mais de 10 chamadas: avise o grupo antes.
