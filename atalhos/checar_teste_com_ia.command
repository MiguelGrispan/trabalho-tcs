#!/bin/zsh
# Dê dois cliques para testar o checador com a IA, usando os dados falsos com erros de propósito.
cd "$(dirname "$0")/.."   # raiz do repositório (onde ficam .venv, .env e requirements.txt)
# Ambiente Python: .venv do repositório; se não existir, o venv ~/bootcamp do Eduardo; senão, cria a .venv.
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f "$HOME/bootcamp/bin/activate" ]; then
  source "$HOME/bootcamp/bin/activate"
else
  python3 -m venv .venv && source .venv/bin/activate
fi
python -m raiox.checagem --teste --com-ia 2>&1 | tee resultado_checagem.txt
echo ""
echo "Resultado salvo em resultado_checagem.txt, anomalias.csv e auditoria_ia.csv. Pode fechar esta janela."
