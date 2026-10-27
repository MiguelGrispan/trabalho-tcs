# Seguindo o projeto: o que falta, de quem é e como provar

Estado em **26/10/2026**. O status de cada requisito agora fica no [REQUISITOS.md](../docs/REQUISITOS.md) e as datas no
[PLANO.md](../docs/PLANO.md); onde este arquivo divergir deles, valem eles. Escrito pelo Claude Code a pedido do Eduardo, comparando o repositório com o
guia oficial do projeto final. Para entender os conceitos antes, leia [entenda-o-projeto.md](entenda-o-projeto.md).

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

### 1) Os CSV são gravados num formato e lidos em outro ⬜ (Marcos + Eduardo)
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

### 2) `cd_cvm` como texto ⬜ (Marcos)
O contrato diz que `cd_cvm` é número inteiro. O `carregar_dfp.py` e o `indicadores.py` leem como texto, e o
`raiox/dados.py` devolve texto (`"cd_cvm": str(codigo)...`). Já está anotado no `contratos.md` (C1 e C2).
**Prova:** `grep -n "str(codigo)" raiox/dados.py` e `grep -n '"cd_cvm": str' scripts/indicadores.py`.

### 3) A busca de empresas pode oferecer empresa sem raio-x ⬜ (Marcos)
`buscar_empresas` procura na tabela `contas` do banco. Se a empresa não estiver no `indicadores.csv`, o vendedor
escolhe e recebe o erro "Empresa X não está na tabela de indicadores". O contrato C1 pede
"só companhias ativas e com indicadores", e a consulta não filtra nenhum dos dois.
O C2 também fala numa tabela `indicadores` dentro do `catalogo.db`, mas o `indicadores.py` só grava o CSV.
**Prova:** leia a consulta SQL em `raiox/dados.py`, função `buscar_empresas`: ela não usa `situacao` nem `indicadores`.
`grep -n "to_sql" scripts/indicadores.py` não acha nada.
**Conserto sugerido:** o `indicadores.py` grava também a tabela `indicadores` no banco, e a busca faz `JOIN` com ela.

### 4) O trabalho do Marcos e da Náthally não consegue entrar na `main` ⬜ (Marcos, Náthally)
As branches `tratamento_dados` e `feat/metricas` foram criadas do zero, sem partir da `main`. O GitHub não junta
branches sem história em comum. **Prova:** `git merge-base origin/main origin/tratamento_dados` não imprime nada.
**Conserto:** depois que o PR `fundacao` entrar na `main`, cada um cria uma branch nova a partir dela e copia os
seus arquivos para a pasta certa (passo a passo na seção 4). Ninguém precisa apagar nada.

### 5) A tela ainda usa os falsos ⬜ (Miguel)
`app/streamlit_app.py` tem `USAR_DADOS_FALSOS = True`. Trocar para `False` quando os itens 1 a 3 estiverem prontos.
**Prova:** `grep -n "USAR_DADOS_FALSOS =" app/streamlit_app.py`.

### 6) Um teste vai quebrar no dia em que os dados reais chegarem 🟡 (Eduardo)
O teste do contrato C3 pede a empresa 90001, que só existe na tabela falsa. Com o `indicadores.csv` real, ela some.
**Prova:** `grep -n "90001" tests/test_raio_x.py`.

### 7) As regras do texto estão em duas versões diferentes ⬜ (Náthally + Eduardo)
A `regras_v1.md` da Náthally (branch `feat/metricas`) e as regras v3 no `raiox/ia.py` não batem:
a v1 não conhece a posição "em linha", pede resumo de 2 a 4 frases (o código pede 2 ou 3) e diz que o LLM recebe
o nome da empresa (ele não recebe, de propósito: veja `entrada = {...}` em `montar()`).
**Prova:** `git show origin/feat/metricas:Semana_01/Sexta_23-10/regras_v1.md | grep -n "posicao\|frases"` e `grep -n "entrada = " raiox/ia.py`.

### 8) Não existe empacotamento ⬜ (Miguel)
Sem `Dockerfile` nem Terraform (comando A). Pontos que precisam estar no desenho: a pasta `data/` entra no
contêiner montada de fora (ela não está no Git); a chave entra como variável sensível, nunca no código nem na imagem;
o contêiner roda a tela de dentro de `app/` (é onde o Streamlit acha o tema).

### 9) Como os dados chegam a quem não é o Marcos 🟡 (todos)
`data/` não vai para o Git. Cada pessoa roda `python scripts/carregar_dfp.py` e `python scripts/indicadores.py`
(a CVM é pública), ou o Marcos compartilha a pasta `data/` por Drive. Combinem qual dos dois.

### Pequenos
- A fonte sai "balanço consolidada" (deveria ser "consolidado"): `raiox/ia.py`, linhas com `"balanço {d}"`. (Eduardo)
- `scripts/verificar_automatico.py` (branch do Marcos) usa `yfinance`, que não está no `requirements.txt`. (Marcos)

---

## 3. O mapa das ligações

| De | Para | Pelo quê | Status |
|---|---|---|---|
| `scripts/carregar_dfp.py` | `scripts/indicadores.py` | `data/contas.csv` | ✅ mesmo formato dos dois lados |
| `scripts/carregar_dfp.py` | `raiox/checagem.py` | `data/contas.csv` | ⬜ formato (item 1) |
| `scripts/indicadores.py` | `raiox/segmentos.py` e `raiox/ia.py` | `data/indicadores.csv` (C2) | ⬜ formato e tipo (itens 1 e 2) |
| `scripts/carregar_dfp.py` | `raiox/dados.py` | `data/catalogo.db` | 🟡 falta filtro e tipo (itens 2 e 3) |
| `raiox/dados.py` | tela | `buscar_empresas`, `registrar_consulta` (C1) | ⬜ chave na tela (item 5) |
| `raiox/ia.py` | tela | `preparar_raio_x` (C3) | ✅ testado |
| `raiox/ia.py` | `avaliacao/avaliar.py` | `preparar_raio_x` (C4) | ⬜ o `avaliar.py` não existe |
| regras da Náthally | `REGRAS` no `raiox/ia.py` | texto do prompt | ⬜ versões diferentes (item 7) |
| tela + `data/` | Docker/Terraform | contêiner | ⬜ (item 8) |

---

## 4. Cada um: o que fazer e o que entender

### Eduardo (IA, ML e gestão)
**Fazer, em ordem:**
1. Pedir a revisão do PR `fundacao` (Miguel é o dono do repositório) e avisar o grupo da estrutura nova.
2. Combinar com o Marcos o formato do CSV (item 1) e escrever no C2.
3. **qua 28/10:** 3 raio-x reais para a Náthally ajustar as regras. Precisa do `indicadores.csv` real: se não chegar,
   rode você mesmo os dois scripts do Marcos e converta o formato localmente.
4. Rodar `segmentos` e `ia` com dados reais; gerar a silhueta e um gráfico dos grupos em 2D (vale como visualização).
5. Criar `avaliacao/avaliar.py` (lê `casos_avaliacao.csv`, grava `resultados.csv`, formato no C4).
6. Consertar o teste da empresa 90001 (item 6) e o "balanço consolidada".
7. Escrever a justificativa técnica (por que dados estruturados + validador, e não RAG nem fine-tuning) e a seção
   "Como usamos IA para programar" do README.
8. Gestão: confirmar data e horário da banca; lembrar a regra "ninguém usa `push --force` na branch do outro".

**Entender do código:** `montar()` separa o que vai para o LLM do que nunca vai; `validar_e_preencher()` é a prova
de que a IA não escreve números; `segmentar()` (log da receita, cortar extremos, padronizar, silhueta).

### Marcos (dados)
**Fazer, em ordem:**
1. Formato do CSV e `cd_cvm` inteiro (itens 1 e 2): duas linhas de `to_csv`, uma de `read_csv`, uma conversão.
2. Gravar a tabela `indicadores` no `catalogo.db` e fazer a busca só mostrar empresas ativas com indicadores (item 3).
3. **dom 01/11:** `indicadores.csv` real para o Eduardo e `raiox/dados.py` pronto para o Miguel (combinar como os
   dados chegam a eles, item 9).
4. Trazer o resto do seu trabalho para a estrutura nova: `git switch main && git pull && git switch -c dados-s2`, depois
   copiar da sua branch `conferir_s1.py` e `verificar_automatico.py` para `scripts/`, os seus testes para `tests/`
   (trocando `from src import dados` por `from raiox import dados`), e decidir entre `scripts/dados.py` e
   `raiox/dados.py` (ficar com um só). Comando para copiar um arquivo:
   `git show origin/tratamento_dados:scripts/conferir_s1.py > scripts/conferir_s1.py`.
5. Rodar `python -m raiox.checagem data/indicadores.csv data/contas.csv` com os dados reais e decidir o que excluir.
6. BPMN 2.0 (`docs/bpmn/`: processo de hoje e com o Raio-X), EDA (`notebooks/eda.ipynb`) e montar o PDF.

**Entender do código:** `raiox/segmentos.py` lê o seu `indicadores.csv` (é ele que quebra com `;`);
`raiox/ia.py` usa as colunas do C2 pelo nome, então nome de coluna não pode mudar sem avisar.

### Miguel (tela e infraestrutura)
**Fazer, em ordem:**
1. Revisar e juntar o PR `fundacao` na `main` (você é o dono do repositório).
2. `Dockerfile` + `.dockerignore` (fora da imagem: `.env`, `data/`, `.git`, `tests/`, `docs/`, `aprender/`).
3. `infra/` com Terraform (provider Docker): imagem, contêiner, porta 8501, `data/` montada, chave como variável `sensitive`.
   O `.gitignore` já tira do Git o estado do Terraform (`*.tfstate`), que pode guardar a chave.
4. **ter 03/11:** ligar os dados reais na tela (item 5). Sugestão: trocar a constante por uma variável de ambiente, para o Terraform escolher.
5. Diagrama da arquitetura (pode partir da seção 3 do `entenda-o-projeto.md`) e o **vídeo de backup** da demo.

**Entender do código:** a tela só chama duas coisas, `buscar_empresas` (C1) e `preparar_raio_x` (C3); a primeira linha
depois dos imports põe a raiz no `sys.path`; o Streamlit lê o tema da pasta de onde é chamado; `/_stcore/health` responde `ok` (serve de healthcheck).

### Náthally (produto, métricas e deck)
**Fazer, em ordem:**
1. Trazer o seu trabalho para a estrutura nova: branch a partir da `main`, `Semana_01/` vai para `docs/produto/` e a
   `regras_v1.md` vira `avaliacao/regras_prompt.md`.
2. Alinhar as regras com o que o código manda de verdade (item 7). O Eduardo copia a versão final para o `ia.py`.
3. `avaliacao/casos_avaliacao.csv` (20 casos: empresa × produto × objetivo), `tempo_manual.csv`, `revisao.csv`,
   `testes_usuarios.csv` (sem nome, e-mail ou telefone: use `pessoa_id`). Colunas no C4.
4. Conta do ROI com os tempos medidos; texto de governança e ética para o PDF.
5. Deck e roteiro de 20 minutos com o tempo de cada parte; ensaio cronometrado.

**Entender do código:** o LLM recebe só setor, produto, objetivo e os indicadores já com a posição (veja `entrada` em
`montar()`); "Detalhes técnicos" na tela mostra o que o validador removeu, e isso é uma métrica de alucinação barrada.

### Todos
- Antes de pedir algo a uma IA, mandem junto o `contratos.md` e digam quais arquivos ela pode mexer.
- Branch nova sempre a partir da `main`. `main` só por pull request com 1 revisão.
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
| A | `for r in origin/main origin/tratamento_dados origin/feat/metricas; do git ls-tree -r --name-only $r \| grep -ciE '\.bpmn$\|\.ipynb$\|dockerfile\|\.tf$'; done` | `0` três vezes (não há BPMN, notebook, Dockerfile nem Terraform) |
| B | `python -m pytest -q` | `8 passed` |
| C | `git merge-base origin/main origin/tratamento_dados; echo $?` | só `1` (sem história em comum) |
| D | o comando do item 1 da seção 2 | `colunas lidas: 1` |
| E | `grep -n "90001" tests/test_raio_x.py` | a linha do teste do C3 |
| F | `grep -n "USAR_DADOS_FALSOS =" app/streamlit_app.py` | `USAR_DADOS_FALSOS = True` |
| G | `git branch -r` | nenhuma branch do Miguel |
| H | `ls avaliacao/` | só `README.md` |

Se algum resultado for diferente, o projeto mudou depois de 26/10 (ótimo, atualizem este arquivo) ou eu errei
(avisem e corrijam). Este arquivo é para ser atualizado: quando um item ficar pronto, troquem ⬜ por ✅ e escrevam a prova.

---

## 7. Datas

Mudaram para o [PLANO.md](../docs/PLANO.md) (calendário na seção 3 e pontos de integração na seção 5).
