# Histórico do Raio-X (versão resumida)

Tudo o que aconteceu no projeto, em poucas linhas. Serve para lembrar, para quem chega atrasado numa conversa e para a banca
("como vocês chegaram até aqui?"). O detalhe de cada passo está no pull request (`gh pr list --state all`) e o "agora" está na
seção 0 do [PLANO.md](PLANO.md).

**Como atualizar:** no fim de cada sessão, o `/fim-de-sessao` acrescenta de 1 a 3 linhas no dia certo (o que mudou, com o
número do PR) e, se houve, a decisão na tabela de decisões. Sem detalhe técnico: isso fica no PR.

## Linha do tempo

### Semana 1 (19 a 25/10): cada um no seu canto
- **19/10** · Miguel cria o repositório.
- **20 a 23/10** · Náthally escreve glossário, roteiro, persona, pitch de 30 s e as regras v1 do texto (pasta `Semana_01/`).
- **21/10** · Eduardo: primeira versão do Raio-X (IA, segmentação, checador de dados, tela v0, testes) e o `REGRAS-IA.md`,
  já com a **regra de ouro**: o LLM nunca escreve números (PR #1, merge em 23/10).
- **21 a 23/10** · Marcos: carga e limpeza da DFP da CVM e a tabela de empresas, na branch `tratamento_dados`.

### Semana 2 (26/10 a 01/11): juntar tudo e fazer funcionar
- **26/10** · PR #2 "Fundação": uma pasta por dono, o código do Marcos trazido para a estrutura nova.
- **27/10** · PRs #3 a #6: plano até a banca, matriz do guia, CI (testes em todo PR), versões fixas (Python 3.14);
  dados do Marcos (#4) e produto da Náthally (#5) trazidos para a `main`; `avaliar.py` e teste ponta a ponta (#6).
  **ED1:** os primeiros 3 raio-x com dados reais (595 empresas, US$ 0,0026). Problema achado: o K-means pôs 567 das
  595 empresas num grupo só.
- **28/10** · PR #9 (ED4): segmentação consertada (k = 4, silhueta 0,30; a silhueta de 0,77 "enganava").
  PR #8: guia do Claude Code e as skills `/explicar` e `/fim-de-sessao`. O Miguel passa a usar o Claude Code e começa o
  Docker e o Terraform (branch sem PR). O Marcos muda o banco para PostgreSQL na `tratamento_dados`.
- **29/10** · A Náthally entrega as regras v2 e os `cd_cvm` dos 10 casos. PR #10 (casos) entra.
  PR #11 (ED3): o prompt passa a ser o arquivo de regras dela; 3 raio-x reais sem nada removido; US$ 0,0012 cada.
  Teste do Docker e do Terraform do Miguel: funcionam, faltam ajustes; o teste achou um bug, consertado no PR #12.
  **O professor diz que SQLite não vale: o banco é PostgreSQL** (PR #13).
  O grupo simplifica o GitHub: o CI e o Claude Code revisam; uma pessoa só é chamada para contrato ou pasta de outro dono (PR #14).
  O Miguel tira a aprovação obrigatória da `main`, e os PRs #11 a #14 entram às 11h17 (73 testes passando).
  O PR #15 (só documentação) foi mesclado antes do CI começar; o CI passou depois, e o `/fim-de-sessao` agora espera
  o `pass` (PR #16). É por isso que o check `testes` deve ficar obrigatório no GitHub (MG1).
  O Marcos abre o PR #18 (MA2, PostgreSQL) e a Náthally abre a issue #17 (ano fiscal da Camil, de março a fevereiro).
  Documentos de orientação enxugados (PR #19): cada informação num lugar só, sem as instruções velhas que contradiziam as novas.

## Decisões (e por quê)

| data | decisão | por quê |
|---|---|---|
| 21/10 | o LLM nunca escreve números; usa marcadores como `{margem_ebit}` | número inventado num material de vendas é o pior erro possível |
| 26/10 | cada pasta tem um dono | quatro pessoas mexendo no mesmo arquivo geravam conflito |
| 27/10 | Python 3.14 e versões fixas no `requirements.txt` | todos, o CI e o Docker rodam igual |
| 27/10 | merge commit; nunca `rebase` nem `push --force` | guarda os passos (prova para a banca) e não apaga trabalho de colega |
| 28/10 | K-means só com receita a partir de R$ 10 mi, extremos cortados, menor grupo com 5% ou mais | sem isso, um grupo tinha 567 de 595 empresas |
| 28/10 | "empresas parecidas" = mesmo perfil financeiro, não o mesmo setor | é o que o modelo mede; o filtro de setor foi cortado |
| 29/10 | o prompt lê o arquivo de regras da Náthally, sem cópia no código | a cópia tinha ficado diferente do que ela escreveu |
| 29/10 | Suzano S.A. (13986) e Localiza Rent a Car (19739) nos casos | as duas empresas tinham mais de um código na CVM |
| 29/10 | **banco PostgreSQL** | regra do professor: SQLite não vale |
| 29/10 | GitHub simples: CI verde + revisão do Claude Code; pessoa só para contrato ou pasta de outro dono | o clique de "aprovar" travava tudo e não era revisão de verdade |
| 29/10 | cada informação num lugar só: o agora na seção 0 do PLANO, o status no REQUISITOS, o passado aqui | instruções de 26/10 continuavam nos guias e contradiziam as novas (ex.: "main só com 1 revisão"; trazer o `verificar_automatico.py`, que já tinha sido cortado) |

**Já cortado do escopo:** verificação com yfinance, receita em 3 anos, filtro de setor, RAG, nome dos grupos pelo LLM,
exportar o raio-x, 20 casos (ficaram 10). A lista e a ordem dos próximos cortes estão no PLANO, seção 7.

## O que aprendemos (para a banca)

- **Branch longa, sem história em comum com a `main`, vira retrabalho:** três vezes alguém teve de trazer à mão o que estava
  na `tratamento_dados` ou na `feat/metricas`. Agora toda sessão começa da `main` (`/inicio-de-sessao`).
- **Número bonito pode enganar:** a silhueta de 0,77 media só a separação de 9 empresas extremas.
- **Teste que passa nem sempre testa:** dois testes passavam com o campo vazio. Agora estragamos o código de propósito
  para ver o teste falhar.
- **Aprovar sem ler não é revisão:** quem revisa de verdade é o CI (mais de 70 testes) e a leitura do diff; a pessoa entra
  quando a mudança afeta o trabalho dela.
- **Documento velho confunde mais que documento nenhum:** uma lista de tarefas de 26/10, já trocada pelo PLANO, ainda mandava
  trazer arquivos que tinham sido cortados. Agora o que passou sai do guia e vem para cá.

**Se começássemos do zero** (para aprender, não para refazer):
1. Matriz do guia com dono no dia 1, antes de qualquer código.
2. Contratos com o formato do arquivo e falsos no mesmo formato: os bugs do CSV com `;` e do `cd_cvm` como texto são de contrato.
3. Repositório-esqueleto feito por uma pessoa, de onde todos clonam, com CI e versões fixas desde o início.
4. Docker "olá mundo" na primeira semana.
5. Cada um trabalhando contra os falsos, com integração semanal e tag.
