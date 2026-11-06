# Entregas da banca · índice

Abra no VS Code com **Cmd+Shift+V** (preview): cada link abre o arquivo do repositório.
Entrega: **seg 16/11/2026**, 48 h antes da banca (`guia_projeto_final.pdf` §6). Atualizado em sex 06/11/2026.

Status: **pronto** = existe e foi conferido · **rascunho** = existe, mas falta conteúdo · **a confirmar** = está fora do repositório,
ainda falta ou depende de uma pessoa confirmar. Só os itens prontos estão marcados.

> **Atenção:** o repositório é **privado** e, em 06/11, o professor não está entre os colaboradores (Miguel, Marcos, Náthally e
> Eduardo). Sem o acesso dele, nenhum item abaixo chega à banca.

## Prazo e acesso

- [ ] **Data de entrega** · a confirmar · seg 16/11/2026, se a banca for mesmo na qua 18/11/2026. Falta o professor confirmar
  a data e o horário da banca. Arquivo ou link a inserir: ________
- [ ] **Acesso do professor ao GitHub** · a confirmar · `MiguelGrispan/trabalho-tcs` é privado. Falta o Miguel (admin) convidar
  o login do professor, ou conferir se já há convite, e o professor aceitar. Arquivo ou link a inserir: ________

## Repositório (`requisitos_projeto.MD`, Documentação e Aplicação; guia §6, item 1)

- [ ] **README** · a confirmar · [README.md](../README.md). Tem tema, objetivo, tecnologias, arquitetura e como rodar; falta
  seguir o README do zero num computador limpo (ED10).
- [x] **Arquitetura** · pronto · [docs/arquitetura.png](arquitetura.png) e o diagrama Mermaid na seção "Arquitetura" do
  [README.md](../README.md). Falta só olhar o Mermaid desenhado na página do GitHub.
- [x] **Terraform** · pronto · [infra/main.tf](../infra/main.tf), [infra/variables.tf](../infra/variables.tf),
  [infra/outputs.tf](../infra/outputs.tf), [infra/providers.tf](../infra/providers.tf), [infra/versions.tf](../infra/versions.tf);
  o mesmo pelo [docker-compose.yml](../docker-compose.yml) e o [Dockerfile](../Dockerfile). Conferido no Mac em 03/11.
- [x] **Prompts usados no vibecoding** · pronto · [CLAUDE.md](../CLAUDE.md), [AGENTS.md](../AGENTS.md),
  [REGRAS-IA.md](../REGRAS-IA.md), skills ([inicio-de-sessao](../.claude/skills/inicio-de-sessao/SKILL.md),
  [fim-de-sessao](../.claude/skills/fim-de-sessao/SKILL.md), [explicar](../.claude/skills/explicar/SKILL.md)),
  [revisor](../.claude/agents/revisor.md), [settings.json](../.claude/settings.json), [guarda.py](../.claude/hooks/guarda.py),
  [pre-commit](../.githooks/pre-commit), [modelo de PR](../.github/pull_request_template.md). O prompt do produto (o que o
  Gemini recebe): [avaliacao/regras_prompt.md](../avaliacao/regras_prompt.md).

## Documento do projeto (guia §6, item 2)

- [ ] **Documento em Markdown** · rascunho · [docs/documentacao.md](documentacao.md). Rascunho 2 (06/11), com BPMN, arquitetura
  e EDA; faltam o ROI, o texto final de ética e as respostas do professor (Apêndice B do documento).
- [ ] **Documento em PDF** · rascunho · [docs/documentacao.pdf](documentacao.pdf). Gerado do Markdown em 06/11 (21 páginas);
  precisa ser gerado de novo depois de cada mudança no `.md`.
- [x] **BPMN 2.0** · pronto · [imagem](bpmn/raio-x-comercial.png) e [arquivo editável](bpmn/raio-x-comercial.bpmn)
  (PRs #52 e #65). Também na seção 4 do documento.
- [x] **EDA** · pronto · [notebooks/eda.ipynb](../notebooks/eda.ipynb) e os gráficos
  [nulos](graficos/eda_1_nulos.png), [distribuições](graficos/eda_2_distribuicoes.png),
  [extremos](graficos/eda_3_extremos.png), [cobertura](graficos/eda_4_cobertura.png). Também na seção 3 do documento.
- [x] **Avaliação dos dez casos** · pronto · [casos](../avaliacao/casos_avaliacao.csv), [resultados](../avaliacao/resultados.csv)
  (0 trechos removidos, 2,15 s e US$ 0,001185 em média) e [conferência contra o RI](../avaliacao/conferencia.csv). O "8 de 10"
  da conferência manual está no `revisao_manual.md`, que ainda não está na `main` (branch `feat/metricas`).
  Arquivo ou link a inserir (se a Náthally subir): ________
- [ ] **Medição de ROI** · a confirmar · não existe. Falta cronometrar 1 raio-x montado à mão contra a ferramenta (NA3).
  Arquivo ou link a inserir: ________
- [ ] **Ética** · rascunho · [docs/etica.md](etica.md) e a seção 7 do documento. Falta o texto final da Náthally com a
  viabilidade (NA5).

## Apresentação (guia §3 e §6, item 3)

- [ ] **Deck** · a confirmar · o grupo diz que o deck existe, mas ele não está no repositório. Falta colar o link e conferir se a
  versão usa os números do documento de 06/11 (8 de 10, 0 removidos, 2,15 s, US$ 0,001185, k = 4, silhueta 0,286).
  Arquivo ou link a inserir: ________ · versão conferida em: ________
- [ ] **Vídeo de reserva da demo** · a confirmar · não está no repositório. Falta gravar no Mac do Eduardo (MG6) e guardar em
  2 lugares. Arquivo ou link a inserir: ________
- [ ] **Ensaio de até 20 minutos** · a confirmar · falta registrar data, tempo medido e quem falou cada parte (guia §3).
  Arquivo ou link a inserir: ________

## Fora da lista, mas pode confundir a banca

- [ ] O arquivo antigo `docs/Raio-X Comercial.pdf` (30/10) ainda está no repositório e fala de SQLite, que o professor não
  aceita. Falta o grupo decidir se ele sai antes da entrega.
