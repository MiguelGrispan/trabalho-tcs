#!/bin/zsh
# Dê dois cliques para abrir a tela com a IA de verdade (Gemini). Gasta crédito: cerca de US$ 0,0008 por raio-x.
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
export RAIOX_IA_REAL=1
echo "Abrindo a tela com IA em http://localhost:8501 ... Para parar, feche esta janela."
streamlit run app.py
