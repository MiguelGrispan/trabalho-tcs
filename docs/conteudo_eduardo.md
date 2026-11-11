---
tags: [projeto-tcs, apresentacao]
data: "07/11/2026"
---

# Eduardo: conteúdo para os slides e a defesa

Ficha para a Náthally montar o deck. Números da avaliação de 05/11 e do [documento do projeto](documentacao.md), seções 6–8. Não é o deck final nem registro de ensaio concluído.

## 1. Dois slides técnicos

### Slide 1 — Como o ML ajuda o vendedor

**Na tela do slide:**
- K-means agrupa empresas pelo perfil financeiro; vizinhos sugerem cinco empresas parecidas.
- Quatro grupos; silhueta de 0,286: os perfis se sobrepõem.
- Limite: os dez casos avaliados caíram no mesmo grupo; parecida não significa concorrente.

**Fala sugerida (30–45 s; cronometrar no ensaio):**
“Partimos dos indicadores calculados com dados públicos da CVM. O K-means cria grupos por perfil financeiro, e os vizinhos mais próximos sugerem empresas para prospectar. Escolhemos quatro grupos pelas regras do treino e pela silhueta. A silhueta de 0,286 mostra que os grupos se sobrepõem. Nos nossos dez casos, todas as empresas ficaram no maior grupo. Por isso, tratamos a comparação como apoio exploratório, com limites, e não como classificação exata ou lista de concorrentes.”

**Prova:** [segmentos.py](../raiox/segmentos.py), `treino()`, `matriz()`, `escolher_k()` e `segmentar()`; [justificativa](justificativa.md), seção 2; [limite conhecido #60](https://github.com/MiguelGrispan/trabalho-tcs/issues/60).

### Slide 2 — Como controlamos a IA generativa

**Na tela do slide:**
- Gemini via LangChain escreve o texto com marcadores; o código insere os valores da tabela.
- O validador barra números fora de marcadores; se a API falhar, há texto sem IA.
- Dez casos: nenhum trecho removido; geração média de 2,15 s. A conferência numérica é separada.

**Fala sugerida (30–45 s; cronometrar no ensaio):**
“A IA recebe os indicadores e o contexto da reunião para escrever perguntas. Ela usa marcadores no lugar dos números. O validador verifica esses marcadores e barra trechos com números fora deles; depois, o código insere os valores. Se a API falhar, a aplicação continua com texto sem IA e avisa. Nos dez casos, não houve trecho removido e a geração levou em média 2,15 segundos. Isso não prova que o texto é sempre correto: afirmações falsas sem números ainda podem passar, então a revisão humana continua necessária.”

**Prova:** [ia.py](../raiox/ia.py), `gerar_llm()`, `checar()`, `validar_e_preencher()` e `preparar_raio_x()`; [resultados dos dez casos](../avaliacao/resultados.csv); [ética](etica.md), seções 1–2.

## 2. Defesa: respostas curtas para treinar

Treino sugerido: 15 min, energia média. Primeiro passo: responder a primeira pergunta em voz alta, sem olhar a resposta.

<details>
<summary>Por que K-means e como os dados entram nele?</summary>

Para comparar perfis sem rótulos prontos. O treino usa empresas com receita a partir de R$ 10 milhões, receita em log, extremos cortados nos percentis 5/95, mediana para nulos e padronização. A receita em log reduz a diferença de escala; a padronização evita que uma variável domine pela unidade. Fonte: `treino()` e `matriz()`, [segmentos.py](../raiox/segmentos.py).
</details>

<details>
<summary>Por que a silhueta antiga de 0,77 era enganosa?</summary>

Separava um pequeno grupo de empresas extremas, deixando quase todas juntas. As regras de receita, extremos e tamanho mínimo de grupo melhoraram a utilidade da comparação, mesmo com silhueta menor. Não vamos retreinar antes da banca. Fonte: [justificativa](justificativa.md), seção 2.
</details>

<details>
<summary>O que o PCA mostra? Ele cria os grupos?</summary>

O PCA projeta as variáveis em dois eixos para desenhar o gráfico. Os grupos são criados pelo K-means na matriz de variáveis, antes dessa projeção. O desenho perde parte da informação; não comprova separação perfeita. Fonte: `grafico_grupos()`, [segmentos.py](../raiox/segmentos.py).
</details>

<details>
<summary>Por que não usar RAG vetorial, fine-tuning ou um agente?</summary>

Os indicadores são recuperados pela chave exata da empresa. Não precisamos de busca semântica para localizar números nem de decisões autônomas: o caminho é fixo, com prompt e saída estruturada. Fine-tuning também não garantiria números corretos. Fonte: [justificativa](justificativa.md), seções 3–4. Se essa tabela satisfaz a expressão “base de conhecimento” do professor ainda é uma pergunta externa; não afirmamos que ele já aceitou.
</details>

<details>
<summary>O validador garante que a resposta inteira está correta?</summary>

Não. Ele verifica números e marcadores, mas não entende todas as afirmações. Um marcador válido no indicador errado, uma hipótese falsa sem números ou “acima” trocado por “abaixo” no texto podem passar. Os cartões usam a posição calculada por código. Fonte: [ética](etica.md), seção 2.
</details>

<details>
<summary>O LLM recebe valores? Ele pode calcular ou escrever novos números?</summary>

Recebe indicadores já formatados no contexto. O dicionário de substituição `valores` fica no código. A saída deve conter marcadores; o código valida e preenche. Não diga que o modelo nunca vê números. Fonte: `montar()`, `_prompt()` e `preparar_raio_x()`, [ia.py](../raiox/ia.py).
</details>

<details>
<summary>Qual é o resultado medido? Já podemos afirmar o ROI?</summary>

Dez casos, nenhum trecho removido e 2,15 s por geração, incluindo montagem, Gemini e validação. O “8 de 10” compara os seis indicadores com a conferência manual; as diferenças de Magalu e RD Saúde envolvem definições contábeis. Não é taxa geral de acerto do LLM. O tempo para digitar, ler e conferir também conta no uso real. Sem medição manual comparável, ainda não há ganho de tempo ou ROI comprovado. Fonte: [documento](documentacao.md), seções 7.4 e 8.
</details>

<details>
<summary>Por que a demo continua se o Gemini falhar?</summary>

O cliente da API tem limite de tempo e tentativas. A tela captura a falha e usa texto sem IA, mantendo os indicadores e avisando a origem. No ensaio técnico de 07/11, uma falha simulada preservou a geração e o registro da consulta no banco; não houve chamada paga. Fonte: `_llm()`, [ia.py](../raiox/ia.py), e `gerar_raio_x()`, [tela](../app/streamlit_app.py).
</details>

**Estado:** conteúdo técnico preparado. Faltam a Náthally incorporá-lo ao deck e o Eduardo ensaiar em voz alta.
