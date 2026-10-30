---
name: explicar
description: Ensina, para iniciante, o que um trecho do código do Raio-X faz e por quê, no método ler → prever → rodar → explicar, e treina as perguntas da banca. Use quando alguém do time pedir para entender ou defender um arquivo, uma função ou uma decisão do projeto (ex.: "/explicar raiox/segmentos.py matriz", "me explica o validador", "como eu defendo o K-means na banca").
---

# Explicar o código (treino para a banca)

Quem chama quer **saber explicar sozinho**, sem consulta, na banca. O objetivo não é você explicar bem:
é a pessoa conseguir explicar depois. Fale em português simples e faça uma coisa de cada vez.

## Regras

- **Só leia e rode.** Não altere nenhum arquivo, nem para "melhorar o exemplo".
- **Nunca chame o Gemini.** Nada de `RAIOX_IA_REAL=1` nem `--com-ia`. Rode sempre com `RAIOX_DADOS=falsos`,
  que usa as 30 empresas inventadas e não grava em `data/`.
- **Toda afirmação vem com arquivo e linha**, e você abriu o arquivo antes de afirmar. O que você não conferiu, chame de suposição.
- Use o Python do projeto: `.venv/bin/python` se existir; senão, `~/bootcamp/bin/python`.

## Passo a passo

1. **Escolher o alvo.** Use o que a pessoa escreveu depois de `/explicar`. Se ela não disse nada, mostre a tabela
   da seção 8 do `docs/PLANO.md` ("o que ele precisa saber explicar") e pergunte por onde começar.
2. **Ler.** Abra a função e mostre só o trecho que importa (até uns 25 linhas), com o número das linhas.
   Diga em uma frase o que entra e o que sai.
3. **Prever.** Antes de rodar, pergunte o que a pessoa acha que vai sair. **Espere a resposta.** Não responda por ela.
4. **Rodar.** Rode um comando curto que mostre o resultado de verdade, por exemplo:
   `RAIOX_DADOS=falsos <python> -c "from raiox import segmentos as s; ..."`. Mostre a saída e compare com a previsão.
5. **Explicar o porquê.** Para cada decisão do trecho: o que faz, por que foi feita assim e o que daria errado sem ela.
   Ligue a decisão ao requisito do professor que ela atende, com o arquivo e o item (`docs/professor/requisitos_projeto.MD`
   ou `docs/professor/guia_projeto_final.pdf`; o status está no `docs/REQUISITOS.md`).
6. **Treinar a banca.** Faça 3 perguntas, uma de cada vez, como um professor ou um especialista da TCS faria
   (ex.: "por que K-means e não outro modelo?", "como você sabe que a IA não inventa número?").
   Depois de cada resposta, diga o que ficou certo, o que faltou e onde está a prova no código.
7. **Fechar.** Termine com 3 linhas: o que a pessoa já explica sozinha, o que ainda precisa rever
   e qual trecho estudar em seguida.

## Atalhos úteis

- Fluxo inteiro, do dado ao texto: `aprender/passo_a_passo.ipynb` e `aprender/entenda-o-projeto.md`.
- Regra de ouro (a IA nunca escreve números): `validar_e_preencher()` em `raiox/ia.py` e os testes `test_regra_de_ouro_*`.
- Formatos entre as partes: `contratos.md`.
