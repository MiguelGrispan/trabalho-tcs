# Instruções para agentes de código (Codex, Claude Code, Copilot)

Este arquivo existe porque o Codex lê `AGENTS.md`. As regras completas do projeto estão em:

1. `CLAUDE.md`: contexto, donos de cada pasta e regras do time.
2. `REGRAS-IA.md`: o que nunca vai para uma IA nem para o Git.
3. `contratos.md`: formatos que passam de uma parte para outra.
4. `docs/PLANO.md`: a sessão que a pessoa está fazendo (ex.: "faça a sessão MG2").

Leia os quatro antes de alterar qualquer arquivo.

## Regras que não podem ser quebradas

- O LLM nunca escreve números: ele usa marcadores como `{margem_ebit}`, e o validador remove qualquer dígito fora de marcador.
- Mexa só nos arquivos da sessão e nas pastas do dono (tabela no `CLAUDE.md`).
- Mudou um formato entre partes? Primeiro o `contratos.md`, avisando quem recebe.
- Não leia, mostre nem envie o `.env`. Nada de dados (`data/`) nem `.env` no Git.
- O modo sem IA (sem `RAIOX_IA_REAL`) precisa continuar funcionando: é o plano B da demo.
- Antes de dizer "pronto", rode `python -m pytest -q` a partir da raiz e mostre o resultado.
- Git: branch `pessoa-tarefa` a partir da `main`; nunca `rebase`, `push --force` nem commit direto na `main`.
- Comece propondo um plano sem alterar arquivos; altere só depois que a pessoa aprovar.
- Responda em português simples, com arquivo e linha como prova.
