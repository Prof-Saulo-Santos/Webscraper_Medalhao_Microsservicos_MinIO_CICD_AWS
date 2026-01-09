FROM python:3.12-slim

WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Garante que o python encontre o módulo 'app'
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Copia arquivos de config
COPY pyproject.toml poetry.lock* ./

# Instala dependências
# --no-root: não instala o projeto como lib
# poetry-plugin-export não é necessário pois estamos usando install direto
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copia código
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
