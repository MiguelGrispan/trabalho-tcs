#!/bin/zsh
# Dê dois cliques para guardar a sua chave do Gemini no arquivo .env (fica só no seu Mac).
cd "$(dirname "$0")/../.."   # raiz do repositório (o atalho fica em aprender/atalhos/)
echo "Cole a sua chave do Google AI Studio e aperte Enter."
echo "(Por segurança, o texto não aparece enquanto você cola.)"
read -rs "CHAVE?Chave: "
echo ""
if [[ -z "$CHAVE" ]]; then
  echo "Nenhuma chave colada. Feche e tente de novo."
else
  echo "GOOGLE_API_KEY=$CHAVE" > .env
  echo "Chave guardada no arquivo .env (termina em ...${CHAVE: -4})."
fi
echo "Pode fechar esta janela."
