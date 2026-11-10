# Entregas da banca · índice

Abra no VS Code com **Cmd+Shift+V** (preview): cada link abre o arquivo do repositório.
Entrega: **ter 17/11/2026**, 48 h antes da banca de qui 19/11/2026 (`guia_projeto_final.pdf` §6). Atualizado em 09/11/2026; código congelado na [v1.0.1](https://github.com/MiguelGrispan/trabalho-tcs/tree/v1.0.1): a `v1.0` (commit `2c3e942`, PR #67) mais o conserto do validador da revisão final (issue #69).

Status: **pronto** = existe e foi conferido · **rascunho** = existe, mas falta conteúdo · **a confirmar** = está fora do repositório,
ainda falta ou depende de uma pessoa confirmar. Só os itens prontos estão marcados.

> **Atenção:** o repositório é **privado** e, em 07/11, o professor não está entre os colaboradores (Miguel, Marcos, Náthally e
> Eduardo). Sem o acesso dele, nenhum item abaixo chega à banca.

## Prazo e acesso

- [ ] **Data de entrega** · a confirmar · ter 17/11/2026 (banca em qui 19/11/2026, dita pelo professor ao Eduardo (registrada em 09/11)). Falta confirmar o horário e o prazo exato
  a data e o horário da banca. Arquivo ou link a inserir: ________
- [ ] **Acesso do professor ao GitHub** · a confirmar · `MiguelGrispan/trabalho-tcs` é privado. Falta o Miguel (admin) convidar
  o login do professor, ou conferir se já há convite, e o professor aceitar. Arquivo ou link a inserir: ________

## Repositório (`requisitos_projeto.MD`, Documentação e Aplicação; guia §6, item 1)

- [ ] **README** · a confirmar · [README.md](../README.md). Tem tema, objetivo, tecnologias, arquitetura, como rodar e, após os PRs #75–#77, como carregar e conferir as fontes da DFP. Em 07/11, instalação de dependências num venv vazio e build Docker conferidos no mesmo Mac. Falta outra pessoa seguir o README em outro computador (ED10).
- [x] **Arquitetura** · pronto · [docs/arquitetura.png](arquitetura.png) e o diagrama Mermaid na seção "Arquitetura" do
  [README.md](../README.md). O Mermaid renderizado foi identificado na árvore de acessibilidade do Chrome em 07/11; sem revisão visual de layout.
- [x] **Terraform** · pronto · [infra/main.tf](../infra/main.tf), [infra/variables.tf](../infra/variables.tf),
  [infra/outputs.tf](../infra/outputs.tf), [infra/providers.tf](../infra/providers.tf), [infra/versions.tf](../infra/versions.tf);
  o mesmo pelo [docker-compose.yml](../docker-compose.yml) e o [Dockerfile](../Dockerfile). Conferido no Mac em 03/11.
- [x] **Prompts usados no vibecoding** · pronto · [CLAUDE.md](../CLAUDE.md), [AGENTS.md](../AGENTS.md),
  [REGRAS-IA.md](../REGRAS-IA.md), skills ([inicio-de-sessao](../.claude/skills/inicio-de-sessao/SKILL.md),
  [fim-de-sessao](../.claude/skills/fim-de-sessao/SKILL.md), [explicar](../.claude/skills/explicar/SKILL.md)),
  [revisor](../.claude/agents/revisor.md), [settings.json](../.claude/settings.json), [guarda.py](../.claude/hooks/guarda.py),
  [pre-commit](../.githooks/pre-commit), [modelo de PR](../.github/pull_request_template.md). Esses arquivos existem; a pergunta 2 ao professor (se também quer prompts digitados) continua em aberto no REQUISITOS. O prompt do produto (o que o
  Gemini recebe): [avaliacao/regras_prompt.md](../avaliacao/regras_prompt.md).

## Documento do projeto (guia §6, item 2)

- [ ] **Documento em Markdown** · rascunho · [docs/documentacao.md](documentacao.md). Rascunho 5 (10/11), com BPMN, arquitetura, EDA e o fluxo de conferência das contas e do link da CVM; faltam o ROI, o texto final de ética e as respostas do professor (Apêndice B do documento).
- [ ] **Documento em PDF** · rascunho · [docs/documentacao.pdf](documentacao.pdf). Regerado em 10/11 (ED18, 22 páginas, com as fontes e o BPMN da MA8); precisa ser gerado de novo depois da entrada do ROI e da ética.
- [x] **BPMN 2.0** · pronto · [imagem](bpmn/raio-x-comercial.png) e [arquivo editável](bpmn/raio-x-comercial.bpmn)
  (PRs #52 e #65). Também na seção 4 do documento.
- [x] **EDA** · pronto · [notebooks/eda.ipynb](../notebooks/eda.ipynb) e os gráficos
  [nulos](graficos/eda_1_nulos.png), [distribuições](graficos/eda_2_distribuicoes.png),
  [extremos](graficos/eda_3_extremos.png), [cobertura](graficos/eda_4_cobertura.png). Na `main` desde o #54, atualizada no #59 e reexecutada com dados reais em 07/11: 15 células de código, quatro figuras e nenhum erro. Notebook/PNG originais preservados. Também na seção 3 do documento.
- [x] **Avaliação dos dez casos** · pronto · [casos](../avaliacao/casos_avaliacao.csv), [resultados](../avaliacao/resultados.csv)
  (0 trechos removidos, 2,15 s e US$ 0,001185 em média) e [conferência contra o RI](../avaliacao/conferencia.csv). O "8 de 10"
  da conferência manual está no `revisao_manual.md`, que ainda não está na `main` (branch `feat/metricas`).
  Arquivo ou link a inserir (se a Náthally subir): ________
- [ ] **Medição de ROI** · a confirmar · não existe. Falta cronometrar 1 raio-x montado à mão contra a ferramenta (NA3).
  Arquivo ou link a inserir: ________
- [ ] **Ética** · rascunho · [docs/etica.md](etica.md) e a seção 7 do documento. Falta o texto final da Náthally com a
  viabilidade (NA5).

## Apresentação (guia §3 e §6, item 3)

- [x] **Conteúdo técnico do Eduardo** · preparado · [dois slides, falas e perguntas de defesa](conteudo_eduardo.md). Falta incorporar ao deck e ensaiar; o arquivo também contém rascunho não enviado ao professor.

- [ ] **Deck** · a confirmar · o grupo diz que o deck existe, mas ele não está no repositório. Falta colar o link e conferir se a
  versão usa os números do documento de 06/11 (8 de 10, 0 removidos, 2,15 s, US$ 0,001185, k = 4, silhueta 0,286).
  Arquivo ou link a inserir: ________ · versão conferida em: ________
- [ ] **Vídeo de reserva da demo** · a confirmar · não está no repositório. Falta gravar no Mac do Eduardo (MG6) e guardar em
  2 lugares. Arquivo ou link a inserir: ________
- [ ] **Ensaio de até 18 minutos (alvo 15)** · a confirmar · falta registrar data, tempo medido e quem falou cada parte (guia §3; tempos em `docs/tempo_apresentacao.md`).
  Arquivo ou link a inserir: ________

## Fechamento técnico de 07/11/2026

- [x] **Ambiente e banco:** venv vazio com dependências instaladas, PostgreSQL ativo e testes locais aprovados; resultados completos no [PR #67](https://github.com/MiguelGrispan/trabalho-tcs/pull/67).
- [x] **Demo funcional:** WEG, Embraer e Ambev pelo Streamlit AppTest, dados reais, seis indicadores e cinco parecidas; erro de IA simulado também registra a consulta com custo zero. Sem inspeção visual da demo.
- [x] **Versão congelada:** PR #67 mesclado, CI verde e tag anotada `v1.0` publicada em 07/11/2026, apontando para `2c3e942`. Em 09/11, a `v1.0.1` (só o conserto do validador, com teste) substitui a `v1.0` como versão da banca. A versão fixa o código; PDF/deck e ensaios continuam sendo finalizados.
