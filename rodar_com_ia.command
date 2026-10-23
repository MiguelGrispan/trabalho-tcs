#!/bin/zsh
# Dê dois cliques para rodar a prova COM a IA (Gemini). Precisa da chave no .env.
cd "$(dirname "$0")"
# Ambiente Python: .venv do repositório; se não existir, o venv ~/bootcamp do Eduardo; senão, cria a .venv.
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f "$HOME/bootcamp/bin/activate" ]; then
  source "$HOME/bootcamp/bin/activate"
else
  python3 -m venv .venv && source .venv/bin/activate
fi
if [[ ! -f .env ]]; then
  echo "Falta a chave. Rode primeiro o configurar_chave.command."
else
  python prova_ia.py 2>&1 | tee resultado_com_ia.txt
  echo ""
  echo "O resultado também foi salvo em resultado_com_ia.txt."
fi
echo "Pode fechar esta janela."
