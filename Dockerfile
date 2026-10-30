# Use a mesma versão de Python testada pelo projeto. 3.12 é uma base inicial.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala as dependências antes de copiar o código, aproveitando o cache.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Executa a aplicação com um usuário sem privilégios de administrador.
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8501

# Confirme o nome do arquivo que inicia a aplicação antes de construir a imagem.
CMD ["python", "-m", "streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
