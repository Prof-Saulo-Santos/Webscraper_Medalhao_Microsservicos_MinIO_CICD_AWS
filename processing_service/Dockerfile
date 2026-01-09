# Use uma imagem slim
FROM python:3.12-slim

WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Copia arquivos de config
COPY pyproject.toml poetry.lock ./

# Instala dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Models cache e outras otimizações podem ser adicionadas aqui

# Copia código
COPY . .

# CMD padrão para API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

# OBS: Para rodar em modo Worker (batch), sobrescreva o CMD no docker-compose ou runtime:
# CMD ["python", "app/services/processor_service.py", "--limit", "100"]
