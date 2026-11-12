# Entenda o projeto (para iniciantes)

Este arquivo explica o Raio-X Comercial do zero: o que ele faz, por que foi feito assim, como o código funciona
e como trabalhar nele sem quebrar nada. Não precisa saber programar bem para ler.
O que falta fazer, e quem faz, está no [PLANO](../docs/PLANO.md) (seção 3) e no [REQUISITOS](../docs/REQUISITOS.md).
O que o projeto **precisa** ter vem dos arquivos do professor, em [docs/professor/](../docs/professor/): eles valem mais que qualquer nota.

---

## 1. A ideia em 30 segundos

Um vendedor que vende para grandes empresas vai ter a **primeira reunião** com um cliente novo.
Hoje ele se prepara à mão: procura números soltos no site da empresa, não compara com ninguém e improvisa perguntas.

No Raio-X, o vendedor escolhe a empresa, diz **o que vende** e **o objetivo da reunião**, e recebe em segundos:

1. **6 números da empresa** (receita, crescimento, margens, ativo, endividamento), cada um com a fonte oficial;
2. se cada número está **acima, abaixo ou em linha** com empresas parecidas;
3. **3 a 5 perguntas** para a reunião, ligadas ao produto dele;
4. **o que os números não mostram** (quem decide a compra, orçamento, fornecedor atual);
5. **5 empresas parecidas** para ele procurar depois.

**Por que isso vale dinheiro (o ROI que a banca vai perguntar):**
economia por mês = reuniões por mês × (minutos à mão − minutos com a ferramenta) × custo da hora do vendedor.
Com os números da Náthally (12/11, `docs/produto/roi.md`): 8 reuniões × (45 − 17,5 min) × R$ 74,40 por hora ≈ **R$ 273 e 3,7 h por mês** por vendedor.
Os 45 min foram declarados por um diretor comercial entrevistado; os 17,5 min, cronometrados com a ferramenta, conferindo as fontes. É uma entrevista só: uma estimativa.

---

## 2. A regra mais importante: a IA nunca escreve números

IA generativa (o "LLM", aqui o Gemini do Google) às vezes **inventa** coisas. Isso se chama **alucinação**.
Num produto que fala de dinheiro, um número inventado é o pior erro possível. Então o projeto foi desenhado assim:

```
1. O CÓDIGO calcula os números e decide "acima/abaixo".
2. O LLM escreve o texto usando MARCADORES no lugar dos números:
       "a margem EBIT ({margem_ebit}) está acima do grupo ({margem_ebit_grupo})"
3. O VALIDADOR (código) apaga qualquer frase que tenha um dígito fora de marcador.
4. O CÓDIGO troca cada marcador pelo valor verdadeiro da tabela:
       "a margem EBIT (16,8%) está acima do grupo (14,9%)"
```

Resultado: mesmo que o LLM tente escrever "a margem é 20%", essa frase é removida e aparece em
"Detalhes técnicos" na tela, com o motivo. **Todo número que o vendedor vê veio da tabela, nunca do LLM.**

**Como provar isso (rode você mesmo):** o teste abaixo dá ao validador uma frase com "3 pontos" e confere que ela foi removida.

```bash
python -m pytest -q -k digito
```

O código está em `raiox/ia.py`, funções `checar()` e `validar_e_preencher()`.

---

## 3. O caminho dos dados (duas fases)

```
PREPARAÇÃO  (roda 1 vez, demora minutos; refaz quando sai balanço novo)
  Site da CVM ──► scripts/carregar_dfp.py ──► data/contas.csv + PostgreSQL   (Marcos)
                  scripts/indicadores.py  ──► data/indicadores.csv  (6 números por empresa)
                  raiox/checagem.py       ──► aponta empresas com números suspeitos
                  raiox/segmentos.py      ──► data/segmentos.csv  (grupo + 5 parecidas)   (Eduardo)

CONSULTA  (cada vez que o vendedor usa, segundos)
  Tela (app/streamlit_app.py)                                                        (Miguel)
    ├─ buscar_empresas("vale")          raiox/dados.py  → lista de empresas (SQL)
    ├─ preparar_raio_x(empresa, produto, objetivo)   raiox/ia.py  → números + texto
    │      └─ Gemini (pela internet, com a chave do .env)
    └─ registrar_consulta(...)          raiox/dados.py  → guarda tempo, tokens e custo
```

**Por que duas fases?** Baixar e limpar a CVM leva minutos e só muda uma vez por ano.
A consulta precisa ser rápida. Então a preparação gera arquivos em `data/`, e a tela só lê esses arquivos.

**Por que `data/` não vai para o GitHub?** São arquivos grandes (centenas de MB) e qualquer um consegue gerar de novo
rodando os scripts, porque a CVM é pública. Cada pessoa gera o seu `data/` no próprio computador.

---

## 4. Os conceitos, um por um

| Palavra | O que é, em uma frase | Onde aparece |
|---|---|---|
| **CVM / DFP** | A CVM é quem fiscaliza a bolsa; DFP é o balanço anual que toda companhia aberta entrega a ela, publicado em CSV | `scripts/carregar_dfp.py` |
| **CSV** | Planilha em texto: uma linha por registro, colunas separadas por vírgula (ou ponto e vírgula) | `data/*.csv`, `falsos/*.csv` |
| **Pandas** | Biblioteca Python para ler e limpar tabelas (o "Excel do Python") | todo o código |
| **SQL / PostgreSQL** | SQL é a linguagem para consultar tabelas; PostgreSQL é o banco de dados que guarda o catálogo (endereço em `DATABASE_URL`, no `.env`) | `raiox/dados.py` |
| **Nulo** | Valor que falta. Aqui ele **continua faltando** (a tela mostra "sem dado"); nunca é inventado | `raiox/ia.py`, `fmt()` |
| **K-means** | Algoritmo de ML que separa as empresas em grupos de perfil parecido, sem ninguém dizer a resposta certa (não supervisionado) | `raiox/segmentos.py` |
| **Silhueta** | Nota de 0 a 1 que diz o quanto os grupos ficaram bem separados; testamos de 3 a 8 grupos e ficamos com a maior nota | `segmentar()` |
| **Padronizar** | Colocar todas as colunas na mesma régua; sem isso a receita (bilhões) engoliria a margem (0,1) | `StandardScaler` |
| **Vizinhos mais próximos** | As 5 empresas com números mais parecidos; viram a lista "para prospectar" | `NearestNeighbors` |
| **Mediana** | O valor do meio. "O grupo" mostrado ao vendedor é a mediana, porque não é puxada por uma empresa extrema | `montar()` |
| **LLM** | Modelo de linguagem (Gemini). Escreve texto; aqui ele só escreve frases com marcadores | `raiox/ia.py` |
| **Prompt** | As instruções que mandamos ao LLM. São as regras da Náthally (`avaliacao/regras_prompt.md`) mais 3 notas do código | `regras()` em `ia.py` |
| **LangChain** | Biblioteca que liga o Python ao LLM: monta o prompt, chama a API e devolve o resultado | `_chain()` |
| **Saída estruturada** | O LLM devolve campos fixos (`resumo`, `perguntas`, `lacunas`), não um texto solto; isso usa Pydantic | classe `RaioX` |
| **Token** | Pedacinho de texto que a API cobra. Cada raio-x custa cerca de US$ 0,0012 | `gerar_llm()` |
| **Streamlit** | Biblioteca que transforma um script Python numa página web | `app/streamlit_app.py` |
| **Contrato** | Combinado do formato que uma parte entrega para outra (nomes de colunas, funções) | `contratos.md` |
| **Falso** | Arquivo "de mentira" no formato do contrato, para ninguém ficar parado esperando o colega | `falsos/` |
| **Teste (pytest)** | Código que confere outro código sozinho. `N passed` = as N conferências deram certo | `tests/` |
| **`.env`** | Arquivo com a chave secreta do Gemini. Fica só no seu computador, nunca no Git, nunca colado em chat | raiz |
| **Branch / PR** | Branch é sua cópia de trabalho; pull request (PR) é o pedido para juntar na `main`, que só entra com os testes do CI verdes | GitHub |
| **Docker** | "Caixa" que leva o programa com tudo que ele precisa, para rodar igual em qualquer computador | `Dockerfile` (a caixa da tela) |
| **Docker Compose** | Sobe várias caixas juntas com um comando: aqui, a tela e o PostgreSQL | `docker-compose.yml` |
| **Volume** | Pasta do seu computador que a caixa enxerga, sem copiar para dentro dela: é assim que a `data/` chega à tela | `docker-compose.yml` |
| **Terraform** | Arquivo que descreve a infraestrutura (a "caixa" e a porta) e cria tudo com um comando | **obrigatório** (`requisitos_projeto.MD`); feito na MG3: `infra/` (`terraform apply` sobe a tela e o banco) |

---

## 5. As pastas

```
raiox/          o cérebro (Python puro, sem tela)
  ia.py           monta os números, chama o Gemini, valida, preenche  ........ Eduardo
  segmentos.py    K-means + 5 parecidas  ...................................... Eduardo
  dados.py        busca empresas e registra consultas no PostgreSQL (contrato C1) .. Marcos
  checagem.py     regras que apontam números suspeitos; IA opcional só explica . Marcos
app/            a tela (Streamlit) e o tema  ................................. Miguel
scripts/        preparação dos dados da CVM (rodam 1 vez)  ................... Marcos
avaliacao/      medir se funciona: casos de teste, revisão, tempo, custo (C4)  Náthally + Eduardo
tests/          os testes automáticos
falsos/         tabela de 30 empresas inventadas + versões falsas de C1 e C3
docs/           estes textos e os gráficos (docs/graficos/)
infra/          o Terraform (*.tf: sobe a tela e o banco) e o script do banco de testes (infra/banco/) . Miguel
aprender/       guias, comandos, notebook e atalhos de dois cliques no Mac: configurar a chave, rodar testes, abrir a tela
data/           gerado por cada um; fora do Git
```

Arquivos da raiz: `README.md` (vitrine), `contratos.md` (formatos entre as partes), `REGRAS-IA.md`
(como o time usa IA), `CLAUDE.md` (contexto para o Claude Code), `requirements.txt` (bibliotecas), `.env.example`,
`Dockerfile` e `docker-compose.yml` (a tela e o PostgreSQL em contêineres).

**Regra das pastas:** cada pasta tem dono. Precisa mudar algo na pasta de outro? Fale com o dono antes.

---

## 6. Por dentro de `preparar_raio_x` (o coração)

Abra `raiox/ia.py` e siga junto. A função do contrato C3 faz quatro coisas:

1. **`montar()`**: acha a empresa e o grupo dela, calcula a mediana do grupo, decide a posição
   ("em linha" se a diferença for de até 3%), formata em português ("R$ 2,4 bi", "16,8%") e escreve a fonte.
   Ela devolve três coisas separadas:
   - `entrada`: vai para o LLM (setor, produto, objetivo, indicadores). **O nome da empresa não vai.**
   - `valores`: **nunca vai para o LLM**. É o dicionário marcador → valor real.
   - `extra`: o que a tela precisa (números para o gráfico, fontes, parecidas).
2. **`gerar_llm()`** chama o Gemini (ou **`texto_sem_ia()`** monta um texto fixo, sem custo, quando `usar_ia=False`).
3. **`validar_e_preencher()`** remove frase com dígito ou marcador desconhecido e troca os marcadores pelos valores.
4. Junta tudo num dicionário e devolve (o formato está no `contratos.md`, C3).

Experimente sem gastar nada:

```bash
python -m raiox.ia --cvm 90001 --produto "software de gestão de frota" --objetivo "primeira conversa" --sem-ia
```

---

## 7. Como rodar no seu computador

Pré-requisito: Python 3.14 e Git. Todos os comandos rodam na **pasta do repositório** (`trabalho-tcs`).

```bash
python3.14 -m venv .venv             # Windows: py -3.14 -m venv .venv (1 vez)
source .venv/bin/activate            # Mac/Linux   |   Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt  # com o ambiente ativo, python é o 3.14
python -m pytest -q                  # deve terminar com "passed" e nenhum "failed"
cd app && streamlit run streamlit_app.py     # abre a tela em http://localhost:8501
```

A tela abre com empresas inventadas (ALFA NORTE, BETA SUL...) e texto sem IA. Para o Gemini escrever:
copie `.env.example` para `.env`, cole a chave e rode `cd app && RAIOX_IA_REAL=1 streamlit run streamlit_app.py`.

Para gerar os dados reais (precisa de internet, alguns minutos):

```bash
python scripts/carregar_dfp.py       # baixa a CVM → data/contas.csv e o PostgreSQL
python scripts/indicadores.py        # → data/indicadores.csv
```

**Sem instalar Python nem PostgreSQL:** com o Docker instalado, `docker compose up -d --build` sobe a tela e o banco,
e `docker compose run --rm tela python -m pytest -q` roda os testes dentro do contêiner. Os outros comandos (carregar a CVM,
ligar a IA, desligar) estão no `aprender/COMANDOS.md`, seção 6.

> Integração conferida: a carga grava o PostgreSQL e os CSV; a tela busca empresas e registra consultas no PostgreSQL, enquanto o raio-x lê os indicadores do CSV. A EDA está em `notebooks/eda.ipynb`. O `seguindo-o-projeto.md` é uma fotografia histórica de 26/10, não o status atual.

---

## 8. Como trabalhar no Git sem quebrar nada

```bash
git switch main && git pull                 # 1. pegue a versão mais nova da main
git switch -c minha-tarefa                  # 2. crie sua branch a partir dela
# ... trabalhe ...
python -m pytest -q                         # 3. testes passando?
git status                                  # 4. leia a lista: nada de .env, nada de data/
git add arquivo1 arquivo2                   # 5. adicione só o que você mudou
git commit -m "o que mudou, em uma frase"
git push -u origin minha-tarefa             # 6. mande para o GitHub
gh pr create                                # 7. abra o pull request (ou pelo site)
```

O CI roda os testes no PR; com ele verde, quem abriu o PR faz o merge na `main` (o GitHub não deixa antes). No Claude Code,
o `/inicio-de-sessao` e o `/fim-de-sessao` fazem estes passos por você. **Nunca use `git push --force` na branch de outra pessoa.**

Por que criar a branch **a partir da `main`**: se a sua branch não tem a `main` como ponto de partida, o GitHub
não consegue juntar as duas ("não há história em comum"). Isso aconteceu com `tratamento_dados` e `feat/metricas`.

---

## 9. Como saber se algo é verdade (contra alucinação, nossa e da IA)

Valem para o que o ChatGPT, o Gemini, o Claude **ou um colega** disser sobre o projeto:

1. **Rode.** `python -m pytest -q` e abra a tela. Código que não rodou não está pronto.
2. **Peça a prova.** "Em que arquivo e linha?" Abra o arquivo e veja se está lá mesmo.
   Ferramenta: `grep -n "texto" arquivo.py` mostra a linha.
3. **Leia o que mudou** antes de aceitar: `git diff` (ou o painel de Controle de Código do VS Code).
4. **Confira números na fonte.** Pegue 2 ou 3 valores e compare com o site de RI da empresa
   (o Marcos já fez isso com a WEG: diferença 0,00%, arquivo `avaliacao/conferencia.csv`).
5. **Desconfie de:** número sem fonte, "deve funcionar", função que você nunca viu, resposta que muda quando você pergunta de novo.
6. **Separe "verifiquei" de "acho".** Nos nossos textos, quem afirma algo diz como conferiu.

---

## 10. Perguntas que a banca deve fazer (e o que a resposta precisa ter)

| Pergunta | A resposta precisa ter |
|---|---|
| Por que não RAG nem fine-tuning? | Os dados são tabelas da CVM, não textos: RAG buscaria texto que não temos e não garante número certo. Fine-tuning precisa de muitos exemplos rotulados e não resolve alucinação de número; o validador resolve |
| Como vocês garantem que a IA não inventa número? | Marcadores + validador + código preenche; mostrar o teste e a seção "Detalhes técnicos" na demo |
| Por que K-means e quantos grupos? | Não há resposta certa rotulada (não supervisionado); k escolhido pela silhueta; mostrar o gráfico `docs/graficos/silhueta.png` |
| E se a API do Gemini cair na demo? | Modo sem IA (mesma tela, texto fixo) e vídeo gravado |
| Quais os limites e vieses? | Só companhias abertas; bancos e seguradoras fora; dados anuais; grupos só por números; não é recomendação de investimento |
| Quanto custa e quanto economiza? | Custo por raio-x medido em tokens; tempo à mão × ferramenta medido pela Náthally |
| Onde está o Terraform (e o contêiner)? | O Terraform é **obrigatório** (`requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform"): dentro de `infra/`, `terraform apply` sobe a tela e o PostgreSQL (MG3), e o `terraform destroy` mantém o banco e a `data/`. O `Dockerfile` e o `docker-compose.yml` são a base: a `data/` entra como volume e a chave fica fora da imagem |
| Vocês têm backend e frontend? | Sim, como o professor combinou: a tela em Streamlit (frontend) e os módulos de `raiox/` (o que roda por trás) num contêiner, e o PostgreSQL em outro (`docker-compose.yml` e `infra/main.tf`) |
| Onde estão os prompts do vibecoding? | No README, seção "Prompts usados no vibecoding": `CLAUDE.md`, `AGENTS.md`, `REGRAS-IA.md`, `.claude/skills/` e o modelo de PR |
