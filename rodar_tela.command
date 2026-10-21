#!/bin/zsh
# Dê dois cliques para abrir a tela do Raio-X no navegador (versão com dados falsos).
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
echo "Abrindo a tela em http://localhost:8501 ... Para parar, feche esta janela."
streamlit run app.py
