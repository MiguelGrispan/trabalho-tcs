# Comandos: o que rodar, em qual pasta, e o que deve aparecer

**Regra número 1:** quase tudo roda na **raiz do repositório**, a pasta `trabalho-tcs/`, onde estão o `README.md` e o
`requirements.txt`. A única exceção é a tela, que roda de dentro de `app/`.

Para saber onde você está, use `pwd`. Para ir até a raiz, use `cd ~/projeto_final_tcs/trabalho-tcs` (troque pelo caminho da sua máquina).

Legenda: ✅ conferido em 27/10/2026 · ⏳ depende de um PR ou sessão que ainda não entrou na `main` (indicado na linha).

---

## 1. Preparar o computador (uma vez só)

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| criar o ambiente Python | raiz | `python3 -m venv .venv` | nada (cria a pasta `.venv/`) |
| ativar o ambiente (toda vez que abrir o terminal) | raiz | `source .venv/bin/activate` | `(.venv)` no começo da linha |
| instalar as bibliotecas | raiz | `pip install -r requirements.txt` | `Successfully installed ...` |
| guardar a chave do Gemini (só para usar a IA) | raiz | `cp .env.example .env` e depois cole a chave no `.env`, ou dê dois cliques em `aprender/atalhos/configurar_chave.command` | o arquivo `.env` existe (`ls -a`). **Nunca** mande esse arquivo para ninguém |

No Mac do Eduardo, o ambiente é `~/bootcamp`: `source ~/bootcamp/bin/activate`.

---

## 2. Testes ✅

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| rodar todos os testes | raiz | `python -m pytest -q` | `N passed` (e talvez `skipped`). **Nenhum** `failed` |
| ver por que um teste foi pulado | raiz | `python -m pytest -q -rs` | o motivo de cada `skipped` (ex.: "sem data/indicadores.csv") |
| rodar só um arquivo | raiz | `python -m pytest -q tests/test_raio_x.py` | só os testes daquele arquivo |
| rodar só os testes com uma palavra no nome | raiz | `python -m pytest -q -k validador` | só os testes do validador |
| teste de ponta a ponta com os dados reais | raiz | `python -m pytest -q tests/test_ponta_a_ponta.py` | passa se você tiver a `data/` real; é pulado se não tiver |
| rodar os testes sem instalar Python | raiz | `docker compose run --rm tela python -m pytest -q` | o mesmo resultado, dentro do contêiner (seção 6) |
| dois cliques (Mac) | — | `aprender/atalhos/rodar_testes.command` | a mesma lista de testes, numa janela |

**Deu `failed`?** Leia a última linha do erro. Ela diz o arquivo, a linha e o que era esperado. Não apague o teste: ou o código quebrou, ou o contrato mudou.

---

## 3. Dados da CVM (Marcos)

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| conferir se a CVM está no ar e quantas empresas têm receita | raiz | `python scripts/verificar_dfp.py` | contagens e nomes das contas |
| baixar e limpar a DFP 2023–2025 ✅ | raiz | `python scripts/carregar_dfp.py` | uns 20 s; "contas.csv salvo com ... linhas" e "Banco de dados PostgreSQL atualizado" |
| calcular os 6 indicadores ✅ | raiz | `python scripts/indicadores.py` | nada na tela; cria `data/indicadores.csv` (cerca de 595 empresas) |
| checar a tabela com os dados falsos (5 erros plantados) ✅ | raiz | `python -m raiox.checagem --teste` | uma lista de alertas e "Salvo em anomalias.csv" |
| checar a tabela real ✅ | raiz | `python -m raiox.checagem data/indicadores.csv data/contas.csv` | "595 empresas · ... · 0 erros" e "Salvo em anomalias.csv" |

Se a sua `data/` é anterior a 30/10, o `indicadores.csv` ainda está com `;`: rode de novo os dois scripts acima.

---

## 4. Modelo (grupos e empresas parecidas) e IA (Eduardo)

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| agrupar as empresas (K-means) ✅ | raiz | `python -m raiox.segmentos` | a silhueta por k, o k escolhido e o tamanho de cada grupo; cria `data/segmentos.csv` e o gráfico em `docs/graficos/` |
| forçar a tabela falsa mesmo com os dados reais | raiz | `RAIOX_DADOS=falsos python -m raiox.segmentos` | usa as 30 empresas inventadas e não grava nada em `data/` |
| raio-x **sem IA** (não gasta crédito) ✅ | raiz | `python -m raiox.ia --cvm 90001 --produto "software de frota" --objetivo "conhecer a operação" --sem-ia` | um JSON com empresa, 6 indicadores, grupo, parecidas, resumo, perguntas e lacunas |
| raio-x **com IA** (≈ US$ 0,0012 por chamada) | raiz | o mesmo comando, sem o `--sem-ia` | o mesmo JSON, com o texto escrito pelo Gemini; em `removidos`, o que o validador barrou |
| rodar a avaliação dos casos | raiz | `python -m avaliacao.avaliar` (sem IA) ou `python -m avaliacao.avaliar --com-ia` | "N casos → avaliacao/resultados.csv · itens removidos: … · custo total: …" |

Com os dados reais, a WEG é `--cvm 5410`, a Magazine Luiza é `22470` e a Camil é `24228`.
Com os dados falsos, as empresas vão de `90001` a `90030`.

**Mais de 10 chamadas à IA:** avise o grupo antes (gasta crédito).

---

## 5. Tela (Miguel) ✅

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| abrir a tela sem IA | **`app/`** | `cd app` e depois `streamlit run streamlit_app.py` | o navegador abre em `http://localhost:8501` |
| abrir a tela com IA | **`app/`** | `RAIOX_IA_REAL=1 streamlit run streamlit_app.py` | o mesmo, com o texto do Gemini |
| parar a tela | o terminal da tela | `Ctrl + C` | o terminal volta a aceitar comandos |
| dois cliques (Mac) | — | `aprender/atalhos/rodar_tela.command` ou `rodar_tela_com_ia.command` | a tela abre no navegador |

**Por que de dentro de `app/`?** O Streamlit procura o tema (`.streamlit/config.toml`) na pasta de onde você roda o comando.

---

## 6. Docker ✅ (MG2, PR #24) e Terraform ✅ (MG3, obrigatório) (Miguel)

O `docker-compose.yml` sobe 2 contêineres: a `tela` e o `banco` (PostgreSQL 17, o mesmo do CI). Conferido em 30/10 no Linux do Miguel.
O Terraform (`infra/`) sobe os mesmos 2, com os nomes `raiox-tela` e `raiox-banco` e as mesmas portas: rode um de cada vez
(`docker compose down` antes do `terraform apply`). Conferido em 31/10 no Linux do Miguel (Terraform 1.17.0), nas portas 8502 e 5433.

| o que | onde | comando | o que deve aparecer |
|---|---|---|---|
| subir a tela e o banco | raiz | `docker compose up -d --build` | a 1ª vez demora uns 5 min; depois, a tela em `http://localhost:8501` |
| ver se os 2 estão de pé | raiz | `docker compose ps` | `banco` e `tela` com `(healthy)` |
| conferir a tela | qualquer pasta | `curl localhost:8501/_stcore/health` | `ok` |
| ligar a IA (gasta crédito) | raiz | `RAIOX_IA_REAL=1 docker compose up -d` | a chave vem do `GOOGLE_API_KEY` do `.env`; sem ela, o "Gerar raio-x" mostra um erro (a volta sozinha para o modo sem IA é a MG4) |
| carregar a CVM no banco do contêiner | raiz | `docker compose run --rm --user "$(id -u):$(id -g)" tela python scripts/carregar_dfp.py` e depois o mesmo com `scripts/indicadores.py` | "contas.csv salvo com 384561 linhas" e "Banco de dados PostgreSQL atualizado" (cerca de 1 min, com o download). No Mac, sem o `--user` |
| rodar os testes no contêiner | raiz | `docker compose run --rm tela python -m pytest -q` | `87 passed` em 30/10, nenhum pulado |
| ver o que a tela escreve | raiz | `docker compose logs -f tela` | as mensagens da tela (`Ctrl + C` sai) |
| subir só o banco (para rodar o Python fora do Docker) | raiz | `docker compose up -d banco` | o PostgreSQL na porta 5432, já com o `raiox` e o `raiox_teste` |
| desligar | raiz | `docker compose down` | os 2 param; o banco fica guardado no volume `banco-dados` |
| subir com Terraform | `infra/` | `terraform init` (uma vez só) e depois `terraform apply` (responda `yes`) | `Apply complete! Resources: 5 added`; a tela em `http://localhost:8501` |
| conferir que nada mudou | `infra/` | `terraform plan` | `No changes. Your infrastructure matches the configuration.` |
| testes no contêiner do Terraform | qualquer pasta | `docker exec raiox-tela python -m pytest -q` | `87 passed` em 31/10, nenhum pulado |
| derrubar o Terraform | `infra/` | `terraform destroy` (responda `yes`) | `Destroy complete! Resources: 5 destroyed.`; o banco (volume `raiox-banco-dados`) e a `data/` continuam |

---

## 7. Git do dia a dia (uma sessão = uma branch = um PR)

No Claude Code, o `/inicio-de-sessao` e o `/fim-de-sessao` fazem estes passos por você. A tabela serve para entender o que
eles fazem, ou para fazer à mão.

| o que | onde | comando |
|---|---|---|
| ver em que branch estou e o que mudou | raiz | `git status` |
| começar uma tarefa | raiz | `git switch main` → `git pull` → `git switch -c seunome-tarefa` |
| trazer a `main` nova para a sua branch | raiz | `git switch main` → `git pull` → `git switch seunome-tarefa` → `git merge main` → `python -m pytest -q` |
| salvar um passo | raiz | `git add <arquivos>` → `git commit -m "o que mudou"` (antes, leia o `git status`) |
| mandar para o GitHub | raiz | `git push -u origin seunome-tarefa` (da segunda vez em diante, só `git push`) |
| abrir o PR | raiz | `gh pr create`, ou no site do GitHub: botão "Compare & pull request" |
| deu conflito no merge e quero desistir | raiz | `git merge --abort` (depois fale com o dono do arquivo) |

**Nunca:** `git push --force`, `git rebase`, commit direto na `main`, nem `git add .` sem ler o `git status`.

---

## 8. Entender o código

| o que | onde | comando |
|---|---|---|
| abrir o notebook que segue uma empresa do começo ao fim | raiz | `jupyter notebook aprender/passo_a_passo.ipynb`, ou abra o arquivo no VS Code |
| pedir explicação ao Claude Code sem mudar nada | raiz | `claude` e depois: "Explique para iniciante, sem alterar nada: o que faz a função montar() do raiox/ia.py?" |

---

## 9. Erros comuns

| aparece | por quê | o que fazer |
|---|---|---|
| `ModuleNotFoundError: No module named 'raiox'` | você não está na raiz | `cd` até a pasta `trabalho-tcs/` e rode de novo |
| `command not found: streamlit` (ou `pytest`) | o ambiente não está ativado | `source .venv/bin/activate` |
| `Empresa X não está na tabela de indicadores` | o `cd_cvm` não existe nos dados que você tem (real × falso) | confira com `python -m raiox.segmentos` quais dados estão sendo usados |
| a tabela tem 1 coluna só | o CSV está com `;` (a sua `data/` é anterior a 30/10) | rode de novo os dois scripts da seção 3 |
| `port is already allocated` ao subir o `docker compose` | outro programa já usa a porta 5432 (outro PostgreSQL) ou a 8501 (outra tela) | pare o outro, ou suba o banco em outra porta: `PORTA_BANCO=5433 docker compose up -d` |
| `Permission denied` em `data/` dentro do contêiner (Linux) | o contêiner roda com outro usuário | acrescente `--user "$(id -u):$(id -g)"` no `docker compose run` |
| `402` ou "quota" ao chamar a IA | o crédito do Gemini acabou | avise o Eduardo; use o modo sem IA |
| a tela abre sem as cores do projeto | você rodou da raiz, não de `app/` | `cd app` antes do `streamlit run` |
