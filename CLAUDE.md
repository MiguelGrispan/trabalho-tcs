# Raio-X Comercial · contexto para o Claude Code

Projeto final da trilha IA Aplicada (SENAI/TCS). Equipe: Marcos (dados), Eduardo (IA e gestão),
Náthally (produto e métricas, deck), Miguel (tela e infraestrutura). Entrega na semana de 09–15/11/2026.

## O produto
O vendedor escolhe uma companhia aberta da CVM, informa o produto e o objetivo da reunião e recebe:
6 indicadores com fonte (DFP), posição contra o grupo de empresas parecidas (K-means), 3 a 5 perguntas
ligadas ao produto, lacunas e 5 empresas parecidas para prospectar (vizinhos mais próximos).

## Regra de ouro
O LLM (Gemini via LangChain) nunca escreve números. Ele usa marcadores como {margem_ebit};
o validador remove qualquer dígito fora de marcador; o código troca os marcadores pelos valores da tabela.
Não quebre essa regra em nenhuma mudança.

## Repositório
github.com/MiguelGrispan/trabalho-tcs (privado). Cada pessoa trabalha na sua branch (`eduardo`, `tratamento_dados`...) e junta na `main` por pull request.
Dados brutos da CVM e arquivos gerados ficam em `data/`, que não vai para o Git.

## Estrutura
- `checar_indicadores.py` (Marcos): regras de sanidade; `--com-ia` pede ao Gemini a causa provável. A IA não altera dados.
- `segmentos.py` (Eduardo): K-means (k pela silhueta) e 5 vizinhos → `data/segmentos.csv`.
- `ia.py` (Eduardo): `preparar_raio_x(cd_cvm, produto, objetivo)` no formato do contrato C3.
- `app.py` (Miguel): Streamlit. `RAIOX_IA_REAL=1` usa o Gemini; sem isso, texto sem IA.
- `falsos/`: dados e módulos falsos no formato dos contratos. `tabela_falsa.csv`: 30 empresas inventadas.
- `prova_ia.py`: arquivo de estudo da semana 1. Não é o código oficial.
- `contratos.md`: formatos entre as partes (C1 a C4). Não mude um formato sem avisar quem recebe.

## Como rodar
- Ambiente Python: `.venv` na raiz do repositório (`python -m venv .venv`). No Mac do Eduardo, os atalhos `.command` usam o venv `~/bootcamp` se a `.venv` não existir.
- Testes: `python -m pytest -q` (não chamam a API).
- Tela: `streamlit run app.py`.

## Cuidados
- Não leia, mostre nem envie o conteúdo de `.env` (chave do Gemini, plano pré-pago).
- Toda chamada ao Gemini gasta crédito (≈ US$ 0,0008 por raio-x). Avise antes de rodar em lote.
- O Eduardo está aprendendo: explique cada mudança em português simples e prefira passos pequenos.
