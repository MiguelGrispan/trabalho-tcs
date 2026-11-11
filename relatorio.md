# Semana_01

## glossario_finan.md

O glossário foi o primeiro passo para entender melhor o projeto. Como eu tinha pouco conhecimento sobre a área financeira, fiz uma pesquisa inicial e anotei os conceitos mais importantes para meu aprendizado. Algumas informações foram detalhadas além do necessário, porque os cálculos seriam repetidos nos próximos arquivos, mas isso serviu como base de segurança e confiança na execução.

## persona.md

A primeira versão da persona foi compartilhada com o grupo e, depois, ficou mais robusta. A maioria das hipóteses foi confirmada, exceto a H3, que não foi abordada no formulário. Como tínhamos pouco tempo, conseguimos entrevistar apenas um profissional.

## pitch_30s.md

O pitch original usava storytelling e apresentava Marina, uma executiva de contas, em uma situação específica. O texto atual deixou essa narrativa de lado e passou a apresentar diretamente as funcionalidades do Raio-X, como indicadores com fonte, perguntas para a reunião e empresas semelhantes para prospectar. A versão original não se encaixou bem na apresentação final do projeto.

## raiox_IA_Camil.md

Criei esse arquivo para justificar a proposta de valor do projeto, comparando respostas divergentes de diferentes IAs, treinadas com dados amplos da internet e não específicas para a dor que buscamos resolver. A divergência entre os números e a dificuldade para encontrar as fontes evidenciaram problemas que o projeto atualmente já resolve.

## regras_v1.md

Essa foi a primeira versão das regras para a IA. Utlizei técnicas de engenharia de prompt: defini o papel que ela deveria assumir, organizei as instruções por prioridade e especifiquei o formato e a quantidade dos itens da resposta; essas técnicas ajudam a orientar o comportamento e a estrutura da saída.

## roteiro.md

Esse foi o primeiro roteiro de perguntas para o formulário de entrevista com profissionais da área. Naquele momento, esperávamos receber respostas de mais pessoas. Comparando o roteiro inicial com as perguntas registradas no CSV,  foram retiradas a pergunta aberta sobre como a pessoa se preparou para a última reunião e a pergunta sobre ter levantado algum dado financeiro. A ordem também mudou: a pergunta sobre como avaliar se os números são bons ou ruins passou para antes das perguntas sobre fontes, e a quantidade de contas acompanhadas foi antecipada.

# Semana_02

## avaliacao.ipynb

A avaliação foi criada para testar a aplicação com diferentes empresas, produtos e objetivos. No código, o Pandas transforma a lista de casos em uma tabela, e o `Path` define o caminho do arquivo CSV. A tabela contém `caso_id` (identificador do caso), `cd_cvm` (código da empresa na CVM), `empresa` (nome), `setor`, `produto` e `objetivo`; o CSV salva apenas `caso_id`, `cd_cvm`, `produto` e `objetivo`, sem incluir o índice.

## regras_v2.md

Após executar a primeira versão das regras, a v2 passou a aceitar a posição “em linha” e incluiu uma instrução com exemplos de comparação correta e incorreta para evitar repetir o nome do indicador ao mencionar a mediana do grupo. Também fixou o resumo em três frases, acrescentou orientações específicas para escrever as lacunas e proibiu palavras de intensidade nas comparações. Em relação à v1, a lista de dados de entrada deixou de mencionar `empresa` e `ano`. As mudanças usam técnicas de engenharia de prompt como exemplos contrastivos (“errado” e “certo”), regras explícitas e restrições de linguagem e formato, para orientar a IA a produzir respostas mais padronizadas.

## revisao_manual.md

Para conferir os resultados do Raio-X, fiz manualmente a análise das empresas e usei o NotebookLM como apoio. Os resultados coincidiram, com uma diferença de critério na margem EBIT: usei a tabela “Pré-IFRS 16” do Relatório da Administração da DFP 2025 (p. 48 da DFP; p. 50 do PDF), enquanto as tabelas ajustadas aparecem nas pp. 52 e 54 do PDF. Portanto, não foi um erro, mas uma divergência na base considerada.
