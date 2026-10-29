---
name: fim-de-sessao
description: Fecha uma sessão de trabalho do Raio-X do começo ao fim, sem a pessoa precisar saber Git ou GitHub: roda os testes, confere o git status, atualiza a seção 0 do PLANO, o REQUISITOS e o HISTORICO, faz o commit, abre o PR, espera o CI, revisa o diff e faz o merge na main depois de um "pode". Use quando a pessoa disser que terminou a sessão ou a tarefa (ex.: "/fim-de-sessao", "acabei a MA2", "pode fechar").
---

# Fim de sessão

O time é iniciante em Git: você faz tudo e explica cada passo em uma linha simples. A pessoa só confirma **uma vez** (passo 6).
Siga os passos **em ordem** e pare no primeiro que falhar.

## 1. Onde estamos

- `git branch --show-current`. Se for `main`, crie agora a branch `pessoa-tarefa` com as mudanças (`git switch -c pessoa-tarefa`).
- Descubra qual sessão do `docs/PLANO.md` (ex.: MA2) foi feita. Se não estiver claro na conversa, pergunte.

## 2. Testes

- Rode `python -m pytest -q` (ou `~/bootcamp/bin/python -m pytest -q`, se não houver `.venv`) e mostre a última linha.
- Se algo falhar, **pare** e mostre o erro inteiro. Não feche sessão com teste vermelho.
- Se o comportamento mudou e nenhum teste novo ou atualizado entrou, escreva o teste antes de seguir (CLAUDE.md, regra 3).
- Se a tela mudou, abra a tela ou simule com o `AppTest` do Streamlit.

## 3. O que vai para o Git

- Rode `git status` e mostre a lista.
- **Pare** se aparecer `.env`, chave, qualquer coisa em `data/` (fora o `.gitkeep`), `.db`, `.zip` ou `.parquet`.
- Veja se algum arquivo é de outro dono (tabela "Estrutura e donos" do CLAUDE.md) ou se o `contratos.md` mudou.
  Se sim, o dono precisa dar o ok **no grupo** (WhatsApp) antes do merge: escreva para a pessoa a mensagem pronta para ela mandar.

## 4. Documentos de estado

- **`docs/PLANO.md`, seção 0:** data e hora aproximada; o que mudou, com prova (arquivo, linha ou comando); os testes
  (quantos passaram e quantos foram pulados); o próximo passo. Apague o que ficou velho, em vez de só acrescentar.
- **`docs/PLANO.md`, seção 3:** a coluna "status" da sessão (✅ feito, 🟡 em parte).
- **`docs/REQUISITOS.md`:** se a sessão fechou ou mudou uma linha, troque o status e escreva a prova.
- **`docs/HISTORICO.md`:** de 1 a 3 linhas no dia de hoje (o que mudou, em português simples, com o número do PR);
  se houve decisão, uma linha na tabela de decisões, com o porquê.
- Separe "verifiquei" de "suponho" em tudo o que escrever.

## 5. Commit, push e PR

- Commits pequenos, com mensagem em português que diga o que mudou.
- `git push -u origin pessoa-tarefa` e `gh pr create`, seguindo `.github/pull_request_template.md`:
  - "Feito com IA": o que a IA fez nesta sessão;
  - "O que eu entendi ou conferi": **pergunte à pessoa** e escreva o que ela disser, mesmo que seja "ainda não li". Não invente.
- Nunca `push --force`, `rebase` nem commit na `main`.

## 6. Revisão e merge

- Espere o CI: `gh pr checks <número> --watch`. Se aparecer "no checks reported", o CI ainda não começou: espere uns
  segundos e rode de novo. **Só faça o merge depois de ver `pass`** (em 29/10 o PR #15 foi mesclado antes do CI começar).
  Vermelho: mostre o erro, conserte na mesma branch e espere de novo.
- Revise o diff do PR você mesmo (`gh pr diff <número>`): procure dado ou chave, quebra da regra de ouro, mudança fora do
  combinado. Diga em 3 linhas o que o PR muda e o risco que você vê.
- Se mexeu em pasta de outro dono ou no `contratos.md`, confirme com a pessoa que o dono deu o ok no grupo.
- Peça **um "pode"** à pessoa. Com o "pode": `gh pr merge <número> --merge --delete-branch`.
- Se o GitHub recusar porque falta aprovação, a configuração da `main` ainda pede revisão: explique que outra pessoa do grupo
  precisa abrir o PR no navegador, clicar em "Files changed" → "Review changes" → "Approve" → "Submit review", e escreva
  a mensagem pronta para pedir isso. Depois do approve, faça o merge.
- Depois do merge: `git switch main` e `git pull`.

## 7. Fechar

Termine com 3 linhas: o link do PR (e se entrou na `main`), o próximo passo e o lembrete de usar `/clear`
(ou abrir uma sessão nova) antes da próxima tarefa.
