# Raio-X Comercial · contexto para o Claude Code

Projeto final da trilha IA Aplicada (SENAI/TCS). Equipe: Marcos (dados), Eduardo (IA e gestão),
Náthally (produto e métricas, deck), Miguel (tela e infraestrutura). Banca prevista para qua 18/11/2026
(**data e horário a confirmar**; professores + especialistas da TCS). Os entregáveis vão **48 h antes**: seg 16/11.

Antes de qualquer tarefa, leia `docs/PLANO.md` (sessões, datas e donos; a pessoa diz qual sessão está fazendo, ex.: "MA2")
e `docs/REQUISITOS.md` (o que o guia exige e o status). O que está quebrado, com prova: `aprender/seguindo-o-projeto.md`.
Material para quem está aprendendo (comandos, guias, notebook passo a passo, atalhos): `aprender/`; como usar o Claude Code no time: `aprender/claude-code.md`. Quem usa Codex: o `AGENTS.md` aponta para este arquivo.
**Sessão nova?** Comece pela seção 0 do `docs/PLANO.md` (situação atual). Depois confira o estado real com
`gh pr list --state all` e `git log --oneline -15`, porque a nota pode estar velha.

## O produto
O vendedor escolhe uma companhia aberta da CVM, informa o produto e o objetivo da reunião e recebe:
6 indicadores com fonte (DFP), posição contra o grupo de empresas parecidas (K-means), 3 a 5 perguntas
ligadas ao produto, lacunas e 5 empresas parecidas para prospectar (vizinhos mais próximos).

## Regra de ouro
O LLM (Gemini via LangChain) nunca escreve números. Ele usa marcadores como {margem_ebit};
o validador remove qualquer dígito fora de marcador; o código troca os marcadores pelos valores da tabela.
Não quebre essa regra em nenhuma mudança.

## O que o guia oficial exige (e onde fica no projeto)
Todo trabalho precisa servir a um destes itens. Se uma tarefa não serve a nenhum, pergunte antes de fazer.

| Requisito do guia | Onde fica | Dono |
|---|---|---|
| BPMN 2.0 do processo | `docs/bpmn/` (`.bpmn` + `.png`) | Marcos |
| Python/Pandas: limpeza, nulos, estruturação | `scripts/carregar_dfp.py`, `scripts/indicadores.py` | Marcos |
| SQL (consultas ou persistência) | `data/catalogo.db` via `scripts/carregar_dfp.py` e `raiox/dados.py` | Marcos |
| Visualização explicativa (Matplotlib/Seaborn ou dashboard) | `notebooks/`, `docs/graficos/`, gráfico da tela | Marcos, Eduardo |
| Modelo de ML | `raiox/segmentos.py` (K-means + vizinhos) | Eduardo |
| GenAI: prompt engineering, LangChain, API | `raiox/ia.py` (+ auditoria em `raiox/checagem.py`) | Eduardo |
| Interface funcional | `app/streamlit_app.py` | Miguel |
| Boas práticas e agentic coding | `tests/`, `contratos.md`, `REGRAS-IA.md`, este arquivo, pull requests | todos |
| Arquitetura + Terraform ou contêiner | `Dockerfile`, `infra/` | Miguel |
| Governança e ética (viabilidade, limites, viés, confiabilidade, uso responsável) | validador, texto de ética no PDF | Náthally, todos |

**Entregáveis (48 h antes):** (1) repositório organizado, com README de arquitetura, pré-requisitos e como rodar,
e os scripts de infraestrutura e notebooks; (2) PDF com BPMN 2.0, justificativa técnica (inclui por que não
RAG nem fine-tuning) e análise de ética e segurança; (3) deck em PDF ou PPTX. Também: vídeo gravado da demo (plano B).

**Apresentação (20 min, tempo é avaliado):** contexto e problema 3 · BPMN e arquitetura 3 · demo ao vivo 6 ·
detalhe técnico 4 · governança e ética 2 · conclusão 2.
**Pesos da banca:** inovação e valor de negócio (ROI) 20% · qualidade técnica e arquitetura 30% ·
protótipo funcional 20% · governança e ética 15% · comunicação e equipe 15%.

## Estrutura e donos

| caminho | dono |
|---|---|
| `raiox/ia.py`, `raiox/segmentos.py`, `avaliacao/avaliar.py` | Eduardo |
| `scripts/`, `raiox/dados.py`, `raiox/checagem.py`, `docs/bpmn/`, `notebooks/` | Marcos |
| `app/`, `Dockerfile`, `infra/` | Miguel |
| `avaliacao/*.csv`, `avaliacao/regras_prompt.md`, `docs/produto/` | Náthally |

Pastas comuns (avise o grupo antes de mexer): `tests/`, `falsos/` (dados falsos no formato dos contratos;
os falsos chamam o código real sem IA), `docs/`, `aprender/` (guias e atalhos `.command` do Mac; nada ali é usado pelo código), `contratos.md`, `README.md`.
`data/`: dados da CVM e arquivos gerados; só o `.gitkeep` vai para o Git.
Caminhos: todo código que usa `data/` ou `docs/` aponta para a **raiz** do repositório (`Path(__file__).resolve().parent.parent`).

## Regras
1. **Não mexa em pasta de outro dono.** Precisa de mudança lá? Peça ao dono ou combine antes no grupo.
2. **Contrato antes de código.** Mudou um formato entre partes? Primeiro o `contratos.md`, avisando quem recebe; depois o código.
3. **Testes antes de dizer "pronto".** Rode `python -m pytest -q` e mostre o resultado. Mudou a tela? Abra a tela também.
   Toda mudança de comportamento vem com teste novo ou atualizado no mesmo PR (lista dos testes: `docs/PLANO.md`, seção 4).
   Ao terminar uma sessão, atualize a seção 0 do `docs/PLANO.md` (situação atual): é por ela que a próxima sessão começa.
   Atalho: `/fim-de-sessao`. Para aprender a explicar um trecho do código: `/explicar`.
4. **O LLM nunca escreve números** (regra de ouro). Acima/abaixo/em linha é calculado por código.
5. **Nada de dados nem `.env` no Git.** Antes de todo commit, rode `git status` e leia a lista.
6. **A demo não pode quebrar.** O modo sem IA (sem `RAIOX_IA_REAL`) é o plano B: precisa continuar funcionando.
7. **`main` só por pull request**, com o CI verde e 1 pessoa revisando. No PR, 2 linhas: o que foi feito com IA e o que você conferiu.
8. **Git:** uma branch curta por sessão, a partir da `main` atualizada, com nome `pessoa-tarefa` (ex.: `marcos-porta-dados`).
   Para trazer a `main`, use `git merge main`. Nunca `rebase`, `push --force` nem commit direto na `main`.

## Como responder ao time (iniciantes)
- Português simples. Explique o porquê de cada mudança, não só o quê.
- Toda afirmação sobre o código vem com a prova: arquivo e linha, ou um comando que a pessoa roda e vê o mesmo resultado.
- Separe "verifiquei" de "estou supondo". Se não abriu o arquivo, diga.
- Passos pequenos, um commit por passo.

## Como rodar (sempre a partir da raiz do repositório)
Lista completa, com o que deve aparecer: `aprender/COMANDOS.md`.
- Ambiente: `python -m venv .venv` e `pip install -r requirements.txt`. No Mac do Eduardo, os atalhos usam `~/bootcamp` se a `.venv` não existir.
- Testes: `python -m pytest -q` (não chamam a API).
- Módulos: `python -m raiox.ia ... --sem-ia`, `python -m raiox.segmentos`, `python -m raiox.checagem --teste`.
- Tela: `cd app && streamlit run streamlit_app.py`. `RAIOX_IA_REAL=1` liga o Gemini. Até o `raiox/dados.py` ficar pronto, a tela usa `falsos/`.

## Cuidados
- Siga o `REGRAS-IA.md` (regras do time para uso de IA).
- Não leia, mostre nem envie o conteúdo de `.env` (chave do Gemini, plano pré-pago).
- Toda chamada ao Gemini gasta crédito (≈ US$ 0,0008 por raio-x). Mais de 10 chamadas: avise o grupo antes.
