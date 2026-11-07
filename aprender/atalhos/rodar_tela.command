#!/bin/zsh
# Dê dois cliques para abrir a tela do Raio-X no navegador (versão com dados falsos).
cd "$(dirname "$0")/../.."   # raiz do repositório (o atalho fica em aprender/atalhos/)
# Ambiente Python: .venv do repositório; se não existir, o venv ~/bootcamp do Eduardo; senão, cria a .venv.
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f "$HOME/bootcamp/bin/activate" ]; then
  source "$HOME/bootcamp/bin/activate"
else
  python3.14 -m venv .venv && source .venv/bin/activate || exit 1
fi
pip install -q -r requirements.txt
echo "Abrindo a tela em http://localhost:8501 ... Para parar, feche esta janela."
cd app && streamlit run streamlit_app.py   # dentro de app/ para ler o tema em app/.streamlit
