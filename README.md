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

**Vai programar com o Claude Code?** Comece pelo [aprender/claude-code.md](aprender/claude-code.md): a frase de abertura, os modos e os limites.

**Começando agora?** Abra a pasta [aprender/](aprender/README.md): comandos (o que rodar, em qual pasta), o projeto
explicado para iniciantes e um notebook que segue uma empresa do começo ao fim. O plano e o que falta: [docs/PLANO.md](docs/PLANO.md).

## Fluxo

```
CVM (ZIPs da DFP 2023–2025 + cadastro)
   │  scripts/carregar_dfp.py      limpa contas, prefere consolidado      → data/contas.csv, PostgreSQL (contas, empresas)
   ▼
scripts/indicadores.py             6 indicadores por empresa (C2)        → data/indicadores.csv
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
docs/           plano, requisitos do guia, gráficos (docs/graficos/) e documentos da entrega
infra/          implantação · Miguel
aprender/       só para quem está aprendendo: comandos, guias, notebook passo a passo, atalhos do Mac
data/           dados da CVM e arquivos gerados: fica só no seu computador, não vai para o Git
```

Na raiz: `contratos.md`, `REGRAS-IA.md` (regras do time para uso de IA), `CLAUDE.md` (contexto e donos de cada pasta),
`requirements.txt` e `.env.example`.

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

```bash
psql -U postgres -c "CREATE DATABASE raiox"
psql -U postgres -c "CREATE DATABASE raiox_teste"
```

**Dados da CVM** (uns minutos; precisa de internet):

```bash
python scripts/carregar_dfp.py        # baixa a DFP 2023–2025, limpa (raiox/limpeza.py) → data/contas.csv e tabelas contas e empresas
python scripts/indicadores.py         # 6 indicadores por empresa (C2) → data/indicadores.csv
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
cd app && RAIOX_IA_REAL=1 streamlit run streamlit_app.py     # Gemini escreve o texto (≈ US$ 0,0008 por raio-x)
```

Enquanto o `raiox/dados.py` não estiver pronto, a tela usa as empresas inventadas de `falsos/`.

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
| `aprender/atalhos/rodar_tela_com_ia.command` | abre a tela com o Gemini escrevendo o raio-x | sim (≈ US$ 0,0008 por raio-x) |
| `aprender/atalhos/rodar_testes.command` | roda os testes automáticos | não |
| `aprender/atalhos/configurar_chave.command` | guarda a chave do Gemini no `.env` | não |
