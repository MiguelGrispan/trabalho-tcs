#!/bin/zsh
# Dê dois cliques para refazer os grupos (K-means) e o gráfico da silhueta.
cd "$(dirname "$0")/.."   # raiz do repositório (onde ficam .venv, .env e requirements.txt)
# Ambiente Python: .venv do repositório; se não existir, o venv ~/bootcamp do Eduardo; senão, cria a .venv.
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f "$HOME/bootcamp/bin/activate" ]; then
  source "$HOME/bootcamp/bin/activate"
else
  python3 -m venv .venv && source .venv/bin/activate
fi
pip install -q -r requirements.txt
python -m raiox.segmentos
echo ""
echo "Gráfico em docs/graficos/silhueta.png. Pode fechar esta janela."
