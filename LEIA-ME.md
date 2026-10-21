# Raio-X Comercial · pasta do projeto

## Código oficial (o que vai para o repositório)

| Arquivo | Passo do fluxo | Dono | O que faz |
|---|---|---|---|
| `checar_indicadores.py` | 3. Checar e auditar | Marcos | Regras de sanidade nos indicadores; com `--com-ia`, o Gemini explica as empresas suspeitas (não altera números) |
| `segmentos.py` | 4. Grupos e parecidas | Eduardo | K-means (k pela silhueta) e 5 vizinhos mais próximos → `data/segmentos.csv` e `docs/graficos/silhueta.png` |
| `ia.py` | 6. Escrever o raio-x | Eduardo | `preparar_raio_x(cd_cvm, produto, objetivo)` no formato do contrato C3 |
| `app.py` | 5 e 7. Tela | Miguel | Streamlit. Dados falsos até o `dados.py` do Marcos existir |
| `tests/test_raio_x.py` | — | Eduardo | Testes automáticos (validador, contrato C3, checador) |
| `contratos.md` | — | grupo | Formatos combinados entre as partes |

## Arquivo de estudo

`prova_ia.py` é a prova da semana 1, com as partes A a E num arquivo só. É o que usamos nas aulas.
O código oficial reaproveita as mesmas funções, separadas em `segmentos.py` e `ia.py`.

## Atalhos (dois cliques)

| Atalho | O que faz | Gasta crédito? |
|---|---|---|
| `rodar_tela.command` | Abre a tela com texto montado sem IA | Não |
| `rodar_tela_com_ia.command` | Abre a tela com o Gemini escrevendo o raio-x | Sim (≈ US$ 0,0008 por raio-x) |
| `rodar_testes.command` | Roda os testes automáticos | Não |
| `rodar_segmentos.command` | Refaz os grupos e o gráfico da silhueta | Não |
| `checar_teste_com_ia.command` | Testa o checador com dados que têm erros de propósito | Sim (centavos) |
| `rodar_sem_ia.command` / `rodar_com_ia.command` | Rodam a prova de estudo (`prova_ia.py`) | Só o segundo |

## Dados

- `data/indicadores.csv`: vem do Marcos. Enquanto não existir, tudo usa `tabela_falsa.csv` (30 empresas inventadas).
- `falsos/`: arquivos de mentira no formato dos contratos, para cada um trabalhar sem esperar o outro.
- `.env`: a chave do Gemini. Nunca vai para o GitHub.
