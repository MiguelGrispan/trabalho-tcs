# avaliacao/ · contrato C4

Pasta da avaliação do Raio-X: regras da instrução, casos de teste, resultados da IA e revisão humana.
Fluxo: Náthally ⇄ Eduardo → Marcos. O formato oficial está em `contratos.md` (C4); mudou lá, muda aqui.

## Donos

- `avaliar.py` · Eduardo: roda o raio-x para cada caso de `casos_avaliacao.csv` e grava `resultados.csv`.
- `*.csv` e `regras_prompt.md` · Náthally (menos o `resultados.csv`, que o `avaliar.py` escreve).

## Arquivos

| arquivo | quem escreve | colunas |
|---|---|---|
| regras_prompt.md | Náthally | texto das regras da instrução |
| casos_avaliacao.csv | Náthally | caso_id, cd_cvm, produto, objetivo |
| tempo_manual.csv | Náthally | empresa, minutos, fontes |
| resultados.csv | Eduardo (`avaliar.py`) | caso_id, raio_x_json, n_removidos, tokens_entrada, tokens_saida, custo_usd, tempo_s |
| revisao.csv | Náthally | caso_id, item, comparacao_certa, ligada_ao_produto, clara, utilidade |
| conferencia.csv | Náthally | cd_cvm, indicador, valor_sistema, valor_ri, diferenca_pct |
| testes_usuarios.csv | Náthally | pessoa_id, cargo, minutos, utilidade, usaria, comentario |

## Cuidados

- Nada de dado pessoal de quem respondeu teste ou entrevista (nome, e-mail, telefone): use `pessoa_id`.
- Rodar o `avaliar.py` com o Gemini gasta crédito. Mais de 10 chamadas, avise o grupo antes.
