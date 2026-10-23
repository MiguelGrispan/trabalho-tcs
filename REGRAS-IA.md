# Regras de uso de IA no projeto

Valem para os quatro (Marcos, Eduardo, Náthally, Miguel) e para qualquer ferramenta: ChatGPT, Gemini, Claude, Claude Code, Copilot.
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

- Cada um trabalha na sua branch (`eduardo`, `tratamento_dados`, ...).
- Faça commit antes de pedir uma mudança grande à IA: se der errado, dá para voltar.
- Commits pequenos, com mensagem dizendo o que mudou.
- Na `main` só entra por pull request, com os testes passando e 1 pessoa do grupo revisando.

## 6. Regras do produto (não negociáveis)

- O LLM nunca escreve números. Ele usa marcadores (`{margem_ebit}`) e o validador remove qualquer dígito fora deles. Nenhuma mudança pode quebrar isso.
- Acima / abaixo / em linha do grupo é calculado por código, não pela IA.
- A IA auditora dos dados só aponta suspeitas. Quem decide e corrige é uma pessoa.
- Formato de contrato (`contratos.md`) só muda avisando antes quem recebe.
- Rodar o Gemini em lote (mais de 10 chamadas) só avisando o grupo: gasta crédito.

## 7. Registro para a banca

No pull request, escreva em 2 linhas o que foi gerado com IA e o que você revisou e testou. Isso vira a seção "Como usamos IA para programar" do README.

## Checklist do pull request

- [ ] Rodei os testes e passaram.
- [ ] Li o diff inteiro e sei explicar cada mudança.
- [ ] Não tem `.env`, chave nem dado bruto no commit.
- [ ] Não mudei contrato sem avisar quem recebe.
- [ ] Escrevi o que foi feito com IA e o que eu revisei.
