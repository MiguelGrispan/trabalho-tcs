#!/bin/zsh
# Dê dois cliques neste arquivo no Finder para rodar a prova SEM chamar a IA.
cd "$(dirname "$0")"
# Ambiente Python: .venv do repositório; se não existir, o venv ~/bootcamp do Eduardo; senão, cria a .venv.
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f "$HOME/bootcamp/bin/activate" ]; then
  source "$HOME/bootcamp/bin/activate"
else
  python3 -m venv .venv && source .venv/bin/activate
fi
pip install -q -r requirements.txt
python prova_ia.py --sem-llm
echo ""
echo "Pronto. Pode fechar esta janela."
