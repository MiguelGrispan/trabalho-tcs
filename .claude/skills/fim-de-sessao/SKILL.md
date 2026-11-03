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

- Rode `python -m pytest -q` (ou `~/bootcamp/bin/python -m pytest -q`, se não houver `.venv`; sem Python 3.14 na máquina,
  `docker compose run --rm tela python -m pytest -q`, depois de `docker compose build tela`) e mostre a última linha.
- Se algo falhar, **pare** e mostre o erro inteiro. Não feche sessão com teste vermelho.
- Se o comportamento mudou e nenhum teste novo ou atualizado entrou, escreva o teste antes de seguir (CLAUDE.md, regra 3).
- Se a tela mudou, abra a tela ou simule com o `AppTest` do Streamlit.

## 3. O que vai para o Git

- Rode `git status` e mostre a lista.
- **Pare** se aparecer `.env`, chave, qualquer coisa em `data/` (fora o `.gitkeep`), `.db`, `.zip` ou `.parquet`.
  O hook confere de novo na hora do commit (`.claude/hooks/guarda.py`): se ele bloquear, mostre a mensagem, tire o arquivo
  com `git restore --staged <arquivo>` e não contorne.
- Veja se algum arquivo é de outro dono (tabela "Estrutura e donos" do CLAUDE.md) ou se o `contratos.md` mudou.
  Se sim, o dono precisa dar o ok **no grupo** (WhatsApp) antes do merge: escreva para a pessoa a mensagem pronta para ela mandar.

## 4. Documentos de estado

- **Antes de escrever, releia `docs/professor/requisitos_projeto.MD` e `docs/professor/guia_projeto_final.pdf`.** Nenhuma nota
  pode dizer que algo exigido ali é opcional, extra ou cortável; toda frase sobre o que o professor exige cita o arquivo e o item.
- **Antes de reescrever a seção 0, confira o GitHub de novo** (a nota pode ter ficado velha durante a sessão): `git fetch --prune`,
  `git branch -r --no-merged origin/main` e, para cada branch, `gh pr list --head <branch> --state all`. Branch com commit novo e
  sem PR vira linha na seção 0 e issue para o dono (em 03/11, a MA3 ficou pronta numa branch sem PR, e a nota dizia que ela não existia).
- **`docs/PLANO.md`, seção 0:** data e hora aproximada; o que mudou, com prova (arquivo, linha ou comando); os testes
  (quantos passaram e quantos foram pulados); o próximo passo. Apague o que ficou velho, em vez de só acrescentar.
- **`docs/PLANO.md`, seção 3:** a coluna "status" da sessão (✅ feito, 🟡 em parte).
- **`docs/REQUISITOS.md`:** se a sessão fechou ou mudou uma linha, troque o status e escreva a prova.
- **`docs/HISTORICO.md`:** de 1 a 3 linhas no dia de hoje (o que mudou, em português simples, com o número do PR);
  se houve decisão, uma linha na tabela de decisões, com o porquê.
- Separe "verifiquei" de "suponho" em tudo o que escrever.

## 5. Commit, push e PR

- Commits pequenos, com mensagem em português que diga o que mudou.
- Mensagem ou descrição de PR que cita o `.env` ou um comando proibido (`rebase`, `push --force`…): o hook bloqueia o texto
  na linha de comando. Escreva com a ferramenta Write num arquivo fora do repositório e use `git commit -F <arquivo>` e
  `gh pr create --body-file <arquivo>`. O modelo de PR cita o `.env`: a descrição do PR vai sempre por arquivo.
- `git push -u origin pessoa-tarefa` e `gh pr create`, seguindo `.github/pull_request_template.md`:
  - "Feito com IA": o que a IA fez nesta sessão;
  - "O que eu entendi ou conferi": **pergunte à pessoa** e escreva o que ela disser, mesmo que seja "ainda não li". Não invente.
- Nunca `push --force`, `rebase` nem commit na `main`.

## 6. Revisão e merge

- Espere o CI: `gh pr checks <número> --watch`. Se aparecer "no checks reported", o CI ainda não começou: espere uns
  segundos e rode de novo. **Só faça o merge depois de ver `pass`** (em 29/10 o PR #15 foi mesclado antes do CI começar).
  Vermelho: mostre o erro, conserte na mesma branch e espere de novo.
- Peça ao subagent `revisor` (`.claude/agents/revisor.md`) a revisão do PR `<número>` e mostre a resposta dele. Ele não viu a
  sessão e não torce pelo código: enxerga o que quem escreveu deixa passar. Se ele disser **BLOQUEIA**, pare, conserte e peça
  de novo. Os itens de **ATENÇÃO** nos arquivos deste PR: corrija na mesma branch antes do merge (commit "Achados do revisor"),
  espere o CI de novo, peça ao `revisor` uma segunda olhada só nas correções e diga à pessoa o que mudou; o que não der para
  corrigir agora vira issue (abaixo). Depois, diga em 3 linhas
  o que o PR muda e o risco que sobrou.
- **Erro achado fora do PR, na pasta de outro dono** (na sessão ou pelo revisor): não conserte lá (CLAUDE.md, regra 1). Abra uma
  issue para o dono e escreva a sessão dele no PLANO (desde 03/11; ex.: issues #38 e #39 → MG4b do Miguel):
  - `gh issue create --assignee <login> --label bug --body-file <arquivo>` (`--label documentation` se o erro é de texto). O título
    vai na linha de comando: sem `.env` nem comando proibido nele. O corpo, escrito pela ferramenta Write fora do repositório, nunca
    leva chave, senha nem dado pessoal (o repositório vai para o professor) e diz: o que acontece, onde (arquivo e linha), por que importa na banca (arquivo do professor e item), como reproduzir,
    sugestão de conserto e prazo. Logins: Marcos `MarcosIurak`, Miguel `MiguelGrispan`, Náthally `Hawkie06`, Eduardo `Mindoim`;
  - no `docs/PLANO.md`: uma linha nova na tabela da pessoa (seção 3, ex.: MG4b), com o número das issues e o "pronto quando",
    a data no calendário e uma linha no "Próximo passo de cada um" (seção 0);
  - entregue à pessoa a mensagem pronta para o dono, com os links das issues (a Náthally não usa terminal: ela vê pela aba
    "Issues" do GitHub ou pela mensagem);
  - mudou o PLANO depois do CI? É commit novo: espere o `pass` de novo antes do merge.
- Se mexeu em pasta de outro dono ou no `contratos.md`, confirme com a pessoa que o dono deu o ok no grupo.
- Peça **um "pode"** à pessoa. Com o "pode": `gh pr merge <número> --merge --delete-branch`. O Claude Code ainda pede
  permissão antes (regra `ask` do `.claude/settings.json`): é a segunda trava, para o merge nunca sair sem ela ver. Recusou, pare.
- Se o GitHub recusar o merge, mostre a mensagem inteira e pare: não tente contornar.
- Depois do merge: `git switch main` e `git pull`.

## 7. Fechar

Termine com 3 linhas: o link do PR (e se entrou na `main`), o próximo passo e o lembrete de usar `/clear`
(ou abrir uma sessão nova) antes da próxima tarefa.
