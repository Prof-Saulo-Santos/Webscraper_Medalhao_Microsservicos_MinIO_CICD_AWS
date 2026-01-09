# Fase 3 — Frontend Service (Busca & Visualização)

## 1. Objetivo da Fase 3

Implementar a **Interface de Usuário (Frontend)** responsável por:

*   Interagir com o usuário final (Pesquisadores/Alunos).
*   Receber a query de busca em linguagem natural.
*   **Vector Search (MVP):** Carregar os dados da camada **Silver** (S3) e realizar busca semântica em memória (Cosine Similarity).
*   Exibir os resultados (Artigos) com metadados e Score de similaridade.

> [!NOTE]
> **Arquitetura (MVP vs VectorDB):**
> Para esta fase, adotarei uma estratégia **Simples e Robusta**: Carregar os dados processados (JSONs com Embeddings) do MinIO para um DataFrame em memória(`pandas`/`polars`) ao iniciar a aplicação.
> Isso elimina a necessidade de gerenciar um VectorDB complexo (Qdrant/Milvus) neste momento, sendo suficiente para volumes de até ~50k artigos.

---

## 2. Pré-requisitos

### 2.1 Software necessário

*   Python **3.12+**
*   Docker & Docker Compose
*   Poetry
*   Acesso à **Camada Silver** (Bucket `arxiv-silver` populado pela Fase 2)

---

## 3. Criação do Projeto

Como estamos em um **Monorepo**, apenas crie a pasta do serviço na raiz, caso ela não exista:

```bash
mkdir -p frontend_service
cd frontend_service
```

### 3.1 Ignorando arquivos (.gitignore)

Mesmo no Monorepo, é boa prática ter `.gitignore` específico para o serviço (para ignorar artifacts locais de build), embora o da raiz também se aplique.

Crie o arquivo `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
.pytest_cache/
.coverage
htmlcov/
dist/
# Streamlit
.streamlit/
```

### 3.2 Ignorando contexto Docker (.dockerignore)

```text
.git
.gitignore
__pycache__/
*.pyc
*.pyo
*.pyd

.env
.env.*

.venv/
venv/

data/
models/
cache/
artifacts/

node_modules/
dist/
build/

*.ipynb
*.csv
*.parquet
*.pdf

# Optional: keep image small
tests/
README.md
```

---

## 4. Estrutura de Diretórios (Streamlit Pattern)

Estrutura simplificada para aplicação Streamlit:

```text
frontend_service/
├── app/
│   ├── components/         <-- Componentes de UI (Sidebar, Cards)
│   ├── core/
│   │   ├── config.py       <-- Configurações (Env vars)
│   │   └── client.py       <-- Cliente S3 / MinIO
│   ├── services/           <-- Lógica de Busca (Search Engine)
│   ├── __init__.py
│   └── main.py             <-- Entrypoint do Streamlit
├── tests/
│   ├── test_search.py
│   └── __init__.py
├── .dockerignore
├── .bumpversion.cfg
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

---

## 5. Configuração do Projeto (pyproject.toml)

```toml
[tool.poetry]
name = "frontend-service"
version = "0.3.0"
description = "Frontend Service - Busca Semântica com Streamlit"
authors = ["Seu Nome"]
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.12"
streamlit = "^1.32"
pandas = "^2.2"
boto3 = "^1.34"
pydantic = "^2.9"
pydantic-settings = "^2.6"
# ML para recriar embedding da query
torch = { version = "^2.2", source = "pytorch-cpu" }
transformers = "^4.39"
scikit-learn = "^1.4" # Para cosine_similarity
plotly = "^5.20"

[[tool.poetry.source]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
priority = "explicit"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2"
black = "^24.4"
ruff = "^0.4"
bump2version = "^1.0.1"
pre-commit = "^4.5.0"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 5.1 Versionamento Automatizado (`.bumpversion.cfg`)

Arquivo de configuração para versionamento automático.

```ini
[bumpversion]
current_version = 0.3.0
commit = True
tag = True

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"
```

---

## 6. Variáveis de Ambiente (.env)

```env
# Infraestrutura S3
S3_ENDPOINT=http://localhost:9000
S3_BUCKET_SILVER=arxiv-silver
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1

# Modelo (Deve ser o mesmo da Fase 2!)
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## 6.1 Automação (Makefile)

O `Makefile` padroniza os comandos de desenvolvimento, facilitando a vida de quem entra no projeto.

```makefile
.PHONY: install test format lint run run-local clean bump-minor

install:
	poetry install

test:
	poetry run pytest tests/ -v

format:
	poetry run ruff check --fix .
	poetry run black .

lint:
	poetry run ruff check .
	poetry run black --check .

run:
	# Roda via Docker Compose (Produção/Homologação)
	docker compose up --build -d

run-local:
	# Roda nativamente para desenvolvimento rápido
	poetry run streamlit run app/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-minor:
	poetry run bump2version minor --verbose
```

---

## 7. Código-Fonte Principal (Implementação)

### 7.1 Configuração (`app/core/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    S3_ENDPOINT: str = "http://minio:9000"
    S3_BUCKET_SILVER: str = "arxiv-silver"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

### 7.2 Lógica de Busca (`app/services/search_engine.py`)

Esta classe carrega os dados e executa a busca.

> [!TIP]
> **Cache do Streamlit:** Use `@st.cache_resource` para não recarregar o Modelo e os Dados a cada interação do usuário.

```python
import streamlit as st
import pandas as pd
import boto3
import json
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
from app.core.config import settings

class SearchEngine:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.tokenizer = None
        self.model = None
        self.df = pd.DataFrame()

    @st.cache_resource
    def load_model(_self):
        """Carrega o modelo BERT para memória (Singleton)."""
        tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
        model = AutoModel.from_pretrained(settings.MODEL_NAME)
        return tokenizer, model

    @st.cache_data
    def load_data(_self):
        """Baixa TODOS os JSONs da Silver e cria um DataFrame."""
        # 1. Listar objetos
        try:
            response = _self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_SILVER)
        except Exception:
            return pd.DataFrame()
        
        if "Contents" not in response:
            return pd.DataFrame()

        data = []
        # 2. Ler cada JSON (Para prod, usar Parquet é melhor!)
        for obj in response["Contents"]:
            key = obj["Key"]
            file_obj = _self.s3.get_object(Bucket=settings.S3_BUCKET_SILVER, Key=key)
            content = json.loads(file_obj["Body"].read())
            data.append(content)

        return pd.DataFrame(data)

    def search(self, query: str, top_k: int = 5):
        # Inicializa resources se necessário
        if self.model is None:
            self.tokenizer, self.model = self.load_model()
        
        # Recarrega dados se estiver vazio (ou implementa botão de refresh)
        if self.df.empty:
            self.df = self.load_data()

        if self.df.empty:
            return []

        # 1. Embed da Query
        inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean Pooling (Mesma lógica da Fase 2)
        embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]
        mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
        sum_embeddings = torch.sum(embeddings * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        query_embedding = (sum_embeddings / sum_mask)[0].numpy()

        # 2. Calcular Similaridade (Matrix operation)
        # Assume que o DF tem coluna 'embedding' como lista de floats
        doc_embeddings = list(self.df['embedding'].values)
        
        # Scikit-learn cosine_similarity
        scores = cosine_similarity([query_embedding], doc_embeddings)[0]
        
        # 3. Adicionar scores e filtrar
        self.df['score'] = scores
        results = self.df.sort_values(by='score', ascending=False).head(top_k)
        
        return results.to_dict('records')

```

### 7.3 Interface Gráfica (`app/main.py`)

```python
import streamlit as st
from app.services.search_engine import SearchEngine

def main():
    st.set_page_config(page_title="ArXiv Semantic Search", layout="wide")
    
    st.title("📚 ArXiv Semantic Search")
    st.markdown("Busca inteligente em artigos científicos usando BERT embeddings.")

    # Sidebar
    with st.sidebar:
        st.header("Configurações")
        top_k = st.slider("Número de resultados", 1, 20, 5)
        if st.button("Reload Data"):
             st.cache_data.clear()
             st.success("Cache limpo! Recarregue a busca.")

    # Input
    query = st.text_input("O que você está procurando?", placeholder="Ex: 'Applications of LLMs in Healthcare'")

    engine = SearchEngine()

    if query:
        with st.spinner("Pesquisando..."):
            results = engine.search(query, top_k=top_k)
        
        st.write(f"Encontrados {len(results)} resultados relevantes.")
        
        for item in results:
            with st.expander(f"{item['title']} (Score: {item['score']:.4f})"):
                st.markdown(f"**Categories:** {item['categories']}")
                st.markdown(f"**Summary:** {item['summary']}")
                st.caption(f"ID: {item['id']}")

if __name__ == "__main__":
    main()
```

---

### 7.4 Testes Automatizados (`tests/test_search.py`)

Para garantir que a lógica de busca e cálculo de similaridade funcione sem precisar subir o Streamlit ou conectar na AWS real, usamos `pytest` com `unittest.mock`.

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from app.services.search_engine import SearchEngine

@pytest.fixture
def mock_s3_data():
    return [
        {"id": "1", "title": "Paper A", "summary": "Sum A", "embedding": [1.0, 0.0, 0.0], "categories": ["cs.AI"]},
        {"id": "2", "title": "Paper B", "summary": "Sum B", "embedding": [0.0, 1.0, 0.0], "categories": ["cs.CL"]},
    ]

@patch("app.services.search_engine.boto3")
@patch("app.services.search_engine.AutoTokenizer")
@patch("app.services.search_engine.AutoModel")
def test_search_engine_logic(mock_model_cls, mock_tokenizer_cls, mock_boto, mock_s3_data):
    # 1. Setup Mocks
    # Mock do S3
    mock_s3_client = Mock()
    mock_boto.client.return_value = mock_s3_client
    
    # Simula listagem de arquivos
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "1.json"}, {"Key": "2.json"}]
    }
    
    # Simula retorno do conteúdo dos arquivos (streaming body)
    def get_object_side_effect(Bucket, Key):
        import json
        from io import BytesIO
        data = mock_s3_data[0] if Key == "1.json" else mock_s3_data[1]
        body = BytesIO(json.dumps(data).encode("utf-8"))
        return {"Body": body}
    
    mock_s3_client.get_object.side_effect = get_object_side_effect

    # Mock do BERT (evitar download/loading pesado)
    mock_tokenizer = Mock()
    mock_model = Mock()
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
    mock_model_cls.from_pretrained.return_value = mock_model

    # Simula output do modelo (Tensor)
    import torch
    # SETUP SIMPLIFICADO: Mockar a funçao tokenizer para retornar dict
    mock_tokenizer.return_value = {"input_ids": torch.tensor([[1]]), "attention_mask": torch.tensor([[1]])}
    
    # Mock output do modelo: last_hidden_state com shape [1, 1, 3]
    # Se a query for [1, 0, 0], score com Paper A (1,0,0) será 1.0.
    mock_output = Mock()
    mock_output.last_hidden_state = torch.tensor([[[1.0, 0.0, 0.0]]]) 
    mock_model.return_value = mock_output

    # 2. Execução
    engine = SearchEngine()
    # Force load (bypass streamlit cache decoration issues in raw test if needed, 
    # but mocks handle imports usually. If @st.cache fails in test, mock st)
    with patch("app.services.search_engine.st"): 
        results = engine.search("fake query", top_k=2)

    # 3. Asserts
    assert len(results) == 2
    # Paper A deve ser o primeiro pois query [1,0,0] == Paper A [1,0,0] (Score 1.0)
    assert results[0]["id"] == "1"
    assert results[0]["score"] > 0.9
    
    # Paper B [0,1,0] deve ter score baixo com query [1,0,0] (Ortogonal = 0.0)
    assert results[1]["id"] == "2"
    assert results[1]["score"] < 0.1
```

---

## 8. Dockerfile

Para facilitar a execução sem conflitos de ambiente.

```dockerfile
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
```

Com `docker-compose.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./app:/app/app  # Hot reload
    networks:
      - arxiv-shared
    environment:
      # Sobrescreve endpoint para comunicação interna do Docker
      - S3_ENDPOINT=http://arxiv-minio:9000

networks:
  arxiv-shared:
    external: true
```

---

## 9. Execução

### 9.1 Preparação (Instalação e Testes)

Antes de rodar, garanta que tudo está instalado e testado:

```bash
# 0. Criar Rede Compartilhada (Importante!)
# Necessário para que o Frontend encontre o Processing/MinIO se estiverem na mesma rede.
# O docker-compose define a rede como 'external: true', então ela deve existir antes.
docker network create arxiv-shared || true

# 1. Instalar Dependências
make install

# 2. Rodar Testes Unitários
make test
```

### 9.2 Rodando a Aplicação

#### Opção A: Docker (Recomendado)
Para subir o ambiente completo (incluindo rede e variáveis):

```bash
make run
# ou: docker compose up --build -d
```

Acesse: `http://localhost:8501`

#### Opção B: Local (Desenvolvimento Rápido)
Para rodar apenas o Streamlit nativamente (conectando no MinIO via localhost):

```bash
make run-local
# ou: poetry run streamlit run app/main.py
```

---

## 10. Próximos Passos (Fase 4)

Com a aplicação funcional localmente (Bronze -> Silver -> Frontend), a próxima fase (**AWS Infrastructure**) focará em levar a arquitetura para a Nuvem:

1.  **Infraestrutura como Código (IaC):** Provisionar recursos.
2.  **Serviços Gerenciados:** Configuração.
3.  **CI/CD Cloud:** Deploy automático via GitHub Actions.

---

## 11. Versionamento e Deploy (Git Flow)

Seguindo o padrão do projeto:

1.  **Primeiro Commit (Frontend):**
    ```bash
    git add frontend_service/
    git commit -m "feat: implement frontend service with streamlit (phase 3)"
    ```

2.  **Release v0.3.0:**
    ```bash
    cd frontend_service
    poetry run bump2version minor --verbose
    # v0.2.0 -> v0.3.0
    ```

3.  **Push:**
    ```bash
    cd ..
    git push origin main --tags
    ```

