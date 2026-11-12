# Governança, ética e uso responsável da IA

Atende:
- `guia_projeto_final.pdf` §2: "Avaliação explicativa sobre viabilidade, limitações, viés, confiabilidade e uso responsável da IA adotada";
- `guia_projeto_final.pdf` §5 (peso 15%): "riscos de viés, alucinação, segurança de dados e uso ético da solução";
- `guia_projeto_final.pdf` §6: "análise de ética e segurança", no PDF (MA6).

> **Texto final da Náthally (NA5, 12/11/2026)**, sobre a base técnica escrita em 03/11 pelo Claude Code a partir do código (cada
> afirmação tem arquivo e linha). Levado ao repositório pelo Eduardo, com o Claude Code, em 12/11: só links e um detalhe do Magalu.
> A parte de segurança técnica (chave, senha, validador) já está em [justificativa.md](justificativa.md), seção 5, e não se repete aqui.
>
> **Atualizado em 12/11/2026:** a seção 4 (confiabilidade dos dados) foi revisada e a seção 6 (viabilidade de negócio, a partir do [roi.md](produto/roi.md)) foi adicionada.

## 1. O risco principal e como foi tratado: número inventado

| risco | o que fizemos | prova |
|---|---|---|
| O LLM inventa ou arredonda um número (alucinação) e o vendedor leva um dado falso para a reunião | o LLM só escreve marcadores como `{margem_ebit}`; o código coloca os valores; o validador apaga o trecho com algarismo, número por extenso ou marcador inventado | `checar()` e `validar_e_preencher()`, `raiox/ia.py:230-282`; testes `test_validador_*` e `test_regra_de_ouro_*` em `tests/test_raio_x.py` |
| Resultado medido | 10 raio-x reais: 0 trechos removidos, US$ 0,0012 cada, 2,2 s em média | `avaliacao/resultados.csv` (ED7, PR #20) |

## 2. Alucinação que o validador **não** pega

O validador barra números, não ideias. Continuam possíveis:
- **pergunta enviesada ou com suposição falsa:** ex.: "como a gestão avalia o impacto dos custos na margem EBIT?" supõe que os custos
  são o problema; a margem pode ser baixa por outro motivo;
- **"acima" ou "abaixo" trocado no texto:** a posição é calculada por código e entregue ao modelo (`montar()`, `raiox/ia.py:74`),
  mas a palavra na frase é o LLM que escreve, e o validador não confere. O que protege: a regra 4 do prompt
  (`avaliacao/regras_prompt.md`) e o cartão de cada indicador na tela, que mostra a posição calculada pelo código;
- **lacuna genérica:** "pessoas que decidem a compra" serve para qualquer empresa;
- **interpretação de setor:** o modelo pode associar a empresa a um negócio que ela não tem.

O que reduz o risco: as regras do prompt proíbem palavras de intensidade e lacuna em forma de pergunta
(`avaliacao/regras_prompt.md`, lido por `regras()`, `raiox/ia.py:141`); `temperature=0.2` (`raiox/ia.py:161`); cada pergunta
traz a "base", o indicador que a motivou, visível na tela. **O que não resolve:** só a leitura humana. Por isso a seção 5.

## 3. Viés e limites do modelo de ML (K-means + vizinhos)

- **Só companhias abertas:** a base é a DFP da CVM. Empresa de capital fechado, pequena ou média, não aparece. A ferramenta
  serve para vender a grandes contas, não para qualquer cliente.
- **Treino só com receita a partir de R$ 10 mi** (`RECEITA_MINIMA`, `raiox/segmentos.py:35`): abaixo disso, 31 empresas, 52% com
  margem EBIT acima de 100% em valor absoluto (holdings, sem operação), segundo o `scripts/avaliar_corte_receita.py` (rodado pelo Marcos em 03/11, com os dados do PR #46; `docs/REQUISITOS.md`, R5). Essas empresas
  **recebem um grupo mesmo assim**, o mais próximo, sem terem ajudado a formá-lo (`segmentar()`, `raiox/segmentos.py:83-95`).
  Para elas, a comparação com o grupo é menos confiável. E elas também entram na mediana e no tamanho do grupo mostrados na tela
  (ex.: o grupo da WEG tem 330 empresas na tela, mais que no treino).
- **Extremos cortados nos percentis 5 e 95** (`CORTE`, `raiox/segmentos.py:36`): só para o modelo; os números mostrados são os reais.
  Uma empresa muito fora da curva fica num grupo que não a representa bem.
- **Grupo por perfil financeiro, não por setor:** as 5 variáveis são receita, crescimento, margens e endividamento
  (`VARIAVEIS`, `raiox/segmentos.py:38`). Ex.: a WEG (máquinas e equipamentos; números 100% iguais ao RI em
  `avaliacao/conferencia.csv`) tem como parecidas Cemig, Copel, Axia (energia), Votorantim Cimentos e Telefônica: empresas grandes,
  rentáveis e pouco endividadas, mas de outros setores (raio-x sem IA, 03/11). Isso é útil para prospectar perfis parecidos, mas não é "concorrente".
  A tela precisa dizer isso (sugestão para a NA5 e o deck).
- **Silhueta 0,29:** os grupos se sobrepõem. É uma régua de comparação, não uma classificação exata
  ([justificativa.md](justificativa.md), seção 2, explica por que 0,77 enganava).

## 4. Confiabilidade dos dados

- **Dado de até um ano atrás:** a DFP é anual (`scripts/indicadores.py:60`, último ano disponível). Resultado do trimestre não entra.
- **Acerto contra o RI: 7 de 10, e 8 de 10 depois de rodar de novo,** na conferência manual (29/10; o `revisao_manual.md` está na branch
  `feat/metricas`, ainda não na `main`). Na MA3 (PR #46, 03/11), 1 das 3 diferenças foi a Camil, um erro de organização de dados (ano fiscal de março a
  fevereiro, issue #17), corrigido. Ao rodar de novo em 05/11, persistiu uma discrepância em Magalu e RD Saúde: o sistema bate com a DFP, e a diferença veio do
  critério usado na conferência. Na RD Saúde, foi usada a tabela "Pré-IFRS 16" do Relatório da Administração da DFP 2025; no Magalu,
  outra conta do EBIT (sem as perdas de crédito e a equivalência patrimonial; documento, seção 7.4). Não foi um erro, e sim
  uma divergência na base considerada.
- **Fonte em cada número:** cada indicador mostra a conta da DFP de onde veio (coluna "fonte", `raiox/ia.py:36-44`), para o vendedor
  conferir. Desde 10/11, a tela também traz uma tabela das fontes e um zip com a DFP, para conferir dentro da própria aplicação.

## 5. Uso responsável

- **Apoio, não decisão:** o raio-x prepara a primeira reunião. O vendedor confere antes de usar; o aviso está na tela
  ("Confira antes de usar...", `app/streamlit_app.py:187`).
- **Não é recomendação de investimento** (mesmo aviso, `app/streamlit_app.py:187`).
- **Dados públicos e de empresas, não de pessoas:** a DFP é publicada pela CVM. O sistema não guarda dado pessoal de cliente;
  a tabela `consultas` grava empresa, produto, objetivo, tempo e custo (`raiox/dados.py`, `registrar_consulta`).
  Atenção: o produto e o objetivo são texto livre; o vendedor não deve escrever nome de pessoa ou dado sigiloso ali.
- **O que vai para o Gemini:** o setor, os indicadores já formatados com a posição no grupo, o tamanho do grupo, o produto e o
  objetivo. Nem o nome da empresa vai (`entrada`, `raiox/ia.py:102-103`).
- **Se a IA falhar, a ferramenta continua:** a tela monta o texto sem IA, com os mesmos números, e avisa. Conferido em 03/11 com uma
  chave inválida (erro na hora; o caso de rede travada, ~30 s, só tem teste: `test_gemini_desiste_rapido_se_a_api_travar`) no `docker compose`: WEG gerada sem IA, aviso na tela, consulta gravada com custo 0 (`app/streamlit_app.py:49-55`).
- **Custo baixo e acompanhado:** ≈ US$ 0,0012 por raio-x. Não há limite de chamadas na tela; o controle é uma combinação do time
  (mais de 10 chamadas, o grupo é avisado: `CLAUDE.md`, "Cuidados").

## 6. Viabilidade de negócio (ROI, NA3)

Detalhes, fórmulas e premissas em [roi.md](produto/roi.md). Aqui, o resumo para a banca.

> **Aviso:** todos os números abaixo são **estimativas baseadas em uma única entrevista** (um diretor comercial de tecnologia e
> software, mais de 10 anos de B2B). Não representam a média dos vendedores B2B. O perfil (diretor) também difere da persona
> (executivo de contas).

### 6.1 Custo

- **Custo por raio-x:** US$ 0,0011847 de IA (média de 10 casos, 2.262 tokens de entrada e 413 de saída, `gemini-3.1-flash-lite`;
  `avaliacao/resultados.csv`). Com a PTAX de 11/11/2026 (R$ 5,5606 por US$ 1), são **R$ 0,006588 por raio-x**.
- **Custo mensal da IA:** 8 raio-x por mês (um por primeira reunião) = **R$ 0,0527**, cerca de 5 centavos.
- **Custo fixo:** zero hoje (Docker e Terraform rodam na máquina do time). O custo de um servidor em uso real **não foi estimado**.

### 6.2 Tempo e economia

| item | valor | origem |
|---|---|---|
| Primeiras reuniões por mês | 8 (faixa de 6 a 10) | entrevista, ponto médio |
| Preparação hoje, sem o Raio-X | 45 min (faixa de 30 a 60) | entrevista, ponto médio; tempo **declarado, não medido**; o entrevistado já usa IA "quase sempre" e diz verificar os resultados |
| Com o Raio-X, cenário A (conferindo as fontes) | 17,5 min (faixa de 15 a 20) | faixa cronometrada; a conta usa o ponto médio |
| Com o Raio-X, cenário B (sem conferir as fontes) | 12,5 min (faixa de 10 a 15) | faixa cronometrada; a conta usa o ponto médio |
| Custo da hora | R$ 59,52 / R$ 74,40 / R$ 89,29 | salário de R$ 10 mil a R$ 15 mil ÷ 168 h (informado pelo entrevistado) |

Resultado com o custo médio da hora (R$ 74,40):

| | cenário A (com conferência) | cenário B (sem conferência) |
|---|---|---|
| Economia por reunião | 27,5 min | 32,5 min |
| Horas economizadas por mês | 3,67 h | 4,33 h |
| Economia por mês | **R$ 272,82** | **R$ 322,42** |
| ROI (economia ÷ R$ 0,0527) | 5.177 vezes | 6.118 vezes |

- **O cenário A é o recomendado e o mais próximo do comportamento do entrevistado:** ele diz que verifica o que a IA entrega e que
  só confiaria nos números se pudesse conferir a fonte. Conferir as fontes custa cerca de 5 minutos por reunião (R$ 49,60 por
  mês) e preserva cerca de 85% da economia do cenário B. Isso une a viabilidade ao uso responsável da seção 5: a economia
  que a banca deve ouvir é a do cenário A.
- **Faixa de sensibilidade (cenário A):** de R$ 74,40 por mês (pior caso: 30 min hoje, 6 reuniões) a R$ 558,04 por mês (melhor
  caso: 60 min hoje, 10 reuniões). ROI de 1.882 a 8.471 vezes.
- **Ponto de equilíbrio:** a ferramenta se paga se economizar cerca de 0,3 segundo por raio-x.
- **Como ler o ROI:** um ROI de milhares de vezes vem do custo da API ser ínfimo, e não de um ganho enorme. O número mais
  informativo é a economia de **cerca de 3,7 a 4,3 horas por mês (R$ 273 a R$ 322) por executivo**.
- **Evidência qualitativa (não entra na conta):** o entrevistado deu nota 5 de 5 para a utilidade do exemplo, e a parte
  mais útil seria as perguntas para a reunião.

### 6.3 Limites da viabilidade

- **Um único entrevistado:** tempo atual e reuniões por mês vêm de faixas marcadas por uma pessoa; os pontos médios são premissas.
- **Tempo atual declarado, não medido.**
- **O ROI não inclui** desenvolvimento, servidor em uso real nem encargos trabalhistas (FGTS, férias, 13º). Sem os encargos, o
  custo da hora fica **subestimado**. Com jornada de 173,3 h por mês, o custo médio da hora cairia para R$ 72,12 (cerca de 3%).
- **Se houver reconsultas**, o custo da IA sobe, mas continua desprezível.
- **Limite de escala:** a DFP é anual; a base precisa ser recarregada uma vez por ano (`scripts/carregar_dfp.py`).
- **Tempo da IA:** 2,2 s por raio-x (`avaliacao/resultados.csv`), pequeno perto dos 17,5 min do cenário A, que são quase todos
  de leitura e conferência humana.