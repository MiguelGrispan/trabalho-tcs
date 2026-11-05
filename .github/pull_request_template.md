## O que muda e por quê

<!-- 2 ou 3 frases. Qual sessão do docs/PLANO.md é esta (ex.: MA2)? Qual requisito do professor ela atende (docs/professor/, arquivo e item)? -->

## Uso de IA (vira a seção "Como usamos IA para programar" do README)

- Feito com IA:
- O que eu entendi ou conferi (vale "ainda não li"; não vale inventar):

## Para as notas (o Eduardo leva para o PLANO, o REQUISITOS e o HISTORICO)

- Sessão e status (✅ ou 🟡):
- O que mudou, com prova (arquivo, linha ou comando):
- Testes (passed / pulados, em qual máquina):
- Linha do `docs/REQUISITOS.md` afetada (ou "nenhuma"):
- Próximo passo:

## Achados não consertados

<!-- Do revisor ou da sessão: o que não quebra a demo, um requisito do professor nem a regra de ouro. Uma linha cada (ou "nenhum"). -->

## Checklist (REGRAS-IA.md)

O `/fim-de-sessao` confere estes itens antes do merge:

- [ ] O CI deste PR está verde.
- [ ] Não tem `.env`, chave nem dado bruto (`git status` lido).
- [ ] Mexeu no `contratos.md` ou na pasta de outro dono? O dono deu o ok no grupo.
- [ ] O modo sem IA continua funcionando.
- [ ] Nada no PR contradiz os arquivos do professor (`docs/professor/`) nem marca como opcional algo que eles exigem.
- [ ] "Para as notas" preenchido. PLANO, REQUISITOS e HISTORICO só mudam no PR do Eduardo.

## Revisão

O CI e o Claude Code revisam. Uma pessoa só entra quando o PR mexe no contrato ou na pasta dela (ok no grupo).
