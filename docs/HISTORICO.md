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
  **O professor responde à pergunta 1: o Streamlit vale como a aplicação**, com a tela e a aplicação num contêiner e o banco em outro.
  Para o grupo, isso quer dizer que não precisa de API separada. O compose e o Terraform já sobem os 2. Falta a tela usar o banco (MG4).
- **02/11** · **MG4** (PR #36): a tela busca as empresas no PostgreSQL e grava cada consulta na tabela `consultas`; se o Gemini falhar,
  volta sozinha para o modo sem IA. Conferido no Docker com WEG, Embraer e Ambev. O #34 (o guia do professor sem os exemplos, refeito
  pelo grupo no Google Docs) foi desfeito pelo #35, e a branch antiga `docs-docker-e-terraform` foi apagada (a MG2 e a MG3 já a cobriam).
- **03/11** · **Demo ponta a ponta no Mac do Eduardo** e tag `v0.1-demo` (no merge do #36): Vale, Embraer e Ambev sem IA e WEG com o
  Gemini (US$ 0,0011), todas gravadas na `consultas`. O **Terraform** sobe pela 1ª vez num Mac, nas portas padrão, e o banco sobrevive ao
  `destroy` + `apply`. No Mac, o Terraform só acha o Docker com o `DOCKER_HOST` (`README.md:235`).
- **03/11** · O Eduardo testa a tela com o Gemini fora do ar (chave falsa): o plano B funciona; 2 problemas de aparência viram as
  issues #38 e #39 (Miguel, MG4b). Entra `docs/etica.md`, a base técnica da ética para a Náthally (PR `eduardo-etica`).
- **03/11** · **Revisão geral** (Eduardo com o Claude Code): a MA3 do Marcos estava pronta numa branch sem PR, e a nota dizia que
  ela não existia (issue #42); a S2 dele explica 2 das 3 diferenças do "7 de 10"; a #17 (Camil) passa ao Marcos; um bug na tela
  aberta antes da carga da CVM (#43, Eduardo) e a tela aberta para a rede no compose (#44, Miguel). A seção 0 do PLANO cai de
  ~240 para ~90 linhas (a versão longa: `git show 9f85bc9:docs/PLANO.md`). Proposta: o Eduardo monta o PDF e o processo congela até a entrega.
- **03/11** · **MA3** (PR #46, Marcos): o C1 e o C2 no PostgreSQL (busca só de ativas, `cd_cvm` número, tabela `indicadores`) e 5
  empresas conferidas no RI (0,00%). **A Camil estava com o exercício anterior** (#17): a CVM arquiva a DFP pelo ano em que o exercício
  termina, e o "2025" dela (mar/2025 a fev/2026) estava no arquivo de 2026, que não era baixado. Agora a receita (R$ 11,1 bi) e o crescimento
  (−1,2%) batem com o RI e com a conferência manual da Náthally; mudaram as 9 empresas que fecham fora de dezembro.
  No Windows, as travas leem o Git em cp1252 e bloqueavam commit e merge (#45, Eduardo).
- **03/11** · **MG4b** (PR #47, Miguel): a tela para de se contradizer quando a IA falha. O aviso tem uma frase (o erro do Google
  vai para "Detalhes técnicos" e para o log), e o topo e o rodapé só dizem que a IA escreveu quando o Gemini respondeu (#38, #39).
  O compose passa a abrir a tela só no próprio computador, como o Terraform (#44). A tela nova da MG4 também foi conferida pelo
  Terraform, no Linux do Miguel.
- **04/11** · O 1º fechamento da MG4b parou no meio do `git merge main` (o #46 tinha entrado), e a conversa foi voltada no Claude
  Code. Voltar a conversa restaura os arquivos que o Claude editou, mas não desfaz o Git: o merge ficou pela metade, com cópias
  antigas por cima, e o `tests/test_tela.py` antigo junto do `raiox/dados.py` novo derrubou 1 teste. Conserto: `git merge --abort`
  (com o ok do Miguel) e o merge refeito do zero. Na recarga da CVM com o #46, a tela não gerava nenhum raio-x: o
  `indicadores.py` novo grava o CSV com permissão só do dono, e o contêiner não lê (issue #48, Marcos; contorno: `chmod 644`).
- **04/11** · **MA3b** (Marcos): conserto da #48. O `publicar()` libera o CSV para leitura (`0644`) antes de trocá-lo, com teste novo.
  Falta a conferência no Linux do Miguel. Na validação do dia, o `python -m raiox.segmentos` deu grupos de 330, 108, 91 e 66
  com os dados do #46 (os PNG de `docs/graficos/` continuam os de 28/10).
- **04/11** · O #51 (MA3b) entrou na `main`, e a #48 foi fechada depois de o Miguel conferir no Linux: o CSV sai legível e a
  Camil gera o raio-x sem o `chmod`. **MA5** (Marcos): o BPMN 2.0 do processo com o Raio-X (`docs/bpmn/`), desenhado pelo Claude
  Code a partir do código, com as decisões "tem dados?" e "passou no validador?" (item por item); abre no bpmn-js sem avisos. O `revisor` achou que o
  1º desenho dizia "frase por frase", e o código confere o resumo inteiro, cada pergunta e cada lacuna: corrigido no mesmo PR.
- **04/11** · **MA4** (Marcos): a EDA em `notebooks/eda.ipynb`, com 4 gráficos (nulos, distribuições, extremos, cobertura) e o
  porquê de cada decisão de limpeza e do K-means; um teste roda o notebook inteiro no CI. A EDA achou um erro que a limpeza
  deixava passar: a NTS tem 2023 de 1.000 a 2.000 vezes menor e aparecia com crescimento de +107.154% (issue #53, MA4b).
- **04/11** · **MG5** (Miguel, PR #55): o README ganhou a seção "Arquitetura" (diagrama dos 2 contêineres, da `data/`, do Gemini,
  da CVM e do Terraform) e a de "Pré-requisitos"; a mesma figura está em `docs/arquitetura.png` para o documento e o deck. Achado
  no caminho: o README mandava `python -m venv`, que não funciona no Linux do Miguel (lá, `python3` é o 3.12); agora é `python3.14`.
  O `revisor` achou mais 2 erros fora do PR: a tela diz que os números vêm do banco (#56, Miguel) e os outros guias têm o mesmo
  `venv` (#57, Eduardo).
- **04/11** · O grupo decide (mensagem do Marcos): a demo da banca roda no Mac do Eduardo, onde o Miguel grava os vídeos, e o
  documento do projeto (MA6) passa ao Eduardo; o Marcos fica com o BPMN e a EDA. **MA6, rascunho 1** (Eduardo com o Claude Code,
  PR #49): `docs/documentacao.md` e o PDF gerado dele; em 05/11, com o K-means e as métricas novas do #58.
- **05/11** · **MA4b** (Marcos): conserto da #53. A limpeza agora confere também o primeiro ano de cada empresa, comparando-o com
  o seguinte; a NTS passou de +107.154% para +7,3% de crescimento, e nenhuma outra empresa mudou. O JBS N.V. continua como caso a
  conferir na CVM (falta o segundo sinal). Todos recarregam a `data/` depois do merge.
- **05/11** · **ED16** (Eduardo): os 10 raio-x da Náthally de novo, com o Gemini e a Camil corrigida pelo #46. Agora 8 de 10
  batem com a conferência manual dela (era 7); Magalu e RD Saúde seguem iguais à DFP e diferentes dela. O K-means e os gráficos
  foram refeitos com os dados novos, já com o #59 (silhueta 0,29; grupos de 60, 310, 88 e 106 no treino), e o `resultados.csv` trocado.
  As 2 diferenças foram explicadas abrindo os PDFs dela: a RD Saúde estava em "Pré-IFRS 16" (sem os aluguéis das lojas) e o
  Magalu com outra conta do EBIT. Não é erro de dado, é definição; o sistema segue a DFP oficial.
- **05/11** · **Processo** (Eduardo): uma auditoria do projeto mostrou que os conflitos entre as branches vinham das notas:
  os PRs #46 a #59 mexeram todos no PLANO, no REQUISITOS e no HISTORICO, e o time esperava um pelo outro para fazer o merge.
  Agora só o Eduardo edita as notas, uma vez por dia; os outros escrevem o que mudou no PR, e o `/fim-de-sessao` mostra quem tem PR aberto.
  No mesmo PR (#62), a trava parou de perguntar "o grupo sabe?" por CLAUDE.md, skills e CI: só pelo que desliga as travas.
- **05/11** · **ED13, ED14 e #50** (Eduardo, PR #63): a tela aberta antes da carga da CVM agora acha a empresa sem reiniciar (#43);
  o validador barra "dobrou", "triplicou" e "um quarto" (#50); a trava funciona no Windows, lendo e escrevendo em UTF-8 (#45,
  falta o Marcos conferir lá). Cada teste novo falha sem o conserto.
- **06/11** · Marcos: o BPMN corrigido (#65) e os testes passando dentro do contêiner (#66). **MA6, rascunho 2** (Eduardo com o
  Claude Code, PR #49): o documento com BPMN, arquitetura e EDA, os limites do K-means e do validador ditos com exemplo, e o
  índice das entregas (`docs/ENTREGAS.md`); sai o PDF velho que falava de SQLite. Achado: o professor ainda não tem acesso ao
  repositório privado.

- **07/11** · Eduardo com o Codex: candidata técnica ao congelamento, Python 3.14 explícito nos seis guias/atalhos (#57), instalação num venv vazio, testes com PostgreSQL e ensaio funcional com dados reais, sem chamada paga. Conteúdo técnico dos slides e rascunho não enviado ao professor em `docs/conteudo_eduardo.md`; PDF atualizado. Naquele momento, merge/tag, revisão humana e contribuições externas continuavam pendentes.
- **07/11, fechamento** · PR #67 mesclado e tag `v1.0` publicada em `2c3e942`: código congelado, #57 fechada. EDA do Marcos reconferida com dados reais (15 células de código, quatro gráficos), sem alterar seus arquivos. Auditoria dos 114 arquivos e atualização dos registros e da memória compartilhada; sem mudança no produto.

### Semana 4 (09 a 15/11): entregar

- **09/11** · **Revisão final** (Eduardo com o Claude Code, issue #69): três revisores em paralelo, só lendo, e cada achado reproduzido.
  O código passou (263 testes com o banco, CI verde, Terraform válido, nada de segredo no Git), mas duas brechas na regra de ouro
  apareceram: "bilionária" e "uma vez e meia" passavam pelo validador, e o erro de formato do Gemini mostrava o texto dele, com números,
  em "Detalhes técnicos". Consertadas com teste na `v1.0.1`. Fora do código: o professor ainda não tem acesso ao repositório privado,
  o ROI ainda não foi medido e o exemplo do README com a empresa 90001 só funciona com os dados falsos.
- **09/11** · **Tempo da apresentação:** o professor disse ao Eduardo 18 min + 12 min de banca (guia §3 dizia 20) e que a banca é em qui 19/11 (não qua 18/11); entrega 48 h antes: ter 17/11. Alvo do grupo: 15 min, com 3 min de folga; tempo por etapa e por pessoa em `docs/tempo_apresentacao.md` (divisão proposta, não confirmada). Para reverter: reverter este PR.
- **10/11** · **Fontes dos números:** a Náthally pediu um jeito de o usuário conferir de onde vem cada número (ROI). Verificado: a CVM publica o `LINK_DOC` de cada DFP, mas ele baixa um `.zip`, e o cruzamento por ano do calendário erra a Camil (fecha em fev.). Decisão com ela: trecho do DFP (A) e link (B). Desenho sem mudar o C2 nem recarregar as contas: campo `conferir` no C3, `raiox/fontes.py` e `links_dfp`. Sessões ED17, MA7, MG8, NA7, ED18; prazo qui 12/11 18h, plano B `v1.0.1`. Reverter: `git revert` do merge e voltar à tag `v1.0.1`.
- **10/11** · **Notas por sessão:** a partir de hoje cada pessoa registra a própria sessão (linha no PLANO §3, uma linha aqui, linha do REQUISITOS) pelo `/fim-de-sessao`; a seção 0 continua do Eduardo, que consolida (ED19). Motivo: só ele atualizava e as notas atrasavam; o conflito de 05/11 é tratado com o `.gitattributes` (HISTORICO guarda as duas linhas) e com `git merge origin/main` antes do push. Reverter: voltar a regra no `CLAUDE.md` (regra 8) e nas skills `fim-de-sessao` e `inicio-de-sessao`.
- **10/11** · **Tela das fontes (MG8, Miguel com o Claude Code):** em "De onde vem cada número", cada indicador ganhou uma aba com as contas do DFP usadas na conta (código, descrição, ano e valor em reais, sem abreviar) e o botão "Baixar DFP (CVM)", que só aparece quando há link e avisa que baixa um `.zip`. Abas em vez de 6 botões iguais empilhados: o link é o mesmo DFP para os 6 indicadores. Sem o campo `conferir`, a tela fica como na `v1.0.1` (regra 6). Prova: 3 testes novos em `tests/test_tela.py`, 274 passed com o PostgreSQL; WEG real no Docker, com as contas batendo com a tabela `contas`. O botão com dados reais e o print do deck esperam a MA7. Reverter: `git revert` do merge do PR #76.
- **10/11** · **Links da CVM (MA7, Marcos com o Claude Code):** `scripts/carregar_links.py` grava `data/links_dfp.csv` e a tabela `links_dfp` a partir do arquivo principal dos zips de 2023 a 2026, casando pelo ano do exercício para a Camil não pegar o DFP errado. Nas duplicatas (26239 e 26824, exercícios 2023 e 2024), fica o `ID_DOC` mais recente, porque ele cresce com a data de entrega. Prova: "Cobertura: 595 de 595 empresas com link", o link da Camil baixa o arquivo de 28/02/2026, 13 testes novos, 284 passed. Limite visto: o servidor da CVM oscilou (4 tentativas no link da Camil: 2 zips, 1 conexão cortada, 1 página de texto de serviço ocupado). Reverter: `git revert` do merge deste PR; a tela volta a ficar sem o botão.
- **10/11** · **Consolidação do ED18:** a `main` já tem os PRs #75, #76, #77 e #79; README, documento em Markdown, roteiro da demo e índice de entregas agora explicam o trecho das contas e o botão que baixa o `.zip` da CVM. Prova ponta a ponta com PostgreSQL no Docker (depois de reiniciar o Docker Desktop, que devolvia erro 500): WEG, Camil e uma empresa só com balanço individual (22179) trazem as contas e o link da CVM; 287 testes passam com o banco. PDF regerado (22 páginas, com o BPMN da MA8). ROI (NA7), ética final, print do botão (MG8) e tag `v1.1` continuam pendentes.
- **10/11** · **BPMN com as fontes (MA8, Marcos com o Claude Code):** o diagrama ganhou a tarefa "Anexar as fontes" (contas do DFP e link da CVM), logo depois de montar os indicadores, como em `raiox/ia.py:313`, porque o processo mudou com a ED17, a MA7 e a MG8. O documento (seção 4) e o `roteiro_fala.md` acompanham; o roteiro também deixou de dizer que os indicadores do raio-x são lidos do banco (vêm do `indicadores.csv`). Prova: bpmn-js 17.11.1 com 0 avisos, PNG 3900 × 1125. Reverter: `git revert` do merge deste PR.
- **10/11** · **Arquitetura com as fontes (MG9, Miguel com o Claude Code):** o diagrama do README e o `docs/arquitetura.png` ainda eram os da MG5 e não mostravam as fontes dos números. Agora mostram o `raiox/fontes.py` (lê as tabelas `contas` e `links_dfp` a cada raio-x; se o banco falha, o link vem do `links_dfp.csv`), o `scripts/carregar_links.py` na carga e a seta do vendedor para a CVM, porque o botão "Baixar DFP (CVM)" é só um link: o navegador baixa o `.zip` direto do site da CVM (`rad.cvm.gov.br`). A CVM agora diz "exercícios 2023–2025 (arquivos de 2023 a 2026)", como o `ANOS` do `scripts/carregar_dfp.py`. Prova: 287 passed com o PostgreSQL; PNG regerado do mesmo bloco (Mermaid 11.4.1) e conferido. Reverter: `git revert` do merge deste PR.
- **11/11** · **Congelamento e PDF com a arquitetura nova (ED18, Eduardo com o Claude Code, PR #80):** código conferido no Mac (287 passed com o PostgreSQL; 267 passed e 20 skipped no contêiner; Docker com os 2 `healthy`; raio-x sem IA de WEG, Camil e Embraer com o `conferir`; Terraform `validate`). Figura 6 do documento trocada pela arquitetura da MG9 e PDF regerado (a figura cabe na página deitada). Print da tela das fontes (MG8) em `docs/graficos/tela_fontes_weg.png`. Tag `v1.1` = versão da banca; o ROI e a ética entram só no documento. Reverter: `git revert` do merge deste PR e apagar a tag.
- **11/11** · **Repositório para o professor (Eduardo com o Claude Code, PR #82):** README ganhou a tabela "Para quem avalia" (cada requisito do professor e onde está) e aponta a `v1.1`; o `ENTREGAS.md` foi atualizado; saíram a figura sem uso `docs/graficos/grupos_antes_ed4.png` e o rascunho de mensagem ao professor do `conteudo_eduardo.md`. Histórico conferido com `git log -G`: nenhuma chave do Gemini, chave privada ou senha real (só `postgres:postgres` local e `SUA_SENHA`), nenhum arquivo de dados. Reverter: `git revert` do merge.

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
| 02/11 | a aplicação é o Streamlit, sem API separada: a tela e `raiox/` num contêiner, o PostgreSQL em outro | resposta do professor à pergunta 1 ("um contêiner para ele e a aplicação e um para o SQL"); "sem API" é a leitura do grupo; uma API nova (ex.: FastAPI) seria escopo novo a 2 semanas da entrega |
| 02/11 | a tela escolhe entre falsos e banco pela mesma função do raio-x (`usando_falsos()`, `RAIOX_DADOS`), sem chave própria; se a IA falhar, cai sozinha no modo sem IA | com duas chaves, a busca podia vir do banco e o raio-x da tabela falsa, e nada bateria; a demo não pode parar porque a API caiu |
| 02/11 | o guia do professor fica como ele mandou, com os exemplos (#34 desfeito pelo #35) | uma versão refeita pelo grupo deixa de ser a fonte da verdade, e tirar a seção 4 renumeraria as seguintes, quebrando 21 citações como "G §6" |
| 02/11 | tarefas da Náthally: obrigatório é só o que os arquivos do professor pedem (deck, ética e, na apresentação, ROI e métricas); testes com usuários, `revisao.csv` e regras v3 viram sugestão | ela trabalha no ritmo dela e sem IA para código; o grupo concentra o tempo dela no que a banca avalia |
| 03/11 | erro achado na pasta de outro dono vira **issue no GitHub** para ele e uma sessão dele no PLANO; o ATENÇÃO do revisor é corrigido antes do merge (`/fim-de-sessao`, passo 6; `CLAUDE.md`, regra 1) | recado no chat se perde e ninguém cobra; a issue fica com dono, prova e prazo (primeiras: #38 e #39). No PR #40, o revisor achou uma frase falsa na ética que só foi corrigida porque o ATENÇÃO foi tratado |
| 03/11 | o "ano" de cada número é o do exercício (o ano com mais meses dele), e não o do arquivo da CVM; baixa-se também o arquivo do ano seguinte (opção 3 da #17) | a Camil fecha em fevereiro e aparecia com o exercício anterior; o rótulo sozinho (opção 2) mudaria o C2 e o C3, e tirar a Camil da demo (opção 1) deixaria 8 empresas erradas sem aviso. Coube em 2 arquivos e 3 testes, sem mudar o formato do C2 |
| 03/11 | corte de receita mínima de R$ 10 mi no K-means, confirmado pelo Marcos | abaixo dele, 52% das 31 empresas têm margem EBIT acima de 100% ou abaixo de −100%; acima, só 4% das 564 |
| 03/11 | a conexão com o banco desiste em 5 s | sem limite, o psycopg espera 130 s, e a tela ficava parada antes do aviso de banco desligado (a demo não pode travar) |
| 03/11 | a tela só abre no próprio computador (`127.0.0.1`), no compose como no Terraform; o erro técnico da IA vai para "Detalhes técnicos" e para o log, nunca para o aviso | com a IA ligada, qualquer um no mesmo Wi-Fi (o do SENAI, no dia da banca) abria a tela e gastava crédito; quem precisar abrir de outro aparelho muda a porta de propósito. Um JSON do Google no telão não diz nada ao vendedor, mas quem conserta precisa dele |
| 04/11 | a EDA importa do código os limites da checagem e o corte do K-means, em vez de copiar os números; vai para o Git já rodada; com os dados falsos, roda sem gravar os PNG | o notebook nunca discorda do código; a banca vê os gráficos no GitHub sem rodar nada; o CI confere o "Run All" sem tocar nos gráficos dos dados reais |
| 04/11 | o diagrama de arquitetura é texto (Mermaid) dentro do README, e o PNG sai dele; um teste confere que ele só cita arquivos que existem | o GitHub desenha o Mermaid sozinho e o PR mostra a mudança como texto; uma figura só em imagem fica velha sem ninguém ver (lição de 29/10: documento velho confunde mais que documento nenhum) |
| 04/11 | a demo da banca roda no Mac do Eduardo, e o Miguel grava nele os vídeos v0 e final | é o único computador conferido com o compose, o Terraform e o Gemini (03/11); a banca vê o mesmo que o vídeo |
| 04/11 | o documento do projeto (MA6) passa ao Eduardo | o Marcos tinha 4 sessões (MA3 a MA6); o Eduardo escreveu a base (justificativa, ética, HISTORICO) |
| 04/11 | o documento é escrito em markdown (`docs/documentacao.md`) e o PDF é gerado dele | o PR mostra o que mudou, cada número tem a fonte ao lado (Apêndice A) e corrigir leva um minuto; o guia §6 pede PDF, o `requisitos_projeto.MD` aceita markdown: vale o mais exigente |
| 05/11 | escala errada no primeiro ano da empresa: corrigida só quando a receita **e** o ativo estão ~1.000 vezes menores que no ano seguinte (decisão do Marcos) | o primeiro ano não tem anterior para comparar; um salto de 1.000 vezes só na receita pode ser uma empresa que começou a operar, e multiplicar esse ano por 1.000 inventaria um número. Com os 2 sinais, a NTS é corrigida e mais nenhuma empresa muda |
| 05/11 | só o Eduardo edita o PLANO, o REQUISITOS e o HISTORICO, uma vez por dia; os outros PRs trazem "Para as notas" na descrição. O revisor faz uma rodada só, e até 16/11 só vira issue o que quebra a demo, um requisito do professor ou a regra de ouro. O `/fim-de-sessao` e o `/inicio-de-sessao` mostram quem tem PR aberto e quais arquivos ele mexe | todo PR reescrevia o mesmo parágrafo da seção 0, então todo merge virava conflito e ninguém sabia quem estava fazendo PR: o time esperava. 78 commits tinham mexido no PLANO e 39 no código. Com as notas num PR só, o conflito só acontece quando dois PRs mexem no mesmo arquivo, e o Claude mostra quando é o caso |

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
