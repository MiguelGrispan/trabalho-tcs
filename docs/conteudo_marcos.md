---
tags: [projeto-tcs, apresentacao]
data: "09/11/2026"
---

# Marcos: conteúdo dos slides de BPMN e arquitetura

Ficha para o deck: slides 5 e 6 do Canva. Os dois formam o bloco "Mapeamento e Arquitetura" do guia (§3, de 03:00 a 06:00), então a soma das duas falas deve ficar em até 3 minutos. Não é registro de ensaio concluído.

## Slide 5 — BPMN

**Título:** Da reunião marcada ao vendedor preparado

**Imagem:** [raio-x-comercial.png](bpmn/raio-x-comercial.png). Ela é muito larga (3615 × 1125): tirar o cartão branco do modelo e usar a largura inteira do slide, senão o texto do diagrama fica ilegível.

**Na tela do slide (abaixo da imagem):**
- O vendedor escolhe e confere; a aplicação calcula, escreve e valida.
- Gemini é serviço externo: devolve texto com marcadores, não números.
- Se algo falha, há saída: texto sem IA, item removido ou aviso.

**Fala sugerida (cerca de 1 min 15 s de leitura, com folga para apontar o diagrama; cronometrar no ensaio):**
“Este é o processo de negócio em BPMN 2.0. Ele começa com uma reunião marcada e termina com o vendedor preparado. Temos duas raias, o vendedor e a aplicação, e o Google Gemini fica numa piscina separada, porque é um serviço externo. No caminho normal, o vendedor procura a empresa, informa o produto e o objetivo e, no fim, lê o resultado. Os dados da CVM, os grupos e as empresas parecidas são preparados antes da reunião; a aplicação só monta os indicadores e a posição contra o grupo. A decisão central é esta: com a IA ligada, pedimos ao Gemini um texto com marcadores no lugar dos números. Se a IA estiver desligada ou o Gemini falhar, a aplicação monta o texto sem IA, com os mesmos números. Depois, cada item passa pelo validador. Aprovado, o código troca os marcadores pelos valores da tabela. Reprovado, o item sai e o motivo fica anotado. O último passo é humano de propósito: o validador confere a forma do texto, não o sentido, então o vendedor lê antes de usar.”

**Prova:** [raio-x-comercial.bpmn](bpmn/raio-x-comercial.bpmn); [ia.py](../raiox/ia.py), `checar()`, `validar_e_preencher()` e `preparar_raio_x()`; [documento](documentacao.md), seções 4 e 7.2.

## Slide 6 — Arquitetura (hoje com o título "Diagrama")

**Título:** Dois contêineres, criados pelo Terraform

**Imagem:** [arquitetura.png](arquitetura.png), feita pelo Miguel (PR #55). Combinar com ele quem fala este slide: a infraestrutura é a parte dele.

**Na tela do slide (ao lado da imagem):**
- Streamlit + `raiox/` num contêiner; PostgreSQL 17 no outro.
- Integrações: dados abertos da CVM e Gemini via LangChain.
- `terraform apply` cria imagens, rede e os dois contêineres, em ambiente local.

**Fala sugerida (cerca de 1 min 15 s de leitura, com folga para apontar o diagrama; cronometrar no ensaio):**
“Esta é a arquitetura que executa aquele processo. Tudo roda em dois contêineres Docker. Um tem a tela em Streamlit e o pacote Python da aplicação, que fazem o papel de frontend e backend. O outro tem o PostgreSQL 17. A tela só abre no próprio computador. Há duas integrações externas: a CVM, de onde vêm os dados abertos, baixados numa carga feita antes da demo, e o Gemini, chamado pelo LangChain somente quando a IA está ligada. O PostgreSQL guarda as contas, as empresas, os indicadores e cada consulta; é nele que a tela busca a empresa. Os números do raio-x e os grupos são lidos dos arquivos gerados na preparação. Quem cria essa estrutura é o Terraform. Com um terraform apply, ele constrói a imagem da tela, cria a rede e sobe os dois contêineres, aqui na máquina local. O terraform destroy remove os contêineres e a rede, mas mantém o banco e os dados carregados. Assim, a infraestrutura fica descrita em código e pode ser recriada com um comando.”

**Prova:** [main.tf](../infra/main.tf), comentários do topo e recursos `docker_image`, `docker_network` e `docker_container`; [docker-compose.yml](../docker-compose.yml); [streamlit_app.py](../app/streamlit_app.py), linhas 11–12 e 73; [documento](documentacao.md), seção 5.

## O que não dizer nestes slides

- **“O Gemini nunca vê números.”** Ele recebe os valores formatados; o que não pode é escrevê-los. A nota do próprio BPMN diz isso.
- **“O validador garante que o texto está certo.”** Ele barra número fora de marcador, marcador desconhecido e pergunta com base inválida, mas não confere o sentido ([documento](documentacao.md), seção 7.2).
- **“Os números do raio-x vêm do PostgreSQL.”** A busca e o registro usam o banco; os números vêm de `data/indicadores.csv`, gerada pelo mesmo script que grava a tabela `indicadores`.
- **“Está na nuvem.”** O Terraform roda no Docker local, o que o `requisitos_projeto.MD` (Aplicação) permite: “podendo rodar localmente ou na nuvem”.
- **“O `terraform apply` já traz os dados.”** A carga da CVM é um passo à parte, descrito no topo do `infra/main.tf`.

**Estado:** conteúdo preparado, sem incorporar ao deck e sem ensaio cronometrado.
