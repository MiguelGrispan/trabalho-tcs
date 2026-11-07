#!/bin/zsh
# Dê dois cliques para rodar os testes automáticos (não chamam a IA, não gastam crédito).
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
python -m pytest -v
echo ""
echo "Pode fechar esta janela."
