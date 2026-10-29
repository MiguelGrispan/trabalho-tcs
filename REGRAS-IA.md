# Regras de uso de IA no projeto

Valem para os quatro (Marcos, Eduardo, Náthally, Miguel) e para qualquer ferramenta: ChatGPT, Gemini, Claude, Claude Code, Codex, Copilot.
O Claude Code lê o `CLAUDE.md` e o Codex lê o `AGENTS.md`; os dois apontam para este arquivo.
A banca avalia como usamos IA para programar e a governança (segurança de dados, alucinação, uso responsável). Estas regras são a nossa resposta.

## 1. O que nunca vai para uma IA

- Chave de API, senha, token ou o conteúdo do `.env`.
- Dado interno da TCS, de cliente ou de banco.
- Dado pessoal de quem respondeu entrevista ou formulário (nome, e-mail, telefone).

Pode: dados públicos da CVM, o código do projeto, produtos fictícios.
Se uma chave vazou (colou num chat, subiu no Git): avise o grupo e troque a chave no Google AI Studio na hora.

## 2. O que nunca vai para o Git

- `.env` (já está no `.gitignore`).
- Dados brutos da CVM e arquivos gerados (`contas.csv`, `indicadores.csv`, `catalogo.db`, os zips da DFP). Ficam em `data/`, que o Git ignora.
- Arquivos acima de 10 MB.

Antes de todo commit, rode `git status` e leia a lista. Se aparecer algo que não deveria, pare.

## 3. Como pedir para a IA

- Diga o que quer, o que entra, o que sai e como saber que ficou pronto.
- Uma tarefa pequena por vez, dizendo quais arquivos ela pode mexer.
- Para entender código: "explique para iniciante, não altere nada".
- Se a tarefa envolve a parte de outra pessoa, mande junto o `contratos.md`.

## 4. Antes de aceitar o que a IA fez

- Rode. Código que não rodou não está pronto (`python -m pytest -q`).
- Leia o que mudou (`git diff` ou o painel de Controle de Código do VS Code).
- Peça "explique o que você mudou e por quê". Se você não consegue explicar, não suba.
- Desconfie de: número sem fonte; "deve funcionar"; biblioteca ou função que você nunca viu; arquivo que a IA diz ter lido mas não abriu; resposta que muda quando você pergunta de novo.
- Número que a IA calculou ou "achou": confira 2 ou 3 valores na fonte (CVM ou site de RI da empresa).

## 5. Git do time

- **No Claude Code, o Git é com ele:** `/inicio-de-sessao` no começo e `/fim-de-sessao` no fim. Ele cria a branch, faz os commits,
  abre o PR, espera o CI, lê o diff e faz o merge depois do seu "pode". Os combinados e o porquê: `docs/PLANO.md`, seção 2;
  os comandos, um por um: `aprender/COMANDOS.md`, seção 7.
- Uma branch curta por tarefa (uma sessão do `docs/PLANO.md`), sempre a partir da `main` atualizada, com nome `pessoa-tarefa`.
- Faça commit antes de pedir uma mudança grande à IA: se der errado, dá para voltar. Commits pequenos, com mensagem dizendo o que mudou.
- Nunca `rebase` nem `push --force`: reescrevem a história e podem apagar o trabalho de um colega. Para trazer a `main`, `git merge main`.
- Na `main` só entra por pull request, com os testes passando (o CI roda sozinho no PR). Não precisa de aprovação no GitHub:
  o CI e a leitura do diff pelo Claude Code são a revisão. Quem abriu o PR faz o merge (tipo "merge commit").
  Mexeu no `contratos.md` ou na pasta de outro dono? Antes do merge, o dono dá o ok no grupo.
- Quem não programa com IA sobe arquivos pelo navegador: no GitHub, com a `main` selecionada, "Add file → Upload files",
  escolha "Create a new branch" e abra o PR.

## 6. Regras do produto (não negociáveis)

- O LLM nunca escreve números. Ele usa marcadores (`{margem_ebit}`) e o validador remove qualquer dígito fora deles. Nenhuma mudança pode quebrar isso.
- Acima / abaixo / em linha do grupo é calculado por código, não pela IA.
- A IA auditora dos dados só aponta suspeitas. Quem decide e corrige é uma pessoa.
- Formato de contrato (`contratos.md`) só muda avisando antes quem recebe.
- Rodar o Gemini em lote (mais de 10 chamadas) só avisando o grupo: gasta crédito.

## 7. Registro para a banca

No pull request, escreva em 2 linhas o que foi gerado com IA e o que você entendeu ou conferiu (vale "ainda não li";
não vale inventar). Isso vira a seção "Como usamos IA para programar" do README.
Os campos e o checklist do PR estão no modelo (`.github/pull_request_template.md`), e o `/fim-de-sessao` confere cada item antes do merge.
