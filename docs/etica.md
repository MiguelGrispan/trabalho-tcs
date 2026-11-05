# Governança, ética e uso responsável da IA (base para a NA5)

Atende:
- `guia_projeto_final.pdf` §2: "Avaliação explicativa sobre viabilidade, limitações, viés, confiabilidade e uso responsável da IA adotada";
- `guia_projeto_final.pdf` §5 (peso 15%): "riscos de viés, alucinação, segurança de dados e uso ético da solução";
- `guia_projeto_final.pdf` §6: "análise de ética e segurança", no PDF (MA6).

> **Rascunho técnico** escrito em 03/11/2026 pelo Claude Code, a pedido do Eduardo, a partir do código. Cada afirmação tem arquivo
> e linha. **A dona do texto final é a Náthally (NA5):** ela reescreve para a banca e completa a viabilidade de negócio (ROI, NA3).
> A parte de segurança técnica (chave, senha, validador) já está em [justificativa.md](justificativa.md), seção 5, e não se repete aqui.

## 1. O risco principal e como foi tratado: número inventado

| risco | o que fizemos | prova |
|---|---|---|
| O LLM inventa ou arredonda um número (alucinação) e o vendedor leva um dado falso para a reunião | o LLM só escreve marcadores como `{margem_ebit}`; o código coloca os valores; o validador apaga o trecho com algarismo, número por extenso ou marcador inventado | `checar()` e `validar_e_preencher()`, `raiox/ia.py:230-282`; testes `test_validador_*` e `test_regra_de_ouro_*` em `tests/test_raio_x.py` |
| Resultado medido | 10 raio-x reais: 0 trechos removidos, US$ 0,0012 cada, 2,2 s em média | `avaliacao/resultados.csv` (rodada de 05/11, ED16; a primeira foi a ED7, PR #20) |

## 2. Alucinação que o validador **não** pega

O validador barra números, não ideias. Continuam possíveis:
- **pergunta enviesada ou com suposição falsa:** ex.: "como a gestão avalia o impacto dos custos na margem EBIT?" supõe que os custos
  são o problema; a margem pode ser baixa por outro motivo;
- **"acima" ou "abaixo" trocado no texto:** a posição é calculada por código e entregue ao modelo (`montar()`, `raiox/ia.py:74`),
  mas a palavra na frase é o LLM que escreve, e o validador não confere. O que protege: a regra 4 do prompt
  (`avaliacao/regras_prompt.md`) e o cartão de cada indicador na tela, que mostra a posição calculada pelo código;
- **lacuna genérica:** "pessoas que decidem a compra" serve para qualquer empresa;
- **interpretação de setor:** o modelo pode associar a empresa a um negócio que ela não tem.

O que reduz o risco: as regras do prompt da Náthally proíbem palavras de intensidade e lacuna em forma de pergunta
(`avaliacao/regras_prompt.md`, lido por `regras()`, `raiox/ia.py:141`); `temperature=0.2` (`raiox/ia.py:161`); cada pergunta
traz a "base", o indicador que a motivou, visível na tela. **O que não resolve:** só a leitura humana. Por isso a seção 5.

## 3. Viés e limites do modelo de ML (K-means + vizinhos)

- **Só companhias abertas:** a base é a DFP da CVM. Empresa de capital fechado, pequena ou média, não aparece. A ferramenta
  serve para vender a grandes contas, não para qualquer cliente.
- **Treino só com receita a partir de R$ 10 mi** (`RECEITA_MINIMA`, `raiox/segmentos.py:35`): abaixo disso, 31 empresas, 52% com
  margem EBIT acima de 100% em valor absoluto (holdings, sem operação), segundo o `scripts/avaliar_corte_receita.py` (rodado pelo Marcos em 03/11, com os dados do PR #46; `docs/REQUISITOS.md`, R5). Essas empresas
  **recebem um grupo mesmo assim**, o mais próximo, sem terem ajudado a formá-lo (`segmentar()`, `raiox/segmentos.py:83-95`).
  Para elas, a comparação com o grupo é menos confiável. E elas também entram na mediana e no tamanho do grupo mostrados na tela
  (ex.: o grupo da WEG tem 312 empresas na tela e 310 no treino; dados de 05/11).
- **Extremos cortados nos percentis 5 e 95** (`CORTE`, `raiox/segmentos.py:36`): só para o modelo; os números mostrados são os reais.
  Uma empresa muito fora da curva fica num grupo que não a representa bem.
- **Grupo por perfil financeiro, não por setor:** as 5 variáveis são receita, crescimento, margens e endividamento
  (`VARIAVEIS`, `raiox/segmentos.py:38`). Ex.: a WEG (máquinas e equipamentos; números 100% iguais ao RI em
  `avaliacao/conferencia.csv`) tem como parecidas Cemig, Copel, Axia (energia), Votorantim Cimentos e Telefônica: empresas grandes,
  rentáveis e pouco endividadas, mas de outros setores (raio-x sem IA, 03/11). Isso é útil para prospectar perfis parecidos, mas não é "concorrente".
  A tela precisa dizer isso (sugestão para a NA5 e o deck).
- **Os 10 casos de avaliação caem no mesmo grupo** (o maior, com 312 empresas e receita mediana de R$ 3,6 bi; rodadas de 29/10 e
  05/11). A Petrobras (R$ 497,5 bi de receita) é comparada com esse grupo: "acima do grupo" diz pouco para uma empresa desse porte.
  É um limite do K-means com 4 grupos, não um erro de dado (issue #60, Eduardo).
- **Silhueta 0,29:** os grupos se sobrepõem. É uma régua de comparação, não uma classificação exata
  ([justificativa.md](justificativa.md), seção 2, explica por que 0,77 enganava).

## 4. Confiabilidade dos dados

- **Dado de até um ano atrás:** a DFP é anual (`scripts/indicadores.py:60`, último ano disponível). Resultado do trimestre não entra.
- **Acerto contra o RI: 8 de 10** nos 6 indicadores, na conferência manual da Náthally (o `revisao_manual.md` está na branch
  `feat/metricas`, ainda não na `main`), com os dados de 05/11 (ED16). Critério de "bate": receita e ativo com até 1% de diferença; os 4 percentuais com até 0,15 ponto percentual.
  Era 7 de 10 até a Camil ser corrigida (ano fiscal de março a fevereiro, issue #17, PR #46). As 2 diferenças: Magalu (margem EBIT)
  e RD Saúde (margem EBIT, endividamento e ativo); nas duas, o sistema bate com a DFP oficial (conferência S2 do Marcos,
  `avaliacao/conferencia.csv`), e a diferença é de **definição**, não de dado (conferido nos PDFs que ela usou, 05/11):
  - **RD Saúde:** a conferência usou a tabela "Pré-IFRS 16" do Relatório da Administração, que está no mesmo PDF da DFP 2025
    (p. 48 da DFP). Ela tira os aluguéis das lojas do balanço e do resultado: ativo R$ 20.630,8 mi, PL R$ 7.749,6 mi, EBIT ajustado
    R$ 2.331,9 mi e lucro R$ 1.362,5 mi dão exatamente os 4 números dela. O sistema usa a DFP oficial, com IFRS 16 (CPC 06):
    ativo R$ 25.170,5 mi, com R$ 4.336,0 mi de direito de uso das lojas alugadas.
  - **Magalu:** os 5,81% saem exatamente do EBIT oficial (R$ 1.918,7 mi) sem as perdas de créditos esperadas (−R$ 455,8 mi) e sem
    a equivalência patrimonial (+R$ 127,3 mi). É reconstrução nossa; falta a Náthally confirmar que foi essa a conta.
  **Na banca, falar 8 de 10, não "100%"**, e explicar que as 2 diferenças são de definição contábil.
- **Número oficial × número "ajustado":** empresas como a RD divulgam no release números "ajustados" ou "Pré-IFRS 16", e o vendedor
  pode ouvi-los na reunião. O raio-x mostra o número contábil oficial da DFP, igual para as 595 empresas, que pode ser diferente.
  O vendedor precisa saber disso (sugestão para a NA5, o deck e, depois do congelamento, um aviso na tela).
- **Fonte em cada número:** cada indicador mostra a conta da DFP de onde veio (coluna "fonte", `raiox/ia.py:36-44`), para o vendedor
  conferir.

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

## 6. Viabilidade (a completar pela Náthally)

- **Custo por raio-x:** ≈ US$ 0,0012 de IA (`avaliacao/resultados.csv`).
- **Tempo:** 2,2 s de IA (média da rodada de 05/11); o tempo manual de comparação é o ROI da NA3 (a medir).
- **Limite de escala:** a DFP é anual; a base precisa ser recarregada uma vez por ano (`scripts/carregar_dfp.py`).
