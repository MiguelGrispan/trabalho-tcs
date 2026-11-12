# Roteiro da demo

Demo ao vivo: **5 minutos**, das 04:30 às 09:30 da apresentação, falada pelo Miguel (`docs/tempo_apresentacao.md`; o guia §3 dava 6,
das 06:00 às 12:00 de uma apresentação de 20 min: "aplicação rodando em tempo real"). Versão do código: tag **`v1.1`**, com o botão
das fontes (PLANO §0, 11/11); a `v1.0.1` continua como plano B. Dono: Miguel (MG6).

O guia §3 pede na demo "entrada de dados, processamento da IA e saída gerada": o roteiro segue essa ordem. Os tempos de cada bloco
são estimativa (cerca de 130 palavras por minuto, como no `docs/roteiro_fala.md`): **cronometrar no ensaio** e corrigir aqui.

## Antes de apresentar

A aplicação da demo sobe **pelo Terraform** (pasta `infra/`), não pelo `docker compose`: é a "Infraestrutura automatizada com
Terraform" que o `requisitos_projeto.MD` exige (Aplicação), e a banca vê funcionando a mesma infraestrutura que o Miguel explica no
detalhe técnico. No computador da demo (o Mac do Eduardo), **antes de a banca começar** (e sempre depois de reiniciar o computador
ou o Docker):

1. Se o compose estiver de pé (`docker compose ps`, na raiz, mostra `banco` e `tela`), rode `docker compose down`: o compose e o
   Terraform usam as mesmas portas (8501 e 5432), um de cada vez (README, "Como rodar com Terraform").
2. Dentro de `infra/`: `terraform init` (só na primeira vez nesse computador) e `terraform apply -var ia_real=true`. Leia o plano
   e responda `yes`. O `apply` só termina quando o banco aceita conexões e a tela responde (`wait = true`, `infra/main.tf:101`
   e `:145`); se o código mudou, ele refaz a imagem da tela sozinho (`triggers`, `infra/main.tf:46`).
   **Sempre com `-var ia_real=true`:** um `apply` sem ele troca a tela por uma sem IA (`infra/main.tf:114`).
   No Mac, se o `apply` não achar o Docker: `export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock` (README).
3. `docker ps`: `raiox-tela` e `raiox-banco` precisam aparecer como `(healthy)`.
4. Abra http://localhost:8501: a tela precisa abrir e a busca precisa achar a WEG.
   Se aparecer "O banco está vazio": o banco do Terraform é outro volume (`raiox-banco-dados`), e a CVM carregada pelo compose
   não aparece nele. Carregue com `docker exec raiox-tela python scripts/carregar_dfp.py` e depois
   `docker exec raiox-tela python scripts/indicadores.py` (topo do `infra/main.tf`; no Linux, com `--user "$(id -u):$(id -g)"`
   logo depois do `exec`). Faça isso dias antes da banca: a carga baixa os arquivos da CVM.
5. O topo da tela precisa dizer **"IA ligada: o texto será escrito pelo Gemini."** Se disser "Texto montado sem IA", refaça o
   passo 2 com `-var ia_real=true`.
6. Gere um raio-x de teste da WEG (gasta uma chamada, cerca de US$ 0,0012). Em **De onde vem cada número**, a aba de um
   indicador precisa mostrar o botão **Baixar DFP (CVM)**. Se o botão não aparecer, a carga de links não foi feita nesse banco:
   `docker exec raiox-tela python scripts/carregar_links.py`. Depois recarregue a página (Cmd+R ou F5): a tela volta ao começo.
7. Deixe o objetivo da reunião copiado, para colar em vez de digitar. Navegador em tela cheia, zoom de uns 125%, uma aba só,
   notificações desligadas ("Não perturbe").

**Por quê:** depois de reiniciar, só o banco volta sozinho: o `restart = "unless-stopped"` está só nele (`infra/main.tf:68`), e a
tela fica parada (`Exited`), com a página sem abrir. Um novo `terraform apply -var ia_real=true` deve subir a tela de novo (o
provider do Docker recria o contêiner que não está rodando): **conferir no ensaio** com `docker ps`. O conserto é esta lista, não
uma mudança no `infra/`.

## Roteiro dos 5 minutos

Os números citados abaixo são do print da tela real de 11/11 (`docs/graficos/tela_fontes_weg.png`). **Leia sempre da tela**: se a
CVM for recarregada, eles podem mudar. O texto do Gemini (resumo, perguntas, lacunas) muda a cada chamada.

### [0:00–0:30] Abertura

- **Tela:** a tela inicial.
- **Fale:** "Vou mostrar o Raio-X funcionando: a tela e o banco PostgreSQL rodam em dois contêineres que o Terraform subiu, com
  dados reais da CVM e o Gemini ligado. O caso: uma vendedora de soluções de eficiência energética tem a primeira reunião com a WEG."
- **Aponte:** a legenda "IA ligada: o texto será escrito pelo Gemini."

### [0:30–1:15] Entrada de dados

- **Faça:** em "Digite parte do nome", digite `weg`; em "Escolha a empresa", selecione "WEG S.A. · …"; aponte o botão ainda
  desligado e o aviso "Falta preencher: o produto, o objetivo."; em "O que você vende", digite `Energia Eficiente`; em
  "Objetivo da reunião", cole `Investigar oportunidades de eficiência energética nas instalações industriais`
  (o caso 9 de `avaliacao/casos_avaliacao.csv`).
- **Fale:** "A busca vai no banco PostgreSQL. O botão só libera com os três campos preenchidos, e a tela diz o que falta."

### [1:15–1:35] Processamento da IA

- **Faça:** clique em **Gerar raio-x**. Aparece "Montando o raio-x..." (na avaliação, uns 2 s).
- **Fale:** "O código pega os seis indicadores, o K-means acha o grupo de empresas parecidas e o Gemini escreve o texto. A regra
  de ouro: o Gemini não escreve números. Ele usa marcadores, e o código coloca os valores da tabela."

### [1:35–2:15] Saída 1: os números

- **Tela:** "WEG S.A.", a legenda "… grupo 1 (312 empresas de perfil parecido)", os 6 cartões e o gráfico
  "Empresa × grupo de empresas parecidas (%)".
- **Fale (lendo da tela):** "Seis indicadores do último exercício, cada um contra o grupo. A margem EBIT está acima do grupo; o
  endividamento, abaixo. Quem decide acima ou abaixo é o código, não a IA." (No print: margem EBIT 19,6% × 13,8% do grupo;
  endividamento 56,5% × 66,1%.)

### [2:15–3:15] Saída 2: o texto para a reunião

- **Tela:** "Resumo", "Perguntas para a reunião" (cada uma com "base: …") e "O que os números não dizem".
- **Fale:** "As perguntas foram escritas para o produto e o objetivo que digitei, e cada uma mostra de qual indicador saiu."
  Leia **uma** pergunta em voz alta. "Ao lado, o que os números não dizem: o que a vendedora precisa descobrir na conversa. A
  ferramenta mostra o que não sabe."

### [3:15–3:45] Saída 3: para prospectar

- **Tela:** "Empresas parecidas para prospectar" (5 linhas).
- **Fale:** "As cinco empresas de perfil financeiro mais próximo. Parecida não quer dizer concorrente: por isso aparecem empresas
  de energia. É um ponto de partida." (Limite declarado: issue #60, `docs/etica.md`.)

### [3:45–4:40] De onde vem cada número

- **Faça:** abra **De onde vem cada número**. Em "Confira no DFP", clique na aba **Margem EBIT**: a tabela traz as contas 3.05 e
  3.01 com descrição, ano e valor em reais. Aponte o botão **Baixar DFP (CVM)** sem clicar (ele baixa um `.zip` da CVM, e o
  download tomaria tempo).
- **Fale:** "Cada número tem fonte: o ano, o demonstrativo e a conta. Aqui está a conta usada na margem EBIT, com o valor em reais
  como está no documento. E este botão baixa o documento oficial na CVM, para quem quiser conferir. Nada disso é escrito pela IA:
  vem do banco."

### [4:40–5:00] Fechamento

- **Faça:** abra **Detalhes técnicos**.
- **Fale:** "O validador não removeu nenhum trecho, e este raio-x custou menos de um centavo de dólar. Se o Gemini cair, a tela
  monta o texto sem IA, com os mesmos números. Passo ao Marcos."

**Fica fora dos 5 min:** como o Terraform funciona (`infra/main.tf`, `docker ps` com `raiox-tela` e `raiox-banco`) vai para os
0:45 de infraestrutura do Miguel no detalhe técnico; o rodapé da tela não é lido.

## Se algo der errado ao vivo

- **O Gemini não respondeu:** a tela mostra "A IA não respondeu agora. O texto abaixo foi montado sem IA; os números são os
  mesmos." Siga o roteiro e diga essa frase: é o plano B funcionando (regra 6 do `CLAUDE.md`).
- **A tela ou a rede travou:** troque para o vídeo de reserva.

## Vídeo de reserva

O vídeo **ainda não foi gravado** (12/11). Grava-se com este mesmo roteiro de 5 min, na `v1.1`, no Mac do Eduardo (o computador
da demo, decisão de 04/11 no `docs/HISTORICO.md`), com a aplicação subida pelo Terraform como na lista acima, e guarda-se em 2
lugares (`guia_projeto_final.pdf` §3, dica). O vídeo não vai para o Git (a trava barra arquivo acima de 10 MB): o link vai para o
`docs/ENTREGAS.md`.

- Gravar no Mac: Cmd+Shift+5 → "Gravar a tela inteira"; em "Opções", escolher o microfone.
- Cada tomada com IA é uma chamada ao Gemini (cerca de US$ 0,0012). Passou de 10 chamadas: avise o grupo (`CLAUDE.md`, Cuidados).
