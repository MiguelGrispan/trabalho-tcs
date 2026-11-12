# Cálculo do ROI: Raio-X Comercial

**Autora:** Náthally (NA3 e NA7) · entregue em 12/11/2026 · levado ao repositório pelo Eduardo, com o Claude Code, sem mudar
números nem conclusões (só a formatação das tabelas e as origens, para quem lê o repositório).

Atende: `guia_projeto_final.pdf` §7 ("Explique claramente o retorno sobre o investimento (ROI) ou a redução do tempo operacional")
e §5 (Inovação e Valor de Negócio, peso 20%: "A solução traz ganhos perceptíveis de eficiência ou custo?").

> **Aviso:** todos os resultados são **estimativas baseadas em uma única entrevista** (um diretor comercial de tecnologia e software).
> Não representam a média dos vendedores B2B.

## Resumo em 3 linhas

1 - Hoje o entrevistado leva **45 min** (faixa de 30 a 60) para preparar uma primeira reunião; com o Raio-X, **17,5 min** conferindo as fontes (cenário A) ou **12,5 min** sem conferir (cenário B), medidos com cronômetro.
2 - Com 8 primeiras reuniões por mês, isso economiza **3,7 h (A) a 4,3 h (B) por mês**, ou **R$ 273 a R$ 322 por mês** por executivo no custo médio da hora (R$ 74,40).
3 - A API custa **cerca de R$ 0,05 por mês** (8 raio-x); por isso o ROI dá milhares de vezes. O número que importa é o tempo economizado, não o múltiplo.

## 1. Premissas

| premissa | valor | origem | justificativa ou limitação |
|---|---|---|---|
| Amostra | 1 profissional: diretor comercial, mais de 10 anos de B2B, vende tecnologia e software, clientes grandes, acompanha mais de 30 contas | entrevista (formulário de [roteiro_forms.md](roteiro_forms.md)) | o perfil (diretor) difere da persona (executivo de contas) |
| Primeiras reuniões por mês | 6 a 10; usado **8** | entrevista | ponto médio da faixa marcada |
| Tempo atual de preparação (sem o Raio-X) | 30 a 60 min; usado **45 min** | entrevista | ponto médio da faixa marcada. É tempo declarado, não medido. O entrevistado usa IA "quase sempre" (ChatGPT, Copilot e Claude) e diz verificar os resultados, então o cenário já inclui ferramentas de IA |
| Tempo com o Raio-X, cenário A (com conferência das fontes) | 15 a 20 min; usado **17,5 min** | medido com cronômetro | estimativa medida |
| Tempo com o Raio-X, cenário B (sem conferência das fontes) | 10 a 15 min; usado **12,5 min** | medido com cronômetro | estimativa medida |
| Salário mensal | R$ 10.000 a R$ 15.000 | informado pelo entrevistado | faixa; não há outra fonte |
| Jornada mensal | **168 h** (8 h por dia × 21 dias úteis) | premissa | segunda a sexta, 8 h por dia; 21 dias úteis é a média mensal de um ano com cerca de 252 dias úteis |
| Raio-x por mês | **8** (um por primeira reunião) | premissa | se houver reconsultas, o custo sobe, mas continua desprezível |
| Custo por raio-x | **US$ 0,0011847** (média de 10 casos) | [avaliacao/resultados.csv](../../avaliacao/resultados.csv), rodada de 05/11 | média de 2.262 tokens de entrada e 413 de saída no `gemini-3.1-flash-lite` |
| Cotação | **R$ 5,5606 por US$ 1** | PTAX de 11/11/2026 | usada só no custo da API, que está em dólares |

As respostas da entrevista ficam fora do repositório: são dados de uma pessoa (inclusive a faixa de salário).

## 2. Custo da hora do profissional

Fórmula: salário mensal ÷ 168 h.

| faixa | salário | cálculo | custo da hora |
|---|---|---|---|
| inferior | R$ 10.000 | 10.000 ÷ 168 | **R$ 59,52** |
| médio | R$ 12.500 | 12.500 ÷ 168 | **R$ 74,40** |
| superior | R$ 15.000 | 15.000 ÷ 168 | **R$ 89,29** |

Se a jornada fosse de 173,3 h por mês (40 h × 52 semanas ÷ 12), o custo médio da hora cairia para R$ 72,12, uma diferença de cerca
de 3%. Não foram incluídos encargos (FGTS, férias, 13º), o que **subestima** o custo real.

## 3. Tempo atual de preparação

| item | valor | em horas |
|---|---|---|
| Tempo por reunião (ponto médio) | 45 min | **0,75 h** |
| Faixa informada | 30 a 60 min | 0,50 a 1,00 h |
| Horas por mês gastas hoje | 8 reuniões × 0,75 h | **6,0 h** (faixa de 3,0 a 10,0 h) |

## 4. Custo mensal da ferramenta

| cálculo | resultado |
|---|---|
| US$ 0,0011847 × R$ 5,5606 | **R$ 0,006588 por raio-x** |
| 8 raio-x × R$ 0,006588 | **R$ 0,0527 por mês** (cerca de 5 centavos) |

O custo fixo mensal é zero hoje: o Docker e o Terraform rodam no computador de quem usa. O custo de um servidor num uso real não foi estimado.

## 5. Cenário A: com conferência das fontes

Tempo com a ferramenta: 17,5 min = **0,2917 h**. Economia por reunião: 0,75 − 0,2917 = **0,4583 h** (27,5 min).
Horas economizadas por mês: 8 × 0,4583 = **3,67 h**.

| custo da hora | economia por mês (8 × 0,4583 h × custo da hora) | ROI (economia ÷ R$ 0,0527) |
|---|---|---|
| R$ 59,52 (inferior) | R$ 218,25 | 4.141 vezes |
| R$ 74,40 (médio) | **R$ 272,82** | **5.177 vezes** |
| R$ 89,29 (superior) | R$ 327,38 | 6.212 vezes |

## 6. Cenário B: sem conferência das fontes

Tempo com a ferramenta: 12,5 min = **0,2083 h**. Economia por reunião: 0,75 − 0,2083 = **0,5417 h** (32,5 min).
Horas economizadas por mês: 8 × 0,5417 = **4,33 h**.

| custo da hora | economia por mês (8 × 0,5417 h × custo da hora) | ROI (economia ÷ R$ 0,0527) |
|---|---|---|
| R$ 59,52 (inferior) | R$ 257,94 | 4.894 vezes |
| R$ 74,40 (médio) | **R$ 322,42** | **6.118 vezes** |
| R$ 89,29 (superior) | R$ 386,90 | 7.341 vezes |

## 7. Comparação entre os cenários (custo médio da hora)

| item | cenário A (com conferência) | cenário B (sem conferência) | diferença |
|---|---|---|---|
| Tempo com a ferramenta | 0,2917 h | 0,2083 h | 0,0833 h (5 min) por reunião |
| Horas economizadas por mês | 3,67 h | 4,33 h | 0,67 h (40 min) |
| Economia por mês | R$ 272,82 | R$ 322,42 | R$ 49,60 |
| ROI | 5.177 vezes | 6.118 vezes | 941 vezes |

1 - **Conferir as fontes custa cerca de 5 minutos por reunião**, o que corresponde a R$ 49,60 por mês. O cenário A preserva cerca de 85% da economia do B.
2 - **O cenário A é o mais próximo do comportamento do entrevistado:** ele diz que verifica as informações da IA e que só confiaria nos números se pudesse conferir a fonte. Ele deu nota 5 de 5 para a utilidade do exemplo, e a parte mais útil seriam as perguntas para a reunião. Isso é evidência qualitativa de um único caso e não entra na conta.

### Sensibilidade (custo médio da hora, R$ 74,40)

Pior caso: 30 min de tempo atual, limite superior do tempo com a ferramenta e 6 reuniões. Melhor caso: 60 min, limite inferior e 10 reuniões.

| cenário | caso | economia por reunião | horas por mês | economia por mês | ROI |
|---|---|---|---|---|---|
| A | pior | 10 min | 1,00 h | R$ 74,40 | 1.882 vezes |
| A | melhor | 45 min | 7,50 h | R$ 558,04 | 8.471 vezes |
| B | pior | 15 min | 1,50 h | R$ 111,61 | 2.824 vezes |
| B | melhor | 50 min | 8,33 h | R$ 620,04 | 9.412 vezes |

**Ponto de equilíbrio:** a ferramenta se paga se economizar cerca de 0,3 segundo por raio-x (R$ 0,006588 ÷ R$ 74,40 por hora).

## 8. Leitura e limites

1 - **Um ROI de milhares de vezes vem de o custo da API ser ínfimo.** O número mais informativo é a economia de cerca de 3,7 a 4,3 horas por mês, ou R$ 273 a R$ 322 por executivo, no custo médio da hora.
2 - **Um único entrevistado.** O tempo atual e as reuniões por mês vêm de faixas marcadas por uma pessoa, e os pontos médios são premissas.
3 - **O ROI não inclui** desenvolvimento, servidor num uso real nem encargos trabalhistas (o que subestima o custo da hora).

## Como conferir as contas

Todas as contas foram refeitas pelo Eduardo com o Claude Code em 12/11/2026 e bateram, inclusive a sensibilidade e o ponto de equilíbrio:

```python
# Refaz as contas do ROI (cenário A, custo médio da hora). Rode com: python -c "..." ou cole no Python.
custo_raio_x = 0.0011847 * 5.5606          # US$ → R$: 0,006588 por raio-x
custo_mes = 8 * custo_raio_x                # 8 raio-x por mês: R$ 0,0527
hora = 12_500 / 168                          # custo médio da hora: R$ 74,40
economia_h = 8 * (45 - 17.5) / 60            # horas economizadas por mês: 3,67
print(round(economia_h * hora, 2), round(economia_h * hora / custo_mes))  # → 272.82 5177
```
