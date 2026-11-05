# Justificativa técnica (ED8)

Por que o Raio-X usa **K-means + vizinhos** e **um LLM preso a marcadores**, e não RAG vetorial nem fine-tuning.
Atende:
- `guia_projeto_final.pdf` §6: "Justificativa técnica das escolhas de modelos/arquiteturas (ex.: RAG vs Fine-tuning)";
- `guia_projeto_final.pdf` §7: "motivos da escolha por RAG em relação ao Fine-tuning, e como configuraram as chains e a memória";
- `requisitos_projeto.MD`, "Integração com IA de terceiro": "base de dados de conhecimento para a IA utilizar".

Vai para o `documentacao.pdf` (MA6).

> Escrito em 02/11/2026 pelo Claude Code a partir do código. Cada afirmação tem arquivo e linha, conferidos no mesmo dia e revisados
> pelo `revisor` no PR #31. Responsável: Eduardo. "Pronto quando" (PLANO, ED8): o Marcos lê e entende.

## 1. O problema decide a arquitetura

O vendedor precisa de **números certos** (receita, margens, endividamento) e de **texto útil** (resumo, perguntas, lacunas).
Número errado numa reunião de vendas destrói a confiança no produto. Por isso a divisão de trabalho é:

| quem | faz | por quê |
|---|---|---|
| código (Pandas) | calcula todos os números a partir da DFP da CVM | cálculo é determinístico e auditável: cada número tem conta e ano (`raiox/ia.py:36-44`, coluna "fonte") |
| ML (scikit-learn) | acha o grupo de empresas parecidas e as 5 mais próximas | não há rótulo de "empresa parecida": é aprendizado não supervisionado |
| LLM (Gemini) | escreve o texto usando **marcadores** como `{margem_ebit}`, nunca o número | escrever é o que o LLM faz bem; copiar e arredondar número é onde ele erra |
| validador (código) | apaga o texto que tem número fora de marcador e troca cada marcador pelo valor calculado | é a **regra de ouro**: o LLM nunca escreve números (`raiox/ia.py:230`, `:248`) |

## 2. Machine learning: K-means + vizinhos mais próximos

- **Por que não supervisionado:** não existe uma coluna "grupo certo" para treinar. O K-means descobre os grupos sozinho.
- **Variáveis:** log da receita, crescimento em dois anos, margem EBIT, margem líquida e endividamento (`raiox/segmentos.py:38`).
  O log porque a receita vai de milhões a centenas de bilhões; sem ele, só o tamanho decidiria o grupo.
- **Preparo** (`matriz()`, `raiox/segmentos.py:65`):
  - extremos cortados nos percentis 5 e 95;
  - nulos preenchidos com a mediana;
  - `StandardScaler`, para todas as colunas ficarem na mesma régua.
- **Treino só com receita ≥ R$ 10 mi** (`raiox/segmentos.py:35`): holdings e empresas sem operação distorciam os grupos.
- **Escolha do k** (`raiox/segmentos.py:90-95`; regra em `escolher_k()`, `:76`):
  - testa k de 3 a 8;
  - fica com a maior silhueta, **mas só entre os k em que o menor grupo tem pelo menos 5% das empresas**.
- **Lição para a banca:** antes do ED4, a silhueta era 0,77 e parecia ótima, mas só separava 9 empresas extremas e juntava todas as
  outras num grupo só (`docs/HISTORICO.md`, "O que aprendemos"; `raiox/segmentos.py:78`). Com a regra dos 5%, saem 4 grupos e silhueta 0,30. Com os dados do PR #46 (recarregados em 05/11),
  0,29 e grupos de 60, 77, 100 e 327 empresas no treino (`docs/REQUISITOS.md`, R5).
  Silhueta menor, grupos úteis. Os gráficos de antes e depois são `docs/graficos/silhueta_antes_ed4.png` e `silhueta.png`
  (refeito em 05/11: 0,29 em k = 4).
- **5 empresas parecidas:** `NearestNeighbors` com 6 vizinhos, porque o 1º vizinho é a própria empresa e sai da lista
  (`raiox/segmentos.py:97-103`).

## 3. IA generativa: por que nem RAG vetorial nem fine-tuning

**De onde a IA tira o conhecimento.** A base é a tabela de indicadores calculada da DFP da CVM pelos scripts do Marcos
(`data/indicadores.csv`, com o grupo e as parecidas do `data/segmentos.csv`; lida em `raiox/ia.py:52-54`).
O código busca a linha exata da empresa pelo código CVM (`montar()`, `raiox/ia.py:74`) e entrega ao Gemini, para cada indicador
(`raiox/ia.py:99`):
- o nome;
- o valor da empresa e a mediana do grupo, já formatados (ex.: "R$ 12,3 bi");
- a posição, "acima", "abaixo" ou "em linha", calculada por código.

O Gemini **lê** esses valores para entender a empresa, mas **só pode escrever os marcadores**. Os números do texto final são colocados
pelo código, e o validador apaga o que tiver número escrito pelo modelo.
Isso é geração aumentada por recuperação, mas a recuperação é **estruturada** (pela chave da empresa), e não semântica (por embeddings).
O PostgreSQL guarda as contas da DFP (tabelas `contas` e `empresas`, `scripts/carregar_dfp.py:146,155`) e serve à busca de empresas
(`raiox/dados.py`); a tela usa o banco desde a MG4 (PR #36, 02/11).

Se isso conta como a "base de dados de conhecimento" que o `requisitos_projeto.MD` pede, é a pergunta 3 ao professor, ainda sem
resposta (`docs/REQUISITOS.md`). O projeto também segue o caminho "Treinamento de Machine Learning" (seção 2), que fica completo quando a EDA entrar (MA4, REQUISITOS R4).

| opção | o que seria | por que não usamos |
|---|---|---|
| RAG vetorial | quebrar documentos em pedaços, gerar embeddings e buscar os trechos mais parecidos com a pergunta | os dados são números em tabela, não texto. Busca por semelhança pode trazer a empresa ou o ano errado; busca por chave traz sempre a linha certa. Também exigiria um banco vetorial a mais para manter |
| Fine-tuning | treinar o modelo com exemplos de raio-x bons | não temos centenas de exemplos rotulados; custa mais; os dados mudam todo ano (DFP nova); e treinar **não impede** o modelo de errar número, que é o risco principal |
| **O que usamos** | prompt + saída estruturada (Pydantic) + validador | barato (≈ US$ 0,0012 por raio-x), reproduzível e conferível. Nos 10 casos do ED7: 10 raio-x gerados, 0 trechos removidos pelo validador, US$ 0,0118 no total e 2,2 s em média (`avaliacao/resultados.csv`) |

**Quando RAG passaria a valer:** se o raio-x tivesse de ler texto livre, como o release de resultados ou as notas explicativas
da DFP. Ficou fora do escopo (`docs/PLANO.md`, seção 7).

## 4. Chain, memória e agentes no LangChain

- **Uma chain só, de dois passos** (`_chain()`, `raiox/ia.py:165`):
  1. `ChatPromptTemplate`, com as regras como `SystemMessage` e o pedido;
  2. `ChatGoogleGenerativeAI(...).with_structured_output(RaioX)`.
- **Saída estruturada:** a resposta volta no formato `RaioX` (resumo, perguntas e lacunas; `raiox/ia.py:113-125`).
  O Pydantic garante esse formato. As quantidades (3 a 5 perguntas, 2 a 4 lacunas) vão como instrução ao modelo e não são impostas por código.
- **O prompt de sistema** (`regras()`, `raiox/ia.py:141-144`) é o arquivo de regras da Náthally (`avaliacao/regras_prompt.md`, lido sem
  cópia) mais 3 notas do código (`NOTAS_DO_CODIGO`). Assim, o que ela escreve chega inteiro ao Gemini.
- **Modelo:** `gemini-3.1-flash-lite` (`raiox/ia.py:28`). A tarefa é escrever 3 frases e algumas perguntas: um modelo pequeno
  basta e custa menos. `temperature=0.2` dá pouca variação entre uma chamada e outra (`raiox/ia.py:161`).
- **Limites:** 15 s por tentativa e 2 tentativas (`raiox/ia.py:32-33`). Se a API travar, o erro chega em uns 30 s, e a tela não fica
  girando sem fim.
- **Sem memória, de propósito:** cada raio-x é independente (uma empresa, um produto, um objetivo). Memória de conversa só traria
  risco de misturar dados de uma empresa na outra.
- **Sem agente, de propósito:** o caminho é sempre o mesmo (buscar → calcular → escrever → validar), então não há decisão para um
  agente tomar. Um pipeline fixo é mais previsível e mais fácil de testar.
- **Plano B sem IA:** `texto_sem_ia()` (`raiox/ia.py:186`) monta o texto por modelo fixo, com os mesmos marcadores e o mesmo validador.
  A demo funciona sem a chave do Gemini (sem `RAIOX_IA_REAL`).

## 5. Segurança (a parte técnica; a análise de ética é a NA5, da Náthally)

- **O modelo não escreve número:**
  - o validador barra algarismos de qualquer escrita (inclusive ½ e ²), números por extenso ("dez", "o dobro") e marcadores
    inventados (`checar()`, `raiox/ia.py:230-240`);
  - se o resumo tiver um número, ele sai inteiro; perguntas e lacunas saem uma a uma (`raiox/ia.py:248-281`);
  - tudo o que sai fica registrado em `removidos`, que aparece na tela;
  - testes: `test_validador_*` e `test_regra_de_ouro_*`, em `tests/test_raio_x.py`.
- **Chave do Gemini** só no `.env`, que não vai para o Git (`.gitignore`). No Terraform, o `.env` é montado só para leitura e a chave
  não passa por variável, então não fica no `terraform.tfstate` (`infra/main.tf:123-130`; conferido pelo Miguel no PR #29).
  Ponto fraco: a senha do PostgreSQL local passa por variável (`var.senha_banco`, padrão `postgres`; `infra/main.tf:112-113`) e fica no
  `terraform.tfstate`. Ele não vai para o Git, e o banco só abre em `127.0.0.1`.
- **Não é recomendação de investimento:** o aviso aparece na tela (`app/streamlit_app.py:187-188`).

## 6. Perguntas prováveis da banca (respostas curtas)

| pergunta | resposta |
|---|---|
| Por que não RAG? | Os dados são números em tabela: buscar pela chave da empresa é exato, e busca semântica poderia trazer a empresa errada. A recuperação existe, mas é estruturada. |
| Por que não fine-tuning? | Faltam exemplos rotulados, custa mais, os dados mudam todo ano, e não resolve o risco principal (número errado). O validador resolve. |
| Como vocês sabem que a IA não inventa número? | Ela pode ler os valores, mas só pode escrever marcadores. Os números do texto são colocados pelo código, e se ela escrever um dígito o validador apaga o trecho. Nos 10 casos reais, 0 trechos removidos. |
| Por que a silhueta é só 0,29? | Porque a de 0,77 enganava: separava 9 extremas e juntava todo o resto. Preferimos grupos úteis a um número bonito. |
| Qual a memória do agente? | Não há agente nem memória, de propósito: cada raio-x é independente e o caminho é fixo. |
| E se a API do Gemini cair na demo? | A tela monta o texto sem IA, com os mesmos números e o mesmo validador, e mostra um aviso (`app/streamlit_app.py:49-55`, MG4). Conferido em 03/11 com uma chave inválida: WEG gerada sem IA e consulta gravada com custo 0. |
