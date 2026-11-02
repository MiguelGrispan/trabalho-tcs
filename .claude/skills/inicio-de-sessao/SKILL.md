---
name: inicio-de-sessao
description: Começa uma sessão de trabalho do Raio-X sem a pessoa precisar saber Git: atualiza a main, cria a branch da tarefa, lê os arquivos do professor (docs/professor/) e a seção 0 do PLANO, confere o GitHub e diz o que mudou e o que fazer. Use no começo de qualquer tarefa (ex.: "/inicio-de-sessao MA2", "vou fazer a MG2", "bom dia, o que eu faço hoje?").
---

# Início de sessão

O time é iniciante em Git. Você faz o Git; a pessoa só diz qual tarefa vai fazer. Explique cada passo em uma linha simples.

## 1. Quem e qual tarefa

- Descubra quem é a pessoa (Marcos, Miguel, Eduardo ou Náthally) e o código da sessão no `docs/PLANO.md`, seção 3 (ex.: MA2).
  Se ela não disse, pergunte. Se ela não sabe, mostre as sessões dela que ainda não têm ✅ e sugira a primeira.

## 2. Git (você faz)

- `git status`. Se houver mudança sem commit, **pare** e pergunte o que fazer com ela (guardar num commit, num `git stash` ou descartar).
  Nunca descarte sem a pessoa dizer.
- `git switch main` e `git pull`.
- `git config core.hooksPath .githooks`: liga a conferência do commit pelo próprio Git (`.githooks/pre-commit`), que vale também
  fora do Claude Code. Vale só neste repositório; diga à pessoa em uma linha o que é.
- `git switch -c pessoa-tarefa` (ex.: `marcos-postgres`). Hífen, não barra. Se a branch já existe, pergunte se é para continuar nela
  (`git switch pessoa-tarefa` e `git merge main`).
- Nunca `rebase`, `push --force` nem commit na `main`.

## 3. Situação

- **Primeiro, os arquivos do professor, inteiros:** `docs/professor/requisitos_projeto.MD` e `docs/professor/guia_projeto_final.pdf`
  (o PDF com a ferramenta Read). Eles valem mais que o CLAUDE.md, o PLANO e o REQUISITOS; quando os dois diferem, vale o mais
  exigente (ex.: o Terraform é obrigatório). Se uma nota contradiz esses arquivos, avise a pessoa antes de seguir.
- Leia a seção 0 do `docs/PLANO.md` e as últimas linhas do `docs/HISTORICO.md`.
- Confira o estado real: `gh pr list --state all --limit 8` e `git log --oneline -10`.
- Olhe se alguém subiu algo fora da `main`: `git fetch` e `git log --oneline -3` das branches antigas (`origin/tratamento_dados`,
  `origin/feat/metricas`) e das branches sem PR. Se tiver entrega nova, avise.

## 4. Diga à pessoa (curto)

1. o que mudou desde a última nota da seção 0;
2. o objetivo da sessão e o "pronto quando" (PLANO, seção 3), e qual requisito do professor ela atende (arquivo e item,
   ex.: "`requisitos_projeto.MD`, Aplicação: Terraform");
3. o primeiro passo concreto;
4. se a tarefa mexe em pasta de outro dono ou no `contratos.md`: quem precisa dar o ok no grupo antes do merge.

No fim da tarefa, lembre: `/fim-de-sessao`.
