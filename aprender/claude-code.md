# Claude Code no projeto: guia para o time

Para o Marcos, o Miguel e o Eduardo, que programam com o Claude Code. A Náthally não precisa deste guia: ela usa o GitHub pelo navegador.
As regras de uso de IA do time estão no [REGRAS-IA.md](../REGRAS-IA.md); este guia é o "como usar a ferramenta".

## Em 1 minuto

1. Abra o Terminal na **raiz do projeto** (a pasta `trabalho-tcs/`) e digite `claude`.
2. Digite `/inicio-de-sessao XX`, trocando `XX` pelo código da sua sessão (não sabe? digite só `/inicio-de-sessao`).
   Ele atualiza a `main`, cria a sua branch e diz o que mudou e por onde começar.
3. Trabalhe numa tarefa só. O Claude pede licença antes de mudar arquivos.
4. No fim, digite `/fim-de-sessao`. Ele roda os testes, atualiza o PLANO e o HISTORICO, abre o PR, espera o CI, lê o diff e,
   depois do seu "pode", faz o merge na `main`. Você não precisa mexer no GitHub.
5. Antes da próxima tarefa, digite `/clear`.

## Qual é a minha sessão?

- **O código da sua sessão** está no `docs/PLANO.md`, seção 3: MA2, MA3… (Marcos), MG1, MG2… (Miguel), ED7, ED8… (Eduardo).
- Não sabe? Digite só `/inicio-de-sessao`: ele mostra as suas sessões que ainda faltam e sugere a próxima.
- O `/inicio-de-sessao` não aparece? Veja "Problemas comuns", no fim.

## O que o Claude Code é (e o que ele já sabe)

- É o Claude trabalhando **no seu computador, dentro da pasta do projeto**: ele lê arquivos, edita e roda comandos.
- No começo de **toda** sessão, ele lê o `CLAUDE.md` sozinho. Por isso já conhece os donos de cada pasta, a regra de ouro
  (o LLM nunca escreve números), as regras de Git e os comandos de teste. Você não precisa repetir isso.
- Ele **não lembra** das conversas anteriores. O que liga uma sessão à outra são os arquivos: a seção 0 do PLANO, os commits e os PRs.
  Por isso o PLANO tem de estar atualizado no fim de cada sessão.

## Durante a sessão

**Modos** (troque com **Shift+Tab**; o modo atual aparece embaixo da caixa de texto):

| modo | o que faz | quando usar |
|---|---|---|
| normal | pede licença antes de cada edição e de cada comando | quando você quer acompanhar tudo |
| aceitar edições | edita sem perguntar; comandos ainda pedem licença | tarefa pequena num arquivo seu |
| **Plan** | só lê e propõe um plano; nada muda até você aprovar | **mais de um arquivo, contrato ou arquivo comum** (regra do PLANO, seção 3) |

**Quando ele pede licença**, leia o que vai rodar antes de aceitar. "Sim, e não pergunte de novo" só para comandos que não mudam nada,
como `python -m pytest -q` e `git status`.

**Atalhos que valem a pena:**

| atalho | o que faz |
|---|---|
| **Esc** | interrompe o que ele está fazendo (use sem medo) |
| **Esc duas vezes** | volta a uma mensagem anterior e pode desfazer as edições que ele fez desde então |
| `!comando` | roda o comando você mesmo, e o resultado entra na conversa (ex.: `! git status`) |
| `@arquivo` | aponta um arquivo na mensagem (ex.: `@raiox/dados.py`) |
| `/explicar arquivo função` | ensina um trecho do código e faz perguntas como as da banca (só lê, não muda nada) |
| `/help` | lista todos os comandos |

**Como pedir:** veja o [REGRAS-IA.md](../REGRAS-IA.md), seção 3. Em resumo: diga o que quer, quais arquivos ele pode mexer e como saber que ficou pronto.

## Limites: são três coisas diferentes

**1. A memória da conversa (contexto).**
- Cada conversa tem um tamanho máximo. Quando ela fica longa, o Claude resume sozinho as partes antigas e pode esquecer detalhes do começo.
- Sinais: ele repete perguntas, esquece uma regra combinada ou "desfaz" algo que vocês decidiram.
- O que fazer:
  - **uma tarefa por sessão**;
  - `/clear` entre tarefas, porque apaga a conversa, não os arquivos;
  - `/context` mostra quanto da memória já foi usado;
  - `/compact` resume a conversa na hora, se você precisar continuar.
- **Antes de `/clear` com mudança sem commit**, faça o commit ou anote onde parou. A próxima conversa não vai saber por que os arquivos mudaram.

**2. O limite de uso da assinatura.**
- Cada plano tem um limite de uso que volta depois de algumas horas, e há também um limite semanal.
- Quando estiver perto, o Claude Code avisa e diz quando volta. O `/usage` mostra quanto você já usou.
- Conversas longas e arquivos grandes gastam mais. O modo Plan antes de uma tarefa grande evita retrabalho, e retrabalho é o que mais gasta.
- Bateu o limite no meio da tarefa? Faça o commit do que estiver pronto e anote na seção 0 do PLANO onde parou.

**3. O crédito do Gemini (o do produto, não o do Claude).**
- A assinatura do Claude Code **não** paga o Gemini. A chave do Gemini, no `.env`, é de um plano pré-pago do time.
- O Claude Code só gasta crédito do Gemini se rodar o produto com IA: `RAIOX_IA_REAL=1`, `--com-ia` ou `usar_ia=True`.
  Os testes nunca chamam o Gemini. Mais de 10 chamadas: avise o grupo antes.

## Terminar a sessão

Digite `/fim-de-sessao`. Ele faz, nesta ordem:
1. roda os testes;
2. lê o `git status` com você;
3. atualiza a seção 0 do PLANO e o REQUISITOS;
4. escreve de 1 a 3 linhas no `docs/HISTORICO.md`;
5. faz o commit, o push e abre o PR;
6. espera o CI e lê o diff;
7. pede o seu "pode" e faz o merge.

Ele pergunta o que você entendeu ou conferiu e escreve isso no PR (vale "ainda não li"; não vale inventar).
Sem a skill, peça ao Claude: "siga o arquivo `.claude/skills/fim-de-sessao/SKILL.md`".

Depois: `/clear` para a próxima tarefa, ou `/exit` para sair.
Para voltar a uma conversa antiga: `claude --continue` (a última) ou `/resume` (escolher numa lista). Para tarefa nova, prefira uma sessão nova.

## Nunca

- Colar o conteúdo do `.env` ou qualquer chave na conversa.
- Aceitar `git push --force`, `git rebase` ou commit direto na `main`, mesmo que ele sugira.
- Aceitar mudança em pasta de outro dono sem combinar (a tabela de donos está no `CLAUDE.md`).
- Subir algo que você não sabe explicar. Peça "explique o que você mudou e por quê", ou use `/explicar`.

## Problemas comuns

| aparece | o que fazer |
|---|---|
| ele esqueceu uma regra ou está confuso | commit do que estiver pronto, `/clear` e `/inicio-de-sessao` de novo |
| ele mexeu num arquivo que não devia | **Esc**, depois "desfaça a mudança em `arquivo`", e confira com `! git diff` |
| não sei o que mudou | `! git status` e `! git diff` |
| `/inicio-de-sessao`, `/fim-de-sessao` ou `/explicar` não aparece | a sua branch não tem a pasta `.claude/skills/`: `git switch main` e `git pull`, depois abra o `claude` de novo |
| atingiu o limite de uso | commit, anote onde parou na seção 0 do PLANO e continue quando o limite voltar |
| "command not found: claude" | o Claude Code não está instalado nesse terminal; veja a página de instalação do Claude Code ou peça ajuda ao Eduardo |
