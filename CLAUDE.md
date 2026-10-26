# Raio-X Comercial · contexto para o Claude Code

Projeto final da trilha IA Aplicada (SENAI/TCS). Equipe: Marcos (dados), Eduardo (IA e gestão),
Náthally (produto e métricas, deck), Miguel (tela e infraestrutura). Entrega na semana de 09–15/11/2026.

## O produto
O vendedor escolhe uma companhia aberta da CVM, informa o produto e o objetivo da reunião e recebe:
6 indicadores com fonte (DFP), posição contra o grupo de empresas parecidas (K-means), 3 a 5 perguntas
ligadas ao produto, lacunas e 5 empresas parecidas para prospectar (vizinhos mais próximos).

## Regra de ouro
O LLM (Gemini via LangChain) nunca escreve números. Ele usa marcadores como {margem_ebit};
o validador remove qualquer dígito fora de marcador; o código troca os marcadores pelos valores da tabela.
Não quebre essa regra em nenhuma mudança.

## Repositório
github.com/MiguelGrispan/trabalho-tcs (privado). Cada pessoa trabalha na sua branch (`eduardo`, `tratamento_dados`...) e junta na `main` por pull request.

## Estrutura e donos

| caminho | dono | o que é |
|---|---|---|
| `raiox/ia.py` | Eduardo | `preparar_raio_x(cd_cvm, produto, objetivo)` no formato do contrato C3 |
| `raiox/segmentos.py` | Eduardo | K-means (k pela silhueta) e 5 vizinhos → `data/segmentos.csv`, `docs/graficos/silhueta.png` |
| `avaliacao/avaliar.py` | Eduardo | roda os casos de avaliação e grava `avaliacao/resultados.csv` (C4) |
| `scripts/` | Marcos | `verificar_dfp.py`, `carregar_dfp.py` (→ `data/contas.csv`, `data/catalogo.db`), `indicadores.py` (→ `data/indicadores.csv`, C2) |
| `raiox/dados.py` | Marcos | `buscar_empresas`, `registrar_consulta` (contrato C1) |
| `raiox/checagem.py` | Marcos | regras de sanidade nos indicadores; `--com-ia` pede ao Gemini a causa provável (a IA não altera dados) |
| `app/` | Miguel | tela Streamlit (`app/streamlit_app.py`, tema em `app/.streamlit/config.toml`) |
| `Dockerfile`, `infra/` | Miguel | empacotamento e implantação |
| `avaliacao/*.csv` | Náthally | casos, revisão, conferência, testes com usuários (contrato C4) |

Pastas comuns (qualquer um mexe, avisando o grupo):
- `tests/`: testes automáticos (não chamam a API).
- `falsos/`: dados e módulos falsos no formato dos contratos (`tabela_falsa.csv`: 30 empresas inventadas).
- `docs/graficos/`: gráficos gerados. `atalhos/`: os `.command` de dois cliques (rodam a partir da raiz).
- `data/`: dados brutos da CVM e arquivos gerados. Só o `.gitkeep` vai para o Git.
- Raiz: `contratos.md` (C1 a C4, o único arquivo de contratos), `REGRAS-IA.md`, `README.md`, `requirements.txt`, `.env.example`.

Caminhos: todo código que usa `data/` ou `docs/` aponta para a **raiz** do repositório (`Path(__file__).resolve().parent.parent`), nunca para a pasta do próprio arquivo.

## Regras
1. **Não mexa em pasta de outro dono.** Precisa de mudança lá? Peça ao dono ou combine antes no grupo.
2. **Contrato antes de código.** Mudou um formato entre partes? Primeiro o `contratos.md`, avisando quem recebe; depois o código.
3. **Testes antes de dizer "pronto".** Rode `python -m pytest -q` e mostre o resultado. Código que não rodou não está pronto.
4. **O LLM nunca escreve números** (regra de ouro acima). Acima/abaixo/em linha é calculado por código.
5. **Nada de dados nem `.env` no Git.** Antes de todo commit, rode `git status` e leia a lista.

## Como rodar (sempre a partir da raiz do repositório)
- Ambiente Python: `.venv` na raiz (`python -m venv .venv`). No Mac do Eduardo, os atalhos usam o venv `~/bootcamp` se a `.venv` não existir.
- Testes: `python -m pytest -q`.
- Módulos de `raiox/`: `python -m raiox.ia ... --sem-ia`, `python -m raiox.segmentos`, `python -m raiox.checagem --teste`.
- Tela: `cd app && streamlit run streamlit_app.py` (de dentro de `app/` para ler o tema). `RAIOX_IA_REAL=1` usa o Gemini; sem isso, texto sem IA. Até o `raiox/dados.py` ficar pronto, a tela usa `falsos/`.

## Cuidados
- Siga o `REGRAS-IA.md` (regras do time para uso de IA).
- Não leia, mostre nem envie o conteúdo de `.env` (chave do Gemini, plano pré-pago).
- Toda chamada ao Gemini gasta crédito (≈ US$ 0,0008 por raio-x). Avise antes de rodar em lote.
- O Eduardo está aprendendo: explique cada mudança em português simples e prefira passos pequenos.
