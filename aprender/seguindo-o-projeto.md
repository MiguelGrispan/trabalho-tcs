# Seguindo o projeto: o que falta, de quem é e como provar

**Foto de 26/10/2026** (seções 2, 3 e 6 conferidas de novo em 28/10). Serve para aprender a diagnosticar um projeto e a
provar cada afirmação com um comando, **não** para saber o que fazer hoje: o status de cada requisito está no
[REQUISITOS.md](../docs/REQUISITOS.md) e as tarefas no [PLANO.md](../docs/PLANO.md). Onde este arquivo divergir deles, valem eles.
Escrito pelo Claude Code a pedido do Eduardo, comparando o repositório com o guia oficial do projeto final (o PDF de 07/10).
Desde 30/10, os requisitos vêm dos dois arquivos do professor, em `docs/professor/` (o `requisitos_projeto.MD`, de 29/10, exige o Terraform). Para entender os conceitos antes, leia [entenda-o-projeto.md](entenda-o-projeto.md).

Legenda: ✅ feito · 🟡 em parte · ⬜ falta. Cada afirmação tem uma **prova**: um comando que você roda na pasta
do repositório e vê o mesmo resultado. Se não bater, este texto está errado e deve ser corrigido.

---

## Como cheguei nestas conclusões

1. Baixei o estado do GitHub (`git fetch origin`) e listei os arquivos de cada branch:
   `fundacao` (esta reorganização), `origin/main`, `origin/tratamento_dados` (Marcos, 23/10) e `origin/feat/metricas` (Náthally, 26/10).
   O Miguel não tem branch no GitHub (`git branch -r`).
2. Li o código de cada parte e conferi se o que uma parte **entrega** é o que a outra **espera** (os contratos).
3. Rodei os testes (`8 passed`), a tela (com o `AppTest` do Streamlit: busca, gerar, 6 métricas, nenhum erro) e o `raiox.ia --sem-ia`.
4. Reproduzi o problema de formato dos CSV num arquivo de teste (seção 2, item 1).
5. Comparei cada requisito do guia com o que existe em **qualquer** branch.

**O que eu NÃO verifiquei** (trate como suposição até alguém confirmar):
- se o `scripts/carregar_dfp.py` roda inteiro hoje (não baixei a CVM: demora e grava em `data/`). O "650 empresas com receita" é número do Marcos, de 22/10;
- trabalho que esteja só no computador de alguém, sem ter ido para o GitHub (em especial do Miguel);
- formulários, entrevistas e tempos da Náthally que não estão no repositório;
- a data e o horário exatos da banca;
- as datas marcadas com *(plano do Eduardo)*: elas vêm do plano dele, não do repositório. As outras estão no `contratos.md`.

---

## 1. Resumo: o guia × o projeto

Mudou para [REQUISITOS.md](../docs/REQUISITOS.md), que é atualizado a cada PR. Quem faz o quê e quando está no [PLANO.md](../docs/PLANO.md).

---

## 2. O que falta para o produto funcionar com dados reais

Em ordem: cada item depende do anterior.

### 1) Os CSV são gravados num formato e lidos em outro ✅ consertado em 30/10 (tests/test_dados.py)
O `scripts/indicadores.py` grava o `indicadores.csv` com `;` e vírgula decimal (padrão do Excel brasileiro).
O `raiox/segmentos.py` lê no padrão do Python (`,` e ponto). Resultado: a tabela chega com **1 coluna só** e tudo quebra.
O mesmo acontece entre o `contas.csv` (gravado pelo `carregar_dfp.py`) e o `raiox/checagem.py`.

**Prova:**
```bash
grep -n 'sep=";"' scripts/indicadores.py scripts/carregar_dfp.py    # gravam com ;
grep -n "read_csv" raiox/segmentos.py raiox/checagem.py             # leem sem sep
python -c "
import pandas as pd
pd.read_csv('falsos/tabela_falsa.csv').head(3).to_csv('/tmp/x.csv', sep=';', decimal=',', index=False)
print('colunas lidas:', len(pd.read_csv('/tmp/x.csv').columns))"   # mostra: colunas lidas: 1
```
**Conserto sugerido:** escrever no C2 do `contratos.md` "CSV padrão: vírgula, ponto decimal, UTF-8" e trocar
as duas linhas `to_csv(... sep=";", decimal=",")` do Marcos (e a `read_csv` correspondente no `indicadores.py`).
Arquivo para abrir no Excel, se precisar, é um export separado.

### 2) `cd_cvm` como texto 🟡 o `indicadores.csv` já sai com int (30/10); o `raiox/dados.py` ainda devolve texto (Marcos)
O contrato diz que `cd_cvm` é número inteiro. O `carregar_dfp.py` e o `indicadores.py` leem como texto.
O `raiox/dados.py` não converte mais com `str()` (desde o #4), mas devolve o que vem do banco. Já está anotado no `contratos.md` (C1 e C2).
**Prova:** `grep -n '"cd_cvm": str' scripts/indicadores.py`.

### 3) A busca de empresas pode oferecer empresa sem raio-x ⬜ (Marcos)
`buscar_empresas` procura na tabela `contas` do banco. Se a empresa não estiver no `indicadores.csv`, o vendedor
escolhe e recebe o erro "Empresa X não está na tabela de indicadores". O contrato C1 pede
"só companhias ativas e com indicadores", e a consulta não filtra nenhum dos dois.
O C2 também fala numa tabela `indicadores` no PostgreSQL, mas o `indicadores.py` só grava o CSV.
**Prova:** leia a consulta SQL em `raiox/dados.py`, função `buscar_empresas`: ela não usa `situacao` nem `indicadores`.
`grep -n "to_sql" scripts/indicadores.py` não acha nada.
**Conserto sugerido:** o `indicadores.py` grava também a tabela `indicadores` no banco, e a busca faz `JOIN` com ela.

### 4) O trabalho do Marcos e da Náthally não consegue entrar na `main` ✅ portado pelos PRs #4 e #5 (27/10)
As branches `tratamento_dados` e `feat/metricas` foram criadas do zero, sem partir da `main`. O GitHub não junta
branches sem história em comum. **Prova:** `git merge-base origin/main origin/tratamento_dados` não imprime nada.
**Conserto:** depois que o PR `fundacao` entrar na `main`, cada um cria uma branch nova a partir dela e copia os
seus arquivos para a pasta certa. Ninguém precisa apagar nada.

### 5) A tela ainda usa os falsos ✅ (Miguel, MG4, 02/11)
O `USAR_DADOS_FALSOS = True` fixo saiu. A tela segue a mesma regra do `raiox/segmentos.py`: com a `data/indicadores.csv`
real, a busca e o registro da consulta usam o PostgreSQL (`raiox/dados.py`); com `RAIOX_DADOS=falsos`, os falsos.
**Prova:** `grep -n "DADOS_FALSOS =" app/streamlit_app.py` mostra `usando_falsos()`, e `python -m pytest -q tests/test_tela.py` passa.

### 6) Um teste vai quebrar no dia em que os dados reais chegarem ✅ (Eduardo, PR #6)
O teste do contrato C3 pede a empresa 90001, que só existe na tabela falsa. Desde o #6, o `tests/conftest.py` força a
tabela falsa em todo teste (`RAIOX_DADOS=falsos`), mesmo com os dados reais na `data/`.
**Prova:** `grep -n "RAIOX_DADOS" tests/conftest.py`; com a `data/` real, `python -m pytest -q` não tem `failed`.

### 7) As regras do texto estavam em duas versões diferentes ✅ (ED3, 29/10)
Até 28/10, a v1 da Náthally (`avaliacao/regras_prompt.md`) e a cópia v3 no `raiox/ia.py` não batiam (posição "em linha",
número de frases, nome da empresa na entrada). Desde a ED3 não existe mais cópia: o prompt **lê o arquivo da Náthally**
(regras v2, 29/10) e acrescenta só 3 notas do código (`NOTAS_DO_CODIGO`). Se ela mudar o arquivo, o Gemini recebe a mudança.
**Prova:** `grep -n "def regras" -A 4 raiox/ia.py`; `python -m pytest -q -k prompt` (4 testes, um deles confere que o
prompt começa com o texto do arquivo dela).

### 8) Não existe empacotamento ✅ Docker no PR #24 (30/10); ✅ Terraform na MG3 (31/10, Miguel)
Desde o #24, `docker compose up -d --build` sobe a tela e o PostgreSQL. Os três pontos do desenho estão lá: a pasta `data/`
entra no contêiner montada de fora (ela não está no Git nem na imagem); a chave entra como variável, nunca no código nem na
imagem; o contêiner roda a tela de dentro de `app/` (é onde o Streamlit acha o tema).
**Prova:** `docker compose ps` mostra os 2 `healthy`; `grep -n "data/" .dockerignore`; `grep -n "cd app" Dockerfile`.
O Terraform, **obrigatório** (`requisitos_projeto.MD`, Aplicação), está em `infra/` desde a MG3 (31/10): dentro da pasta,
`terraform apply` sobe a tela e o PostgreSQL, e o `terraform destroy` mantém o banco e a `data/`.
**Prova:** `git ls-files infra | grep '\.tf$'`; com os 2 de pé, `terraform plan` → `No changes`.

### 9) Como os dados chegam a quem não é o Marcos 🟡 combinado: zip da `data/` no Drive (PLANO, seção 5)
`data/` não vai para o Git. Cada pessoa roda `python scripts/carregar_dfp.py` e `python scripts/indicadores.py`
(a CVM é pública), ou o Marcos compartilha a pasta `data/` por Drive. Combinem qual dos dois.

### Pequenos
- ✅ A fonte saía "balanço consolidada" (deveria ser "consolidado"). Consertado no #6: `raiox/ia.py:75`. (Eduardo)
- ✅ `scripts/verificar_automatico.py` (branch do Marcos) usava `yfinance`. Foi cortado (PLANO, seção 7). (Marcos)

---

## 3. O mapa das ligações

| De | Para | Pelo quê | Status |
|---|---|---|---|
| `scripts/carregar_dfp.py` | `scripts/indicadores.py` | `data/contas.csv` | ✅ mesmo formato dos dois lados |
| `scripts/carregar_dfp.py` | `raiox/checagem.py` | `data/contas.csv` | ✅ CSV padrão (item 1) |
| `scripts/indicadores.py` | `raiox/segmentos.py` e `raiox/ia.py` | `data/indicadores.csv` (C2) | ✅ CSV padrão e `cd_cvm` int (itens 1 e 2) |
| `scripts/carregar_dfp.py` | `raiox/dados.py` | PostgreSQL (tabelas `contas` e `empresas`) | 🟡 falta filtro e tipo (itens 2 e 3) |
| `raiox/dados.py` | tela | `buscar_empresas`, `registrar_consulta` (C1) | ⬜ chave na tela (item 5) |
| `raiox/ia.py` | tela | `preparar_raio_x` (C3) | ✅ testado |
| `raiox/ia.py` | `avaliacao/avaliar.py` | `preparar_raio_x` (C4) | ✅ `avaliar.py` na `main` desde o #6 |
| regras da Náthally (`avaliacao/regras_prompt.md`) | `regras()` no `raiox/ia.py` | texto do prompt | ✅ o código lê o arquivo dela (item 7) |
| tela + `data/` | Docker/Terraform | contêiner | ✅ Docker com `docker compose` (#24); ✅ Terraform em `infra/` (MG3, item 8) |

---

## 4. Cada um: o que entender do código

As tarefas de cada um ficam no [PLANO.md](../docs/PLANO.md), seção 3. O que segue continua valendo.

### Eduardo (IA, ML e gestão)
**Entender do código:** `montar()` separa o que vai para o LLM do que nunca vai; `validar_e_preencher()` é a prova
de que a IA não escreve números; `segmentar()` (log da receita, cortar extremos, padronizar, silhueta).

### Marcos (dados)
**Entender do código:** `raiox/segmentos.py` lê o seu `indicadores.csv` (é ele que quebra com `;`);
`raiox/ia.py` usa as colunas do C2 pelo nome, então nome de coluna não pode mudar sem avisar.

### Miguel (tela e infraestrutura)
**Entender do código:** a tela só chama duas coisas, `buscar_empresas` (C1) e `preparar_raio_x` (C3); a primeira linha
depois dos imports põe a raiz no `sys.path`; o Streamlit lê o tema da pasta de onde é chamado; `/_stcore/health` responde `ok` (serve de healthcheck).

### Náthally (produto, métricas e deck)
**Entender do código:** o LLM recebe só setor, produto, objetivo e os indicadores já com a posição (veja `entrada` em
`montar()`); "Detalhes técnicos" na tela mostra o que o validador removeu, e isso é uma métrica de alucinação barrada.

### Todos
- Antes de pedir algo a uma IA, mandem junto o `contratos.md` e digam quais arquivos ela pode mexer.
- Branch nova sempre a partir da `main`. `main` só por pull request, com o CI verde (PLANO, seção 2).
- **Cada um apresenta a sua parte**: a divisão entre os membros vale nota (15% em comunicação e equipe).

---

## 5. O que foi cortado nesta reorganização e por quê

| Saiu | Por quê | Como conferir que nada quebrou |
|---|---|---|
| `prova_ia.py`, `resultado_com_ia.txt` | estudo da semana 1; o código oficial está em `raiox/` | `python -m pytest -q` → 8 passed |
| `rodar_com_ia.command`, `rodar_sem_ia.command` | só rodavam a `prova_ia.py` | — |
| `rodar_segmentos.command`, `checar_teste_com_ia.command` | pouco usados; os comandos estão no README | `python -m raiox.segmentos`, `python -m raiox.checagem --teste` |
| `LEIA-ME.md` | repetia o README | — |
| `falsos/dados_exemplo.py` (20 KB de números escritos à mão) | o falso agora chama o `raiox/ia.py` de verdade sem IA: menos código e a demo de teste usa o caminho real | tela: buscar "alfa" e gerar |
| `falsos/gerar_tabela_falsa.py` | o `tabela_falsa.csv` já está no Git | testes |
| 170 linhas do `.gitignore` | modelo genérico; ficou só o que o projeto usa | `git status --ignored` |

O Git guarda tudo: qualquer arquivo apagado volta com `git show <commit>:<arquivo>`.

---

## 6. Prove você mesmo (comandos e o que devem mostrar)

Rode na pasta do repositório, com o ambiente ativado e depois de `git fetch origin`.

| # | Comando | Deve mostrar |
|---|---|---|
| A | `for r in origin/main origin/tratamento_dados origin/feat/metricas; do git ls-tree -r --name-only $r \| grep -ciE '\.bpmn$\|\.ipynb$\|dockerfile\|\.tf$'; done` | em 28/10: `1` na `main` (o notebook do `aprender/`), `0` na `tratamento_dados` e `1` na `feat/metricas`. Dockerfile e Terraform só na `origin/docs-docker-e-terraform` |
| B | `python -m pytest -q` | nenhum `failed`. Em 28/10: 61 passed e 3 skipped sem `data/`; 64 passed com a `data/` real |
| C | `git merge-base origin/main origin/tratamento_dados; echo $?` | só `1` (sem história em comum) |
| D | o comando do item 1 da seção 2 | `colunas lidas: 1` |
| E | `grep -n "RAIOX_DADOS" tests/conftest.py` | a linha que força a tabela falsa nos testes (item 6) |
| F | `grep -n "DADOS_FALSOS =" app/streamlit_app.py` | desde 02/11 (MG4): `DADOS_FALSOS = usando_falsos()` (antes, `USAR_DADOS_FALSOS = True`) |
| G | `git branch -r` | em 28/10: `origin/docs-docker-e-terraform` (Miguel) |
| H | `ls avaliacao/` | `README.md`, `avaliar.py`, `casos_avaliacao.csv`, `conferencia.csv`, `regras_prompt.md` |

Se algum resultado for diferente, o projeto mudou depois de 26/10 (ótimo, atualizem este arquivo) ou eu errei
(avisem e corrijam). Este arquivo é para ser atualizado: quando um item ficar pronto, troquem ⬜ por ✅ e escrevam a prova.

---

## 7. Datas

Mudaram para o [PLANO.md](../docs/PLANO.md) (calendário na seção 3 e pontos de integração na seção 5).
