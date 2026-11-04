# Raio-X Comercial

Ferramenta para vendedores B2B prepararem a primeira reunião com uma companhia aberta.
O vendedor escolhe a empresa, diz o que vende e o objetivo da reunião, e recebe:

- 6 indicadores das demonstrações entregues à CVM (DFP), cada um com a fonte;
- a posição de cada indicador contra o grupo de empresas de perfil parecido (K-means);
- 3 a 5 perguntas para a reunião, ligadas ao produto, e o que os números não mostram;
- 5 empresas parecidas para prospectar (vizinhos mais próximos).

O texto é escrito por um LLM (Gemini via LangChain) que **nunca escreve números**: ele usa marcadores
como `{margem_ebit}`, um validador remove qualquer dígito fora de marcador e o código troca os marcadores pelos valores da tabela.

Projeto final da trilha IA Aplicada (SENAI/TCS) · Marcos, Eduardo, Náthally e Miguel.
O que o projeto precisa ter vem dos arquivos do professor, em [docs/professor/](docs/professor/)
(`requisitos_projeto.MD` e `guia_projeto_final.pdf`); o status de cada requisito está em [docs/REQUISITOS.md](docs/REQUISITOS.md).

## Tecnologias

| parte | tecnologia (versão fixa no `requirements.txt`) |
|---|---|
| linguagem | Python 3.14 |
| dados: limpeza, nulos, indicadores | Pandas 3.0, NumPy 2.5; dados públicos da CVM (DFP 2023–2025), baixados com `requests` |
| banco de dados | PostgreSQL 17, com SQLAlchemy 2.1 e psycopg 3.3 |
| machine learning | scikit-learn 1.9: K-means (grupos de empresas parecidas) e NearestNeighbors (5 parecidas) |
| IA generativa | Gemini (`gemini-3.1-flash-lite`) pela API, com LangChain (`langchain-core`, `langchain-google-genai`) e saída estruturada com Pydantic |
| tela (aplicação web) | Streamlit 1.66 |
| gráficos | Matplotlib 3.11 |
| infraestrutura | Docker e Docker Compose (tela + PostgreSQL); Terraform 1.17 com o provider Docker (`kreuzwerker/docker` 4.6), em `infra/` |
| testes e CI | pytest 9.1, GitHub Actions (com um PostgreSQL só para os testes) |
| programação com IA (vibecoding) | Claude Code e Codex, guiados pelos arquivos de prompts listados abaixo |

## Prompts usados no vibecoding

Os arquivos que dizem às IAs de programação como trabalhar neste projeto:

| arquivo | para quê |
|---|---|
| [CLAUDE.md](CLAUDE.md) | contexto, requisitos do professor, donos e regras; o Claude Code lê em toda sessão |
| [AGENTS.md](AGENTS.md) | o mesmo, para o Codex |
| [REGRAS-IA.md](REGRAS-IA.md) | o que nunca vai para uma IA, como pedir e como conferir o que ela fez |
| [.claude/skills/](.claude/skills/) | `/inicio-de-sessao`, `/fim-de-sessao` e `/explicar`: os passos que o Claude Code segue |
| [.claude/settings.json](.claude/settings.json) e [.claude/hooks/guarda.py](.claude/hooks/guarda.py) | as travas: o que o Claude Code nunca faz (ler o `.env`, apagar trabalho no Git, commit com dado), o que ele pergunta antes (merge, Gemini, pasta de outro dono) e os testes no fim de cada resposta |
| [.claude/agents/revisor.md](.claude/agents/revisor.md) | o revisor: um segundo Claude, que só lê e revisa o PR sem ter escrito o código |
| [.githooks/pre-commit](.githooks/pre-commit) | a conferência do commit pelo próprio Git (ligue com `git config core.hooksPath .githooks`): vale também fora do Claude Code |
| [.github/pull_request_template.md](.github/pull_request_template.md) | em todo PR: o que foi feito com IA e o que o autor conferiu |

O prompt do produto (o que o Gemini recebe para escrever o raio-x) é outro: [avaliacao/regras_prompt.md](avaliacao/regras_prompt.md).

**Vai programar com o Claude Code?** Comece pelo [aprender/claude-code.md](aprender/claude-code.md): `/inicio-de-sessao`, `/fim-de-sessao`, os modos e os limites.

**Começando agora?** Abra a pasta [aprender/](aprender/README.md): comandos (o que rodar, em qual pasta), o projeto
explicado para iniciantes e um notebook que segue uma empresa do começo ao fim. O plano e o que falta: [docs/PLANO.md](docs/PLANO.md).

## Como usamos IA para programar

O time é iniciante: três pessoas programam com o Claude Code (o Miguel começou com o Codex) e a Náthally não usa IA
para código. A IA escreve muito do código; **quem responde por ele é a pessoa**. Para isso valer, todo trabalho segue o mesmo caminho:

1. **Começo:** `/inicio-de-sessao` cria uma branch a partir da `main` e faz a IA ler os arquivos do professor e o estado do projeto
   (`docs/PLANO.md`, seção 0) antes de mexer em qualquer coisa.
2. **Durante:** a IA segue o [CLAUDE.md](CLAUDE.md) (donos de cada pasta, regra de ouro, contratos) e o [REGRAS-IA.md](REGRAS-IA.md)
   (o que nunca vai para uma IA: chave, senha, dados pessoais). Toda afirmação sobre o código vem com arquivo e linha, ou com um comando que prova.
3. **Fim:** `/fim-de-sessao` roda os testes, atualiza o PLANO, o REQUISITOS e o HISTORICO e abre o PR. O CI roda os testes de novo, e o merge
   só acontece depois de um "pode" da pessoa.
4. **No PR, duas linhas obrigatórias** ([modelo](.github/pull_request_template.md)): o que foi feito com IA e o que o autor entendeu ou conferiu.
   Vale escrever "ainda não li"; o que não vale é inventar.
5. **Na banca, cada um defende o seu código sem consulta:** a skill `/explicar` treina isso (ler, prever, rodar, explicar).

O que aprendemos: a IA erra com confiança. Um exemplo é a silhueta de 0,77, que parecia ótima e escondia grupos inúteis (ED4).
Por isso, nada entra na `main` sem teste, e a IA do produto (o Gemini) nunca escreve números: a justificativa está em
[docs/justificativa.md](docs/justificativa.md).

## Fluxo

```
CVM (ZIPs da DFP 2023–2025 + cadastro)
   │  scripts/carregar_dfp.py      limpa contas, prefere consolidado      → data/contas.csv, PostgreSQL (contas, empresas)
   ▼
scripts/indicadores.py             6 indicadores por empresa (C2)        → data/indicadores.csv, PostgreSQL (indicadores)
   │
   ▼
raiox/checagem.py                  regras de sanidade; IA só aponta suspeitas, pessoa decide
   │
   ▼
raiox/segmentos.py                 K-means + 5 vizinhos                   → data/segmentos.csv, docs/graficos/silhueta.png
   │
   ▼
raiox/ia.py                        preparar_raio_x() (C3): números por código, texto pelo LLM com marcadores, validador
   │
   ▼
app/streamlit_app.py               tela: busca a empresa (raiox/dados.py, C1), mostra o raio-x, registra a consulta
```

Os formatos entre as partes (C1 a C4) estão em [contratos.md](contratos.md).

## Pastas

```
raiox/          código do produto: ia.py, segmentos.py (Eduardo) · dados.py, checagem.py (Marcos)
app/            tela Streamlit e tema (.streamlit/config.toml) · Miguel
scripts/        preparação dos dados da CVM: verificar_dfp, carregar_dfp, indicadores · Marcos
avaliacao/      avaliação do raio-x (contrato C4) · Náthally e Eduardo
tests/          testes automáticos (não chamam a API)
falsos/         dados e módulos falsos no formato dos contratos, para ninguém esperar ninguém
docs/           arquivos do professor (docs/professor/), plano, requisitos, gráficos (docs/graficos/) e documentos da entrega
infra/          implantação: o Terraform (*.tf: sobe a tela e o banco) e o script do banco de testes (infra/banco/) · Miguel
aprender/       só para quem está aprendendo: comandos, guias, notebook passo a passo, atalhos do Mac
data/           dados da CVM e arquivos gerados: fica só no seu computador, não vai para o Git
```

Na raiz: `contratos.md`, `REGRAS-IA.md` (regras do time para uso de IA), `CLAUDE.md` (contexto e donos de cada pasta),
`requirements.txt`, `.env.example`, e o `Dockerfile` e o `docker-compose.yml` (o contêiner).

## Como rodar com Docker (o caminho mais curto)

Pré-requisito: Docker com o Compose (`docker compose version`). Não precisa instalar Python nem PostgreSQL. Na raiz do repositório:

```bash
docker compose up -d --build        # sobe a tela e o PostgreSQL (a 1ª vez demora uns 5 min) → http://localhost:8501
docker compose ps                   # os 2 (banco e tela) devem aparecer como "healthy"
docker compose run --rm tela python -m pytest -q    # os testes dentro do contêiner, com o banco de testes
docker compose down                 # desliga os 2; o banco continua guardado no volume
```

- **Dados da CVM no banco do contêiner:** `docker compose run --rm --user "$(id -u):$(id -g)" tela python scripts/carregar_dfp.py`
  e o mesmo com `scripts/indicadores.py` (no Linux, o `--user` deixa o contêiner gravar na sua `data/`; no Mac não precisa).
  Abriu a tela antes de carregar? Depois da carga, `docker compose restart tela` (até o conserto da issue #43).
- **IA ligada:** `RAIOX_IA_REAL=1 docker compose up -d`. A chave vem do `GOOGLE_API_KEY` do `.env`, que o Compose lê sozinho.
  A chave e a `data/` nunca entram na imagem (`.dockerignore`): a `data/` entra como volume.
- **Porta 5432 ocupada** por outro PostgreSQL: `PORTA_BANCO=5433 docker compose up -d`.

## Como rodar com Terraform (infraestrutura automatizada)

O `requisitos_projeto.MD` do professor pede "Infraestrutura automatizada com Terraform". A pasta `infra/` descreve a mesma
infraestrutura do `docker-compose.yml` (a tela, o PostgreSQL, a rede entre eles e as pastas montadas), e o Terraform cria tudo
com um comando, no Docker do seu computador. Pré-requisitos: Docker e Terraform 1.5 ou mais novo (`terraform version`; no Mac,
`brew install hashicorp/tap/terraform`). Dentro da pasta `infra/`:

```bash
terraform init       # uma vez só: baixa o provider do Docker (a versão do .terraform.lock.hcl)
terraform apply      # mostra o plano, pede "yes", constrói a imagem e sobe os 2 → http://localhost:8501
terraform plan       # com os 2 de pé: "No changes" (não há nada a refazer)
docker exec raiox-tela python -m pytest -q   # os testes dentro do contêiner, com o banco de testes
terraform destroy    # apaga os 2 contêineres e a rede; o banco e a data/ continuam
```

- **Um de cada vez:** o compose e o Terraform usam as portas 8501 e 5432 (com os 2 ligados, o `apply` dá
  `port is already allocated`). Rode `docker compose down` antes do `terraform apply`, ou suba o Terraform em outras portas:
  `terraform apply -var porta_tela=8502 -var porta_banco=5433`. As mesmas variáveis valem para o `destroy`.
- **O que sobrevive ao `destroy`:** a `data/` (pasta do seu computador, montada na tela) e o banco (volume `raiox-banco-dados`,
  que o Terraform não cria nem apaga). Apagar o banco de vez: `docker volume rm raiox-banco-dados`. O banco do compose e o do
  Terraform são volumes diferentes: a CVM carregada num não aparece no outro (os comandos de carga estão no topo do `infra/main.tf`).
- **IA ligada:** `terraform apply -var ia_real=true`. A chave não passa pelo Terraform: a tela lê o `.env` da raiz, montado só
  leitura no contêiner. Assim ela não fica no `terraform.tfstate`, onde o Terraform guarda as variáveis em texto puro. Mesmo assim,
  o `terraform.tfstate` fica fora do Git (`.gitignore`) e não se manda para ninguém.
- **Outras escolhas** (portas, senha do banco, dados falsos): `infra/variables.tf`. Para fixá-las, copie o
  `infra/terraform.tfvars.example` para `infra/terraform.tfvars`.
- **Mac:** se o `apply` não achar o Docker, rode antes `export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock`.
- O CI confere o Terraform (`terraform fmt` e `terraform validate`) em todo PR que mexe em `infra/` (`.github/workflows/terraform.yml`).

Sem Docker, siga a seção abaixo.

## Como rodar

Pré-requisitos: Python 3.14 (a versão do CI e do `requirements.txt`; o 3.11 não instala as versões fixadas), Git e
PostgreSQL (o banco do catálogo, regra do professor). Todos os comandos rodam na **raiz do repositório**.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie `.env.example` para `.env`. O `.env` nunca vai para o Git, porque tem a chave do Gemini e a senha do banco.
- Chave do Gemini (só para os modos com IA): cole em `GOOGLE_API_KEY`, ou dê dois cliques em `aprender/atalhos/configurar_chave.command`.
- PostgreSQL: troque `SUA_SENHA` em `DATABASE_URL` e `TEST_DATABASE_URL` pela senha do usuário `postgres`. Sem essas linhas,
  o código tenta a senha `postgres` (`raiox/banco.py`).

**Banco** (uma vez só): crie o banco do catálogo e o banco dos testes, que é apagado a cada teste.
Com Docker, `docker compose up -d banco` sobe um PostgreSQL já com os dois bancos, na porta 5432 (a do código).

```bash
psql -U postgres -c "CREATE DATABASE raiox"
psql -U postgres -c "CREATE DATABASE raiox_teste"
```

**Dados da CVM** (uns minutos; precisa de internet e do PostgreSQL ligado, porque os dois scripts gravam no banco):

```bash
python scripts/carregar_dfp.py        # baixa a DFP dos exercícios 2023–2025, limpa (raiox/limpeza.py) → data/contas.csv e tabelas contas e empresas
python scripts/indicadores.py         # 6 indicadores por empresa (C2) → data/indicadores.csv e tabela indicadores
python scripts/verificar_automatico.py   # opcional: compara receita, EBIT e lucro com o Yahoo Finance
```

**Testes** (não gastam crédito):

```bash
python -m pytest -q
```

Sem o PostgreSQL de testes (`TEST_DATABASE_URL`), os testes de banco aparecem como `skipped`: confira com `python -m pytest -q -rs`.

**Tela** (de dentro de `app/`, para o Streamlit ler o tema):

```bash
cd app && streamlit run streamlit_app.py                     # texto montado sem IA, sem custo
cd app && RAIOX_IA_REAL=1 streamlit run streamlit_app.py     # Gemini escreve o texto (≈ US$ 0,0012 por raio-x)
```

Com a `data/indicadores.csv` real, a tela busca as empresas no PostgreSQL e grava cada consulta na tabela `consultas`.
Com `RAIOX_DADOS=falsos` (ou sem a `data/`), usa as empresas inventadas de `falsos/`.

**Outros módulos**:

```bash
python -m raiox.ia --cvm 90001 --produto "software de gestão de frota" --objetivo "primeira conversa" --sem-ia
python -m raiox.segmentos          # refaz os grupos e o gráfico da silhueta
python -m raiox.checagem --teste   # checador com dados que têm erros de propósito (sem IA)
```

## Dados

- `data/indicadores.csv` vem do `scripts/indicadores.py`. Enquanto ele não existir, tudo usa `falsos/tabela_falsa.csv` (30 empresas inventadas).
- `falsos/`: tabela de empresas inventadas e versões falsas do C1 e do C3 (o falso do C3 chama o `raiox/ia.py` real, sem IA).
- Nada de `data/` (fora o `.gitkeep`) nem `.env` vai para o Git.

## Atalhos (Mac, dois cliques)

| atalho | o que faz | gasta crédito? |
|---|---|---|
| `aprender/atalhos/rodar_tela.command` | abre a tela com texto montado sem IA | não |
| `aprender/atalhos/rodar_tela_com_ia.command` | abre a tela com o Gemini escrevendo o raio-x | sim (≈ US$ 0,0012 por raio-x) |
| `aprender/atalhos/rodar_testes.command` | roda os testes automáticos | não |
| `aprender/atalhos/configurar_chave.command` | guarda a chave do Gemini no `.env` | não |
