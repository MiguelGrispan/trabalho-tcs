---
name: fim-de-sessao
description: Fecha uma sessão de trabalho do Raio-X como o CLAUDE.md manda: roda os testes, confere o git status, atualiza a seção 0 do PLANO e o REQUISITOS, faz o commit e abre o PR com o modelo do projeto. Use quando a pessoa disser que terminou a sessão ou a tarefa (ex.: "/fim-de-sessao", "acabei a MA2", "pode fechar").
---

# Fim de sessão

Fecha a sessão para que a próxima comece do lugar certo. Siga os passos **em ordem** e pare no primeiro que falhar.

## 1. Onde estamos

- `git branch --show-current`. Se for `main`, **pare**: crie antes a branch `pessoa-tarefa` (CLAUDE.md, regra 8).
- Descubra qual sessão do `docs/PLANO.md` (ex.: MA2) foi feita. Se não estiver claro na conversa, pergunte.

## 2. Testes

- Rode `python -m pytest -q` (ou `~/bootcamp/bin/python -m pytest -q`, se não houver `.venv`) e mostre a última linha.
- Se algo falhar, **pare** e mostre o erro inteiro. Não feche sessão com teste vermelho.
- Se o comportamento mudou e nenhum teste novo ou atualizado entrou, avise: o CLAUDE.md exige teste no mesmo PR.
- Se a tela mudou, lembre a pessoa de abrir a tela também.

## 3. O que vai para o Git

- Rode `git status` e leia a lista **com** a pessoa.
- **Pare** se aparecer `.env`, chave, qualquer coisa em `data/` (fora o `.gitkeep`), `.db`, `.zip` ou `.parquet`.
- Confira se algum arquivo é de outro dono (tabela "Estrutura e donos" do CLAUDE.md). Se for, pergunte se foi combinado.

## 4. Documentos de estado

- **`docs/PLANO.md`, seção 0:** data e hora aproximada; o que mudou nesta sessão, com prova (arquivo, linha ou comando);
  os testes (quantos passaram e quantos foram pulados); o próximo passo de quem fez a sessão.
  Apague o que ficou velho, em vez de só acrescentar.
- **`docs/PLANO.md`, seção 3:** a coluna "status" da sessão (✅ feito, 🟡 em parte).
- **`docs/REQUISITOS.md`:** se a sessão fechou ou mudou uma linha, troque o status e escreva a prova.
- Separe "verifiquei" de "suponho" em tudo o que escrever.

## 5. Commit, push e PR

- Commits pequenos, um por passo, com mensagem em português que diga o que mudou.
- Antes de `git push` e de abrir o PR, mostre o resumo e **peça confirmação**.
- Abra o PR com `gh pr create`, seguindo `.github/pull_request_template.md`:
  - "Feito com IA": o que a IA fez nesta sessão;
  - "Eu conferi": **pergunte à pessoa** o que ela conferiu. Não preencha por ela.
- Diga quem revisa (PLANO, seção 2: quem **recebe** o contrato).
- Nunca `push --force`, `rebase` nem commit na `main`.

## 6. Fechar

Termine com 3 linhas: o link do PR, o próximo passo e o lembrete de usar `/clear` (ou abrir uma sessão nova) antes da próxima tarefa.
