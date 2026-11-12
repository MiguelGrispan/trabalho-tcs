# Roteiro de fala (base, 15 min)

Texto corrido para ensaiar. **É rascunho:** cada um troca pelas próprias palavras e cronometra. Ritmo usado: cerca de 130 palavras por
minuto, com pausas. Tempos e quem fala: `docs/tempo_apresentacao.md` (divisão por pessoa ainda não confirmada pelo grupo).
Trechos entre `[ ]` são lacunas que o dono preenche. Nenhum número novo foi inventado: os que aparecem vêm de
`docs/conteudo_eduardo.md` e `avaliacao/resultados.csv`.

---

## 1. Contexto e problema · 00:00 a 02:00 · Náthally

"Bom dia a todos. Somos o grupo do Raio-X Comercial. Eu sou a Náthally, e comigo estão o Marcos, o Miguel e o Eduardo.

Imagine um vendedor que vai a uma reunião com uma empresa grande. Ele quer vender um produto, mas não sabe como a empresa está
financeiramente, o que perguntar nem que empresas parecidas poderia procurar depois. Hoje ele junta isso na mão, entre relatórios
longos e planilhas, e a reunião chega sem preparo.

O Raio-X Comercial resolve isso. O vendedor escolhe uma companhia aberta, informa o produto e o objetivo da reunião, e recebe em
poucos minutos seis indicadores financeiros com a fonte, a posição da empresa em relação a um grupo de empresas parecidas, de três
a cinco perguntas ligadas ao produto, as lacunas do que não sabemos e cinco empresas parecidas para prospectar.

Todos os dados vêm de uma fonte pública, as demonstrações financeiras da CVM. O ganho é tempo: um diretor comercial que
entrevistamos leva uns 45 minutos para preparar uma primeira reunião; com o Raio-X, conferindo as fontes, cronometramos 17 minutos e meio.
São quase 4 horas por mês por vendedor, cerca de 270 reais, para um custo de IA de 5 centavos. É uma entrevista só, então é uma estimativa. Vou passar para o Marcos,
que mostra como o processo funciona por dentro."

## 2. BPMN e arquitetura · 02:00 a 04:30 · Marcos

"Obrigado, Náthally. Aqui está o processo da regra de negócio em BPMN 2.0. [Mostrar o diagrama de `docs/bpmn/`.] O vendedor procura
a empresa no banco, e o sistema monta os indicadores e a posição contra o grupo de parecidas, já calculada pelo modelo de
agrupamento. Depois, anexa a fonte de cada número: as contas do DFP e o link do documento na CVM. A IA escreve as perguntas, o sistema
confere o texto e a tela entrega o resultado. Cada etapa tem um responsável claro no desenho.

Na arquitetura, temos dois contêineres. Em um roda a tela, em Streamlit, junto com o código da aplicação. No outro roda o banco,
um PostgreSQL. A tela busca as empresas no banco, registra cada consulta nele e lê dali as contas e os links das fontes.

O caminho dos dados é simples: os arquivos da CVM entram, passam por limpeza e viram indicadores, gravados no banco e num arquivo
com o mesmo conteúdo; os números do raio-x são lidos desse arquivo. Esse trecho é o que eu detalho daqui a pouco. Agora o Miguel
mostra tudo funcionando."

## 3. Demonstração ao vivo · 04:30 a 09:30 · Miguel

(Fala curta; o resto do tempo é a tela. Roteiro completo em `docs/roteiro_demo.md`. Se a rede falhar: vídeo de reserva.)

"Vou mostrar o Raio-X no ar. Esta é a tela. [Digitar] Escolho uma empresa, por exemplo a WEG. Informo o produto que quero vender e o
objetivo da reunião. [Clicar em gerar.]

Enquanto ele trabalha: o sistema está montando os indicadores e a IA está escrevendo as perguntas.

Pronto. Aqui estão os seis indicadores, cada um com sua fonte. Aqui a posição da empresa contra o grupo de parecidas, calculada por
código, não pela IA. Aqui as perguntas para a reunião, ligadas ao produto que informei. Aqui as lacunas: o que o sistema não sabe e
o vendedor deve confirmar. E aqui as cinco empresas parecidas para prospectar.

[Se sobrar tempo: repetir com outra empresa, ou mostrar o aviso de modo sem IA.] Se a IA estiver fora do ar, a tela continua e
avisa que o texto veio sem IA. Passo ao Marcos e ao Eduardo, para explicar o que há por trás."

## 4. Detalhe técnico · 09:30 a 12:30 · Marcos 0:45, Eduardo 1:30, Miguel 0:45

**Marcos (0:45):** "Os dados vêm das demonstrações da CVM. Com Python e Pandas, limpamos, tratamos valores nulos e calculamos os
indicadores. Depois gravamos tudo no PostgreSQL, e a tela consulta com SQL. São 595 empresas, com indicadores do exercício de 2025, calculados sobre as contas de 2023 a 2025."

**Eduardo (1:30):** "Na parte de IA temos duas peças. A primeira é o K-means, que agrupa as empresas pelo perfil financeiro; os
vizinhos mais próximos sugerem as cinco parecidas. Escolhemos quatro grupos, e a silhueta deu 0,286: os grupos se sobrepõem. Nos
dez casos que avaliamos, todas as empresas caíram no mesmo grupo. Por isso tratamos isso como apoio exploratório, não como lista de
concorrentes.

A segunda peça é o Gemini, usado com LangChain. A regra de ouro do projeto: a IA nunca escreve número. Ela usa marcadores no lugar
dos valores; um validador barra qualquer dígito fora de marcador; só então o código troca os marcadores pelos valores da tabela.
Nos dez casos, nenhum trecho foi removido e a geração levou em média 2,15 segundos. Isso não prova que o texto está sempre correto:
afirmação falsa sem número ainda pode passar, então a revisão humana continua necessária."

**Miguel (0:45):** "Para rodar tudo, usamos Docker Compose, que sobe a tela e o banco. A mesma infraestrutura também está declarada
em Terraform, que o professor exige. [Mostrar `infra/` na tela se couber.] Um comando sobe os dois contêineres, e outro desliga."

## 5. Governança e ética · 12:30 a 14:00 · Náthally

"Sobre uso responsável. Primeiro, os limites que já citamos: o agrupamento mostra empresas parecidas, não concorrentes, e os grupos
se sobrepõem. Segundo, a IA pode errar sem usar número, por isso o texto é um apoio e o vendedor revisa antes de usar.

Os dados são públicos, da CVM, [CONFERIR em `docs/etica.md` antes de afirmar que não há dado pessoal]. A consulta registrada no banco guarda [PREENCHER: o que
exatamente é registrado, conforme `docs/etica.md`]. A chave da IA fica fora do código. Nossa conclusão é que o Raio-X ajuda a
preparar a reunião, mas não decide por ninguém."

## 6. Conclusão · 14:00 a 15:00 · Eduardo

"Resumindo: entregamos uma aplicação que roda de ponta a ponta, com dados públicos, um modelo de agrupamento, IA generativa
controlada por validador e infraestrutura declarada em Terraform. O que ainda é limite: o ROI vem de uma única entrevista e o
agrupamento é exploratório.

Em equipe, aprendemos a combinar o formato entre as partes antes de escrever código e a rodar testes antes de dizer que está pronto.
[PREENCHER: uma lição de cada pessoa, 1 frase.]

Obrigado. Ficamos à disposição para as perguntas da banca."

---

## Folga e perguntas (15:00 a 18:00 e 12 min de banca)

- Os 3 min de folga existem para gaguejar, dar branco e a demo demorar. **Não preencher com mais conteúdo.**
- Deu branco? Volte à última frase do slide e siga. Perdeu mais de 30 s? Corte a próxima frase de exemplo, não acelere.
- Perguntas da banca: treinar com as respostas de `docs/conteudo_eduardo.md`, seção 2.
