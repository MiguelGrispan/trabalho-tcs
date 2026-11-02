# Justificativa técnica (ED8)

Por que o Raio-X usa **K-means + vizinhos** e **um LLM preso a marcadores**, e não RAG vetorial nem fine-tuning.
Atende: `guia_projeto_final.pdf` §6 ("Justificativa técnica das escolhas de modelos/arquiteturas (ex.: RAG vs Fine-tuning)")
e §7 ("motivos da escolha por RAG em relação ao Fine-tuning, e como configuraram as chains e a memória"); `requisitos_projeto.MD`,
"Integração com IA de terceiro" ("base de dados de conhecimento para a IA utilizar"). Vai para o `documentacao.pdf` (MA6).

> Rascunho de 02/11/2026: o Claude Code escreveu a partir do código, e cada afirmação tem o arquivo e a linha.
> O Eduardo revisa e reescreve com as palavras dele antes do merge. "Pronto quando" (PLANO, ED8): o Marcos lê e entende.

## 1. O problema decide a arquitetura

O vendedor precisa de **números certos** (receita, margens, endividamento) e de **texto útil** (resumo, perguntas, lacunas).
Número errado numa reunião de vendas destrói a confiança no produto. Por isso a divisão de trabalho é:

| quem | faz | por quê |
|---|---|---|
| código (Pandas, SQL) | calcula todos os números a partir da DFP da CVM | cálculo é determinístico e auditável: cada número tem conta e ano (`raiox/ia.py:36-44`, coluna "fonte") |
| ML (scikit-learn) | acha o grupo de empresas parecidas e as 5 mais próximas | não há rótulo de "empresa parecida": é aprendizado não supervisionado |
| LLM (Gemini) | escreve o texto, usando **marcadores** como `{margem_ebit}` no lugar dos números | escrever é o que o LLM faz bem; contar e copiar número é o que ele faz mal |
| validador (código) | remove qualquer frase com número fora de marcador e troca os marcadores pelos valores | é a **regra de ouro**: o LLM nunca escreve números (`raiox/ia.py:230`, `:248`) |

## 2. Machine learning: K-means + vizinhos mais próximos

- **Por que não supervisionado:** não existe uma coluna "grupo certo" para treinar. O K-means descobre os grupos sozinho
  (`raiox/segmentos.py:91`).
- **Variáveis:** log da receita, crescimento em dois anos, margem EBIT, margem líquida e endividamento (`raiox/segmentos.py:38`).
  O log porque a receita vai de milhões a centenas de bilhões; sem ele, só o tamanho decidiria o grupo.
- **Preparo** (`matriz()`, `raiox/segmentos.py:65`): extremos cortados nos percentis 5 e 95, nulos com a mediana e `StandardScaler`
  (todas as colunas na mesma régua).
- **Treino só com receita ≥ R$ 10 mi** (`raiox/segmentos.py:35`): holdings e empresas sem operação distorciam os grupos.
- **Escolha do k** (`escolher_k()`, `raiox/segmentos.py:76`): testa k de 3 a 8 e fica com a maior silhueta **entre os k em que o menor
  grupo tem pelo menos 5% das empresas**.
- **Lição para a banca:** antes do ED4, a silhueta era 0,77 e parecia ótima, mas só separava 9 empresas extremas e deixava as outras
  num grupo só. Depois da regra dos 5%: k = 4 e silhueta ≈ 0,29 (`docs/HISTORICO.md`, 28/10; `docs/PLANO.md`, seção 0).
  Silhueta menor, grupos úteis. Gráficos: `docs/graficos/silhueta_antes_ed4.png` × `silhueta.png`.
- **5 empresas parecidas:** `NearestNeighbors` com 6 vizinhos, porque o 1º vizinho é a própria empresa (`raiox/segmentos.py:97`).

## 3. IA generativa: por que nem RAG vetorial nem fine-tuning

**A nossa "base de conhecimento" é a tabela da CVM no PostgreSQL.** O código busca a linha exata da empresa pelo código CVM
(`montar()`, `raiox/ia.py:74`) e entrega ao Gemini só os nomes dos indicadores e a posição de cada um contra o grupo
("acima", "abaixo", "em linha"). Isso é geração aumentada por recuperação, mas a recuperação é **estruturada** (por chave),
não semântica (por embeddings).

| opção | o que seria | por que não usamos |
|---|---|---|
| RAG vetorial | quebrar documentos em pedaços, gerar embeddings e buscar os trechos mais parecidos com a pergunta | os dados são números em tabela, não texto. Busca por semelhança pode trazer a empresa ou o ano errado; busca por chave traz sempre a linha certa. Também exigiria um banco vetorial a mais para manter |
| Fine-tuning | treinar o modelo com exemplos de raio-x bons | não temos centenas de exemplos rotulados; custa mais; os dados mudam todo ano (DFP nova); e treinar **não impede** o modelo de errar número, que é o risco principal |
| **O que usamos** | prompt das regras da Náthally + saída estruturada (Pydantic) + validador | barato (≈ US$ 0,0012 por raio-x), reproduzível e conferível: nos 10 casos do ED7, 0 erros e 0 frases removidas, US$ 0,0118 no total (`avaliacao/resultados.csv`) |

**Quando RAG passaria a valer:** se o raio-x tivesse de ler texto livre, como o release de resultados ou as notas explicativas
da DFP. Ficou fora do escopo (`docs/PLANO.md`, seção 7).

## 4. Chain, memória e agentes no LangChain

- **Uma chain só, de dois passos** (`_chain()`, `raiox/ia.py:165`):
  `ChatPromptTemplate` (regras da Náthally como `SystemMessage` + o pedido) `|` `ChatGoogleGenerativeAI(...).with_structured_output(RaioX)`.
  A saída já vem no formato `RaioX` (resumo, 3 a 5 perguntas, 2 a 4 lacunas), validado pelo Pydantic (`raiox/ia.py:113-125`).
- **O prompt não tem cópia:** `regras()` lê `avaliacao/regras_prompt.md`, o arquivo da Náthally (`raiox/ia.py:141`). O que ela escreve é
  exatamente o que o Gemini recebe.
- **Modelo:** `gemini-3.1-flash-lite` (`raiox/ia.py:28`): é a tarefa de escrever 3 frases e algumas perguntas, então um modelo pequeno
  basta e custa menos. `temperature=0.2`: pouca variação entre uma chamada e outra (`raiox/ia.py:161`).
- **Limites:** 15 s por tentativa e 2 tentativas (`raiox/ia.py:32-33`). Se a API travar, o erro chega em uns 30 s, e não com a tela
  girando na banca.
- **Sem memória, de propósito:** cada raio-x é independente (uma empresa, um produto, um objetivo). Memória de conversa só traria
  risco de misturar dados de uma empresa na outra.
- **Sem agente, de propósito:** o caminho é sempre o mesmo (buscar → calcular → escrever → validar), então não há decisão para um
  agente tomar. Um pipeline fixo é mais previsível e mais fácil de testar.
- **Plano B sem IA:** `texto_sem_ia()` (`raiox/ia.py:186`) monta o texto por modelo fixo, com os mesmos marcadores e o mesmo validador.
  A demo funciona sem a chave do Gemini.

## 5. Segurança (a parte técnica; a análise de ética é a NA5, da Náthally)

- **Os valores nunca vão para o LLM** (`raiox/ia.py:109`): o Gemini recebe "acima" ou "abaixo", não o número.
- **Validador:** barra algarismos de qualquer escrita (inclusive ½ e ²), números por extenso ("dez", "o dobro") e marcadores
  inventados (`raiox/ia.py:230-240`). Testes: `test_validador_*` e `test_regra_de_ouro_*` em `tests/test_raio_x.py`.
- **Chave do Gemini e senha do banco** só no `.env`, que não vai para o Git (`.gitignore`). Na infraestrutura, o `.env` é montado só para
  leitura e a chave não fica no estado do Terraform (`docs/PLANO.md`, seção 0, PR #29).
- **Não é recomendação de investimento:** o aviso aparece na tela (`app/streamlit_app.py`).

## 6. Perguntas prováveis da banca (respostas curtas)

| pergunta | resposta |
|---|---|
| Por que não RAG? | Os dados são números em tabela: buscar pela chave da empresa é exato, e busca semântica poderia trazer a empresa errada. A recuperação existe, mas é estruturada. |
| Por que não fine-tuning? | Faltam exemplos rotulados, custa mais, os dados mudam todo ano, e não resolve o risco principal (número errado). O validador resolve. |
| Como vocês sabem que a IA não inventa número? | Ela nunca vê os números. Se escrever um dígito, o validador apaga a frase. Nos 10 casos reais, 0 frases removidas. |
| Por que a silhueta é só 0,29? | Porque a de 0,77 enganava: separava 9 extremas e juntava todo o resto. Preferimos grupos úteis a um número bonito. |
| Qual a memória do agente? | Não há agente nem memória, de propósito: cada raio-x é independente e o caminho é fixo. |
| E se a API do Gemini cair na demo? | Em uns 30 s a tela recebe o erro; o modo sem IA gera o raio-x com os mesmos números e o mesmo validador. |
