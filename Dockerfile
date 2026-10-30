# Imagem da tela do Raio-X. O docker-compose.yml sobe esta imagem junto com o PostgreSQL.
# Mesma versão de Python do CI (.github/workflows/testes.yml) e do requirements.txt.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala as dependências antes de copiar o código, aproveitando o cache.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Executa a aplicação com um usuário sem privilégios de administrador.
# A data/ e o .env não entram na imagem (.dockerignore): a data/ chega como volume e a chave como variável.
# O chown deixa o appuser gravar em /app (o cache do pytest, por exemplo); o WORKDIR cria a pasta como root.
RUN useradd --create-home --uid 10001 appuser && chown appuser:appuser /app
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8501

# O Docker pergunta à tela, de 30 em 30 s, se ela está de pé (o slim não tem curl; o Python faz o papel).
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# Roda de dentro de app/: é onde o Streamlit acha o tema (app/.streamlit/config.toml).
CMD ["sh", "-c", "cd app && exec python -m streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]
