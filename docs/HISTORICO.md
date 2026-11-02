# Histórico do Raio-X (versão resumida)

Tudo o que aconteceu no projeto, em poucas linhas. Serve para lembrar, para quem chega atrasado numa conversa e para a banca
("como vocês chegaram até aqui?"). O detalhe de cada passo está no pull request (`gh pr list --state all`) e o "agora" está na
seção 0 do [PLANO.md](PLANO.md).

**Como atualizar:** no fim de cada sessão, o `/fim-de-sessao` acrescenta de 1 a 3 linhas no dia certo (o que mudou, com o
número do PR) e, se houve, a decisão na tabela de decisões. Sem detalhe técnico: isso fica no PR.

## Linha do tempo

### Semana 1 (19 a 25/10): cada um no seu canto
- **19/10** · Miguel cria o repositório.
- **20 a 23/10** · Náthally escreve glossário, roteiro, persona, pitch de 30 s e as regras v1 do texto (pasta `Semana_01/`).
- **21/10** · Eduardo: primeira versão do Raio-X (IA, segmentação, checador de dados, tela v0, testes) e o `REGRAS-IA.md`,
  já com a **regra de ouro**: o LLM nunca escreve números (PR #1, merge em 23/10).
- **21 a 23/10** · Marcos: carga e limpeza da DFP da CVM e a tabela de empresas, na branch `tratamento_dados`.

### Semana 2 (26/10 a 01/11): juntar tudo e fazer funcionar
- **26/10** · PR #2 "Fundação": uma pasta por dono, o código do Marcos trazido para a estrutura nova.
- **27/10** · PRs #3 a #6: plano até a banca, matriz do guia, CI (testes em todo PR), versões fixas (Python 3.14);
  dados do Marcos (#4) e produto da Náthally (#5) trazidos para a `main`; `avaliar.py` e teste ponta a ponta (#6).
  **ED1:** os primeiros 3 raio-x com dados reais (595 empresas, US$ 0,0026). Problema achado: o K-means pôs 567 das
  595 empresas num grupo só.
- **28/10** · PR #9 (ED4): segmentação consertada (k = 4, silhueta 0,30; a silhueta de 0,77 "enganava").
  PR #8: guia do Claude Code e as skills `/explicar` e `/fim-de-sessao`. O Miguel passa a usar o Claude Code e começa o
  Docker e o Terraform (branch sem PR). O Marcos muda o banco para PostgreSQL na `tratamento_dados`.
- **29/10** · A Náthally entrega as regras v2 e os `cd_cvm` dos 10 casos. PR #10 (casos) entra.
  PR #11 (ED3): o prompt passa a ser o arquivo de regras dela; 3 raio-x reais sem nada removido; US$ 0,0012 cada.
  Teste do Docker e do Terraform do Miguel: funcionam, faltam ajustes; o teste achou um bug, consertado no PR #12.
  **O professor diz que SQLite não vale: o banco é PostgreSQL** (PR #13).
  O grupo simplifica o GitHub: o CI e o Claude Code revisam; uma pessoa só é chamada para contrato ou pasta de outro dono (PR #14).
  O Miguel tira a aprovação obrigatória da `main`, e os PRs #11 a #14 entram às 11h17 (73 testes passando).
  O PR #15 (só documentação) foi mesclado antes do CI começar; o CI passou depois, e o `/fim-de-sessao` agora espera
  o `pass` (PR #16). É por isso que o check `testes` deve ficar obrigatório no GitHub (MG1).
  O Marcos abre o PR #18 (MA2, PostgreSQL) e a Náthally abre a issue #17 (ano fiscal da Camil, de março a fevereiro).
  Documentos de orientação enxugados (PR #19): cada informação num lugar só, sem as instruções velhas que contradiziam as novas.
  O Marcos fecha o PR #18 sem merge e sem comentário (11h51). **ED7** (PR #20): 10 raio-x com IA, 0 itens removidos,
  US$ 0,0118; comparados com a conferência manual da Náthally no RI, batem 7 de 10 (Camil é a issue #17; Magalu e RD Saúde vão à MA3).
  Quem reformatava as tabelas do PLANO era a extensão Office Viewer do VS Code (abre todo `.md`), não o "Format On Save".
  Às 17h52, o Marcos mescla o PR #21: **o PostgreSQL entra na `main`** (MA2).
- **30/10** · O Eduardo confere a MA2: o banco funciona (carga real em 44 s), mas o CI não tinha PostgreSQL (17 testes pulados)
  e o `indicadores.csv` ainda saía com `;`, formato que o resto do código não lê. O PR #22 corrige os dois, com o ok do Marcos
  (86 testes, nenhum pulado).
  PR #23: o Gemini passa a desistir em até uns 30 s. Antes, esperava sem limite e tentava 6 vezes: com a API travada na banca,
  a tela ficaria girando em vez de cair no plano B.
  O Miguel faz a primeira sessão com o Claude Code, a **MG2** (PR #24): `docker compose up` sobe a tela e o PostgreSQL juntos.
  No Linux dele: os 2 contêineres saudáveis, a CVM carregada no banco do contêiner, 87 testes dentro do contêiner e o raio-x da WEG na tela.
  O #24 entra às 11h32, com o CI verde. A MG1 já estava feita no GitHub (PR e check `testes` obrigatórios, só merge commit,
  apagar branch após o merge): o #24 ficou bloqueado até o CI passar, o que teria evitado o caso do #15.
  PR #26: os guias (CLAUDE.md, README e `aprender/`) passam a ensinar o `docker compose`, e saem deles o `docker run` antigo e o SQLite.
  PR #27: o `contratos.md` deixa de dizer que a `main` usa SQLite; sobram só as frases da regra do professor ("SQLite não vale").
  **PR #28: os 2 arquivos do professor entram em `docs/professor/` e viram a fonte da verdade.** O `requisitos_projeto.MD` (29/10)
  exige o Terraform, que as notas (e o Claude, numa resposta ao Miguel) tratavam como cortável por causa do "ou" do guia de 07/10.
  CLAUDE.md, AGENTS.md, REGRAS-IA.md, as 3 skills, PLANO, REQUISITOS, README e `aprender/` passam a seguir os dois arquivos.
- **31/10** · **MG3** (PR #29): **o Terraform entra na `main`**, em `infra/`. `terraform apply` sobe a tela e o PostgreSQL, como o
  `docker compose`, e o `destroy` apaga os contêineres mas mantém o banco e a `data/` (testado com uma tabela de marca). A chave do
  Gemini não passa pelo Terraform e não fica no `terraform.tfstate`. Um CI novo confere o Terraform em todo PR que mexe em `infra/`.
  No teste da IA, o `apply` falhou com o compose ligado (as mesmas portas): virou aviso no README e nos "Erros comuns".
- **31/10** · **ED12** (PR #30): as regras do `CLAUDE.md` que dá para conferir por máquina viram **travas**: o Claude Code não lê o
  `.env`, não apaga trabalho no Git nem faz commit na `main` ou com dado; pergunta antes do merge, do Gemini e de mexer em pasta
  de outro dono; roda os testes quando muda código. Um segundo Claude (o `revisor`) revisa os PRs sem ter escrito o código:
  na estreia, no próprio #30, achou um jeito de vazar a chave e outros furos que o autor deixou passar; na 2ª revisão, mostrou
  que o conserto tinha aberto furos novos; na 3ª, levou a uma conferência do commit pelo próprio Git (`.githooks/pre-commit`),
  que vale também fora do Claude Code. Tudo corrigido no mesmo PR, com os casos dele virando testes.

### Semana 3 (02 a 08/11): fechar o código e escrever
- **02/11** · O #30 (travas) entra na `main`. **ED8** (PR #31): a justificativa técnica (`docs/justificativa.md`) explica por que o
  projeto não usa RAG vetorial nem fine-tuning: a base de conhecimento da IA é a tabela da CVM, buscada pela chave da empresa, e o
  validador resolve o risco principal (número errado). O README ganha "Como usamos IA para programar".

## Decisões (e por quê)

| data | decisão | por quê |
|---|---|---|
| 21/10 | o LLM nunca escreve números; usa marcadores como `{margem_ebit}` | número inventado num material de vendas é o pior erro possível |
| 26/10 | cada pasta tem um dono | quatro pessoas mexendo no mesmo arquivo geravam conflito |
| 27/10 | Python 3.14 e versões fixas no `requirements.txt` | todos, o CI e o Docker rodam igual |
| 27/10 | merge commit; nunca `rebase` nem `push --force` | guarda os passos (prova para a banca) e não apaga trabalho de colega |
| 28/10 | K-means só com receita a partir de R$ 10 mi, extremos cortados, menor grupo com 5% ou mais | sem isso, um grupo tinha 567 de 595 empresas |
| 28/10 | "empresas parecidas" = mesmo perfil financeiro, não o mesmo setor | é o que o modelo mede; o filtro de setor foi cortado |
| 29/10 | o prompt lê o arquivo de regras da Náthally, sem cópia no código | a cópia tinha ficado diferente do que ela escreveu |
| 29/10 | Suzano S.A. (13986) e Localiza Rent a Car (19739) nos casos | as duas empresas tinham mais de um código na CVM |
| 29/10 | **banco PostgreSQL** | regra do professor: SQLite não vale |
| 29/10 | GitHub simples: CI verde + revisão do Claude Code; pessoa só para contrato ou pasta de outro dono | o clique de "aprovar" travava tudo e não era revisão de verdade |
| 29/10 | cada informação num lugar só: o agora na seção 0 do PLANO, o status no REQUISITOS, o passado aqui | instruções de 26/10 continuavam nos guias e contradiziam as novas (ex.: "main só com 1 revisão"; trazer o `verificar_automatico.py`, que já tinha sido cortado) |
| 30/10 | o CI sobe um PostgreSQL só para os testes (`postgres:17`, banco `raiox_teste`) | sem ele, os testes do banco eram pulados e o CI ficava verde sem testar o banco |
| 30/10 | Gemini com limite de 15 s por tentativa e 2 tentativas | um raio-x leva uns 2 s; sem limite, a API travada deixava a tela girando, sem chegar ao modo sem IA |
| 30/10 | os arquivos do professor (`docs/professor/`) valem mais que qualquer nota; quando os dois diferem, vale o mais exigente; nada que esteja neles pode ser cortado | uma nota tinha virado "regra" (Terraform cortável) contra o `requisitos_projeto.MD`, e o Claude Code repetiu o erro |
| 30/10 | **Terraform obrigatório** | `requisitos_projeto.MD`, Aplicação: "Infraestrutura automatizada com Terraform, podendo rodar localmente ou na nuvem" |
| 30/10 | Docker com `docker compose` (tela + PostgreSQL); a `data/` entra como volume, nunca na imagem | um comando sobe tudo igual em qualquer máquina; a `data/` não vai para o Git nem para a imagem, e o banco fica guardado num volume |
| 31/10 | Terraform em `infra/` com o provider Docker (local, sem nuvem); o volume do banco fica fora do Terraform; a chave chega pelo `.env` montado, não por variável | o R aceita "localmente"; o `destroy` não pode apagar o banco carregado; variável do Terraform fica em texto puro no `terraform.tfstate` |
| 31/10 | regra que custa caro quebrar e que uma máquina confere vira trava (permissão, hook ou CI), não só texto no `CLAUDE.md`; o resto continua instrução | texto o modelo tenta seguir e esquece em conversa longa; trava acontece sempre. A regra de ouro já era assim (validador + testes + CI) |
| 31/10 | o hook não tenta entender o shell: procura o perigo em qualquer ponto do comando e, na dúvida, bloqueia; mensagem que cita o `.env` vai por arquivo (`-F`, `--body-file`) | separar "texto" de "comando" por regex abriu furos duas vezes (achados do `revisor`); um pouco de atrito com uma saída clara é melhor que um buraco |
| 02/11 | sem RAG vetorial, sem fine-tuning, sem memória e sem agente no LangChain: uma chain fixa (prompt → Gemini com saída estruturada) e recuperação pela chave da empresa | os dados são números em tabela (busca por chave é exata; por semelhança, pode trazer a empresa errada); faltam exemplos para fine-tuning, e ele não impediria número errado; cada raio-x é independente e o caminho é sempre o mesmo |

**Já cortado do escopo:** verificação com yfinance, receita em 3 anos, filtro de setor, RAG, nome dos grupos pelo LLM,
exportar o raio-x, 20 casos (ficaram 10). A lista e a ordem dos próximos cortes estão no PLANO, seção 7.

## O que aprendemos (para a banca)

- **Branch longa, sem história em comum com a `main`, vira retrabalho:** três vezes alguém teve de trazer à mão o que estava
  na `tratamento_dados` ou na `feat/metricas`. Agora toda sessão começa da `main` (`/inicio-de-sessao`).
- **Número bonito pode enganar:** a silhueta de 0,77 media só a separação de 9 empresas extremas.
- **Teste que passa nem sempre testa:** dois testes passavam com o campo vazio. Agora estragamos o código de propósito
  para ver o teste falhar.
- **Teste pulado não é teste que passou:** com o PR #21, o CI ficou verde com 17 testes do banco pulados, porque não havia
  PostgreSQL no CI. Agora o CI sobe o banco e lista os pulados (`pytest -rs`).
- **Aprovar sem ler não é revisão:** quem revisa de verdade é o CI (mais de 70 testes) e a leitura do diff; a pessoa entra
  quando a mudança afeta o trabalho dela.
- **Documento velho confunde mais que documento nenhum:** uma lista de tarefas de 26/10, já trocada pelo PLANO, ainda mandava
  trazer arquivos que tinham sido cortados. Agora o que passou sai do guia e vem para cá.
- **A fonte vale mais que o resumo da fonte:** o REQUISITOS resumia só o guia de 07/10, e o resumo virou "verdade" até para a IA,
  que disse que o Terraform não era preciso. Agora os arquivos do professor ficam no repositório e são lidos em toda sessão.

**Se começássemos do zero** (para aprender, não para refazer):
1. Matriz do guia com dono no dia 1, antes de qualquer código.
2. Contratos com o formato do arquivo e falsos no mesmo formato: os bugs do CSV com `;` e do `cd_cvm` como texto são de contrato.
3. Repositório-esqueleto feito por uma pessoa, de onde todos clonam, com CI e versões fixas desde o início.
4. Docker "olá mundo" na primeira semana.
5. Cada um trabalhando contra os falsos, com integração semanal e tag.
