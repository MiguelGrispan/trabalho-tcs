---
name: fim-de-sessao
description: Fecha uma sessão de trabalho do Raio-X do começo ao fim, sem a pessoa precisar saber Git ou GitHub: roda os testes, confere o git status, escreve no PR o que mudou (só o Eduardo atualiza o PLANO, o REQUISITOS e o HISTORICO), faz o commit, abre o PR, espera o CI, revisa o diff numa rodada e faz o merge na main depois de um "pode". Use quando a pessoa disser que terminou a sessão ou a tarefa (ex.: "/fim-de-sessao", "acabei a MA2", "pode fechar").
---

# Fim de sessão

O time é iniciante em Git: você faz tudo e explica cada passo em uma linha simples. A pessoa só confirma **uma vez** (passo 6).
Siga os passos **em ordem** e pare no primeiro que falhar.

## 1. Onde estamos

- `git branch --show-current`. Se for `main`, crie agora a branch `pessoa-tarefa` com as mudanças (`git switch -c pessoa-tarefa`).
- Descubra qual sessão do `docs/PLANO.md` (ex.: MA2) foi feita. Se não estiver claro na conversa, pergunte.
- Descubra quem é a pessoa: `gh api user --jq .login` (logins no passo 6). O passo 4 muda se é o Eduardo (`Mindoim`) ou não;
  na dúvida, trate como não-Eduardo.

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

## 4. O que mudou: na descrição do PR (as notas do projeto são só do Eduardo)

**Por quê (decidido em 05/11):** todo PR reescrevia a seção 0 do PLANO, o REQUISITOS e o HISTORICO. Com três pessoas ao mesmo
tempo, o mesmo parágrafo mudava em três branches e todo merge virava conflito (os PRs #46 a #59 mexeram todos nesses 3 arquivos).

- **Antes de escrever qualquer coisa, releia `docs/professor/requisitos_projeto.MD` e `docs/professor/guia_projeto_final.pdf`.**
  Nenhum texto pode dizer que algo exigido ali é opcional, extra ou cortável; toda frase sobre o que o professor exige cita o
  arquivo e o item. Separe "verifiquei" de "suponho".
- **A pessoa não é o Eduardo:** não mexa em `docs/PLANO.md`, `docs/REQUISITOS.md` nem `docs/HISTORICO.md` (nem na coluna de status).
  Se o `git status` mostra mudança neles, não ponha no commit e pergunte à pessoa o que fazer. Escreva o que mudou na seção
  **"Para as notas"** da descrição do PR (passo 5); o Eduardo leva para as notas.
  **Branch que já tem commit nessas notas** (feito antes desta regra): copie o que ela escreveu nelas para "Para as notas" e
  volte os 3 arquivos para a versão da `main`: `git fetch`, `git checkout origin/main -- docs/PLANO.md docs/REQUISITOS.md
  docs/HISTORICO.md` e um commit "Notas saem do PR: só o Eduardo edita". Assim o PR não conflita com ninguém nas notas.
- **A pessoa é o Eduardo:** ele atualiza as notas **uma vez por dia**, num PR dele (pode ser o da própria sessão). Já atualizou
  hoje e nada entrou na `main` depois? Não mexa. Se for atualizar:
  - confira o GitHub: `git fetch --prune`, `git branch -r --no-merged origin/main` e, para cada branch, `gh pr list --head <branch>
    --state all` (branch com commit novo e sem PR vira linha na seção 0; em 03/11, a MA3 ficou pronta numa branch sem PR);
  - a seção 0 diz o último PR levado para as notas ("último PR levado: #N"). Para cada PR mesclado com número maior
    (`gh pr list --state all --limit 30`, coluna do estado), leia "Para as notas" e "Achados não consertados" (`gh pr view <número>`);
  - **`docs/PLANO.md`, seção 0:** data e hora aproximada; "último PR levado: #N"; o que mudou, com prova; os testes; o próximo
    passo de cada um; as issues novas. Apague o que ficou velho, em vez de só acrescentar;
  - **`docs/PLANO.md`, seção 3:** a coluna "status" das sessões que terminaram (✅ feito, 🟡 em parte);
  - **`docs/REQUISITOS.md`:** se um PR fechou ou mudou uma linha, troque o status e escreva a prova;
  - **`docs/HISTORICO.md`:** de 1 a 3 linhas no dia (o que mudou, em português simples, com os números dos PRs); decisão nova
    vira uma linha na tabela de decisões, com o porquê.

## 5. Commit, push e PR

- Commits pequenos, com mensagem em português que diga o que mudou.
- Mensagem ou descrição de PR que cita o `.env` ou um comando proibido (`rebase`, `push --force`…): o hook bloqueia o texto
  na linha de comando. Escreva com a ferramenta Write num arquivo fora do repositório e use `git commit -F <arquivo>` e
  `gh pr create --body-file <arquivo>`. O modelo de PR cita o `.env`: a descrição do PR vai sempre por arquivo.
- `git push -u origin pessoa-tarefa` e `gh pr create`, seguindo `.github/pull_request_template.md`:
  - "Feito com IA": o que a IA fez nesta sessão;
  - "O que eu entendi ou conferi": **pergunte à pessoa** e escreva o que ela disser, mesmo que seja "ainda não li". Não invente;
  - "Para as notas": a sessão e o status (✅ ou 🟡), o que mudou com prova (arquivo, linha ou comando), os testes (quantos
    passaram e quantos foram pulados, em qual máquina), a linha do `docs/REQUISITOS.md` afetada (ou "nenhuma") e o próximo passo.
- Nunca `push --force`, `rebase` nem commit na `main`.

## 6. Revisão (uma rodada) e merge

- **Ninguém espera ninguém.** Mostre à pessoa quem tem PR aberto agora e o que ele mexe:
  `gh pr list --state open --json number,title,author,files --jq '.[] | "#\(.number) \(.author.login): \(.title) · \([.files[].path] | join(", "))"'`
  (logins na lista de issues, abaixo). Tire o próprio PR da lista e compare com os arquivos dele (`gh pr diff <número> --name-only`):
  - **nenhum arquivo em comum:** diga "pode seguir, não precisa esperar ninguém". Os dois PRs entram na `main` sem conflito;
  - **arquivo em comum:** diga quem é o dono do outro PR e qual arquivo. Quem terminar primeiro faz o merge; o outro faz
    `git fetch` e `git merge origin/main` na própria branch e roda os testes. Conflito: `git merge --abort` e a pessoa fala com o
    dono do arquivo (conflito nas 3 notas: quem resolve é o Eduardo).
- Se o `gh pr merge` recusar porque a branch está desatualizada: `git fetch`, `git merge origin/main`, testes, `git push` e espere
  o CI de novo. Sem conflito, não precisa falar com ninguém.
- Espere o CI: `gh pr checks <número> --watch`. Se aparecer "no checks reported", o CI ainda não começou: espere uns
  segundos e rode de novo. **Só faça o merge depois de ver `pass`** (em 29/10 o PR #15 foi mesclado antes do CI começar).
  Vermelho: mostre o erro, conserte na mesma branch e espere de novo.
- Peça ao subagent `revisor` (`.claude/agents/revisor.md`) a revisão do PR `<número>` e mostre a resposta dele. Ele não viu a
  sessão e não torce pelo código: enxerga o que quem escreveu deixa passar. **É uma rodada só:**
  - **BLOQUEIA:** pare, conserte na mesma branch, espere o CI e peça ao `revisor` que confira só esse conserto;
  - **ATENÇÃO que quebra a demo, um requisito do professor ou a regra de ouro:** conserte na mesma branch (commit "Achados do
    revisor") e espere o CI de novo, sem pedir outra olhada;
  - **o resto** (texto, nota, estilo, melhoria): não vira commit. Vira uma linha em "Achados não consertados", na descrição do
    PR (`gh pr edit <número> --body-file <arquivo>`).
  Depois, diga em 3 linhas o que o PR muda e o risco que sobrou.
- **Erro achado fora do PR, na pasta de outro dono** (na sessão ou pelo revisor): não conserte lá (CLAUDE.md, regra 1).
  - **Até a entrega (16/11), só vira issue o que quebra a demo, um requisito do professor ou a regra de ouro.** Texto que
    contradiz os arquivos do professor ou deixa um entregável errado (README, documento, deck) conta como requisito: vira issue.
    O resto (nota, frase de guia, estilo) vai para "Achados não consertados".
  - A issue: `gh issue create --assignee <login> --label bug --body-file <arquivo>`. O título vai na linha de comando: sem `.env`
    nem comando proibido nele. O corpo, escrito pela ferramenta Write fora do repositório, nunca leva chave, senha nem dado pessoal
    (o repositório vai para o professor) e diz: o que acontece, onde (arquivo e linha), por que importa na banca (arquivo do
    professor e item), como reproduzir, sugestão de conserto e prazo. Logins: Marcos `MarcosIurak`, Miguel `MiguelGrispan`,
    Náthally `Hawkie06`, Eduardo `Mindoim`;
  - não escreva a sessão nova no PLANO: ponha o número da issue em "Para as notas", e o Eduardo a põe no PLANO na próxima atualização;
  - entregue à pessoa a mensagem pronta para o dono, com o link da issue (a Náthally não usa terminal: ela vê pela aba
    "Issues" do GitHub ou pela mensagem).
- Commit novo depois do CI? Espere o `pass` de novo antes do merge.
- Se mexeu em pasta de outro dono ou no `contratos.md`, confirme com a pessoa que o dono deu o ok no grupo.
- Peça **um "pode"** à pessoa. Com o "pode": `gh pr merge <número> --merge --delete-branch`. O Claude Code ainda pede
  permissão antes (regra `ask` do `.claude/settings.json`): é a segunda trava, para o merge nunca sair sem ela ver. Recusou, pare.
- Se o GitHub recusar o merge, mostre a mensagem inteira e pare: não tente contornar.
- Depois do merge: `git switch main` e `git pull`.

## 7. Fechar

Termine com 3 linhas: o link do PR (e se entrou na `main`), o próximo passo e o lembrete de usar `/clear`
(ou abrir uma sessão nova) antes da próxima tarefa.
