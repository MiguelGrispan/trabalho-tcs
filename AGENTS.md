# Instruções para agentes de código (Codex, Claude Code, Copilot)

Este arquivo existe porque o Codex lê `AGENTS.md`. O que o projeto precisa ter vem dos arquivos do professor, e as regras do time
estão nos outros:

1. `docs/professor/requisitos_projeto.MD` e `docs/professor/guia_projeto_final.pdf`: **o que o professor exige**. Valem mais que
   qualquer nota do repositório; quando os dois diferem, vale o mais exigente (ex.: o Terraform é obrigatório).
2. `CLAUDE.md`: contexto, donos de cada pasta, regras do time e a tabela "O que o professor exige".
3. `REGRAS-IA.md`: o que nunca vai para uma IA nem para o Git.
4. `contratos.md`: formatos que passam de uma parte para outra.
5. `docs/PLANO.md`: a sessão que a pessoa está fazendo (ex.: "faça a sessão MG2"); `docs/REQUISITOS.md`: o status de cada requisito.

Leia todos antes de alterar qualquer arquivo.

## Regras que não podem ser quebradas

As travas automáticas do Claude Code (`.claude/settings.json` e `.claude/hooks/guarda.py`) **não rodam no Codex**: aqui, as
regras abaixo dependem de você. Valem para todos: a conferência do commit pelo Git (`.githooks/pre-commit`, depois de
`git config core.hooksPath .githooks`) e o CI (`tests/test_guarda.py`: nada de `data/`, `.env`, chave, senha nem arquivo acima
de 10 MB no Git). Não use `--no-verify`.

- Nunca diga que algo exigido nos arquivos do professor é opcional ou pode ser cortado. Toda afirmação sobre o que o professor
  exige vem com o arquivo e o item. Se não está claro, diga que não sabe e anote a pergunta no `docs/REQUISITOS.md`.

- O LLM nunca escreve números: ele usa marcadores como `{margem_ebit}`, e o validador remove qualquer dígito fora de marcador.
- Mexa só nos arquivos da sessão e nas pastas do dono (tabela no `CLAUDE.md`).
- Mudou um formato entre partes? Primeiro o `contratos.md`, avisando quem recebe.
- Não leia, mostre nem envie o `.env`. Nada de dados (`data/`) nem `.env` no Git.
- O modo sem IA (sem `RAIOX_IA_REAL`) precisa continuar funcionando: é o plano B da demo.
- Antes de dizer "pronto", rode `python -m pytest -q` a partir da raiz e mostre o resultado.
- Git: branch `pessoa-tarefa` a partir da `main`; nunca `rebase`, `push --force` nem commit direto na `main`.
- Comece propondo um plano sem alterar arquivos; altere só depois que a pessoa aprovar.
- Responda em português simples, com arquivo e linha como prova.
