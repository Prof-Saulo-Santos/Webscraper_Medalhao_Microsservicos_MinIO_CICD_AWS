# 1. Visão Geral da Arquitetura

O projeto segue uma arquitetura de microserviços onde cada componente possui responsabilidade única.

*   **Ingestion Service (Fase 1 - Completa):** Responsável por coletar dados brutos (Scraping) e salvar na camada **Bronze**.
*   **Processing Service (Fase 2 - Futura):** Processará dados da Bronze para Silver (limpeza/embeddings).
*   **Frontend Service (Fase 3 - Futura):** Interface do usuário (Streamlit).

**Tecnologias da Fase 1:**
*   **Linguagem:** Python 3.12
*   **Gerenciador:** Poetry
*   **Web Framework:** FastAPI
*   **Containerização:** Docker
*   **Qualidade:** Pre-commit, Black, Ruff, Pytest

---

# Fase 1 — Ingestion Service (Bronze)

## 1. Objetivo da Fase 1

Implementar um **microserviço de ingestão** responsável por:

* Realizar **web scraping via HTML** no arXiv (requisito do projeto)
* Extrair dados brutos de artigos científicos
* Persistir os dados **sem transformação** na **Camada Bronze**
* Utilizar **S3 compatível** (MinIO local / AWS S3 em produção)

Nada além disso.

---

## 2. Pré-requisitos

### 2.1 Software necessário

* Python **3.12+**
* Docker
* Docker Compose
* Git

Verificação rápida:

```bash
python --version
docker --version
docker compose version
git --version
```

---

## 3. Criação do Projeto

```bash
mkdir ingestion_service
cd ingestion_service
git init
```

### 3.1 Ignorando arquivos (.gitignore)

Crie o arquivo `.gitignore` na raiz:

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
.pytest_cache/
.coverage
htmlcov/
dist/
.DS_Store
```

---

## 4. Estrutura de Diretórios

```text
project_root/               <-- (Raiz do Monorepo)
├── docs/                   <-- (Documentação Geral)
│   └── passo_a_passo_fase_1.md
├── README.md               <-- (Visão Geral das 4 Fases)
├── ingestion_service/      <-- (Fase 1 - Completa)
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │   └── storage.py
│   │   ├── domain/
│   │   │   ├── article.py
│   │   │   ├── repository.py
│   │   │   └── scraper.py
│   │   ├── repositories/
│   │   │   └── s3_repository.py
│   │   ├── scrapers/
│   │   │   └── arxiv_scraper.py
│   │   ├── services/
│   │   │   └── ingestion_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_domain.py
│   │   ├── test_ingestion.py
│   │   ├── test_pagination.py
│   │   ├── test_repository.py
│   │   ├── test_scraper.py
│   │   └── test_storage.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── Makefile
│   ├── pyproject.toml
│   └── README.md           <-- (Doc Específica da Ingestão)
├── processing_service/     <-- (Fase 2 - Placeholder)
├── frontend_service/       <-- (Fase 3 - Placeholder)
└── aws_infrastructure/     <-- (Fase 4 - Doc/IaC)
    └── README.md
```

---

## 5. Configuração do Projeto (pyproject.toml)

```toml
[tool.poetry]
name = "ingestion-service"
version = "0.1.0"
description = "Ingestion Service - Camada Bronze"
authors = ["Seu Nome"]
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115"
uvicorn = "^0.30"
beautifulsoup4 = "^4.12"
boto3 = "^1.34"
pydantic = "^2.9"
pydantic-settings = "^2.6"
httpx = "^0.28.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2"
bump2version = "^1.0.1"
pytest-asyncio = "^1.3.0"
pre-commit = "^3.7"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

> [!TIP]
> **Gerenciamento de Versão (bump2version):**
> O `bump2version` foi incluído para automatizar o versionamento semântico do projeto.
> **Importância:** Ele garante consistência alterando a versão em múltiplos arquivos (ex: `pyproject.toml`, `app/main.py`) simultaneamente e criando a tag git correspondente, evitando erros manuais e descompasso de versões.

---

## 6. Variáveis de Ambiente (.env)


```env
USE_S3=True
S3_ENDPOINT=http://minio:9000
S3_BUCKET_NAME=arxiv-bronze
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
```

> [!WARNING]
> **Segurança em Produção:**  
> Evite credenciais no arquivo `.env` commitado. Para produção, utilize **Docker Secrets**, **AWS Systems Manager Parameter Store** ou **HashiCorp Vault**. Injete as variáveis apenas no momento do deploy (CI/CD).

---

## 7. Automação (Makefile)

O `Makefile` simplifica comandos comuns. Crie o arquivo na raiz:

```makefile
.PHONY: install test format lint run clean

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
	docker compose up --build -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-patch:
	poetry run bump2version patch --verbose

bump-minor:
	poetry run bump2version minor --verbose

bump-major:
	poetry run bump2version major --verbose
```

### 7.1 Pre-commit Hooks (Opcional)

Para garantir qualidade antes de cada commit, crie o arquivo `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.8
    hooks:
      - id: ruff
        args: [ --fix ]
```

Instale os hooks com:
```bash
poetry run pre-commit install
```


---

## 8. Código-Fonte

### 8.1 app/core/config.py

-   **Descrição:**
    *   Configura as variáveis de ambiente para o serviço de ingestão.
    *   Utiliza o Pydantic Settings para validação e serialização.
    *   Inclui campos como USE_S3, S3_ENDPOINT, S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY e AWS_REGION.  

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USE_S3: bool = True
    S3_ENDPOINT: str = "http://minio:9000"
    S3_BUCKET_NAME: str = "arxiv-bronze"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"

settings = Settings()
```

---

### 8.2 app/core/logger.py  

-   **Descrição:**
    *   Configura o logger para o serviço de ingestão.
    *   Utiliza o logging do Python para registro de logs.
    *   Define o nível de log como INFO.
    *   Inicializa o logger com o nome "ingestion_service".

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion_service")
```

---

### 8.2.1 app/core/storage.py  

-   **Descrição:**
    *   Gerencia a inicialização da infraestrutura de armazenamento (S3).
    *   Garante que o bucket configurado existe ao iniciar a aplicação.
    *   Isola a lógica de infraestrutura da lógica de repositório.

```python
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logger import logger

def initialize_buckets():
    """Garante que o bucket configurado existe."""
    if not settings.USE_S3:
        return

    client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    bucket = settings.S3_BUCKET_NAME
    try:
        client.head_bucket(Bucket=bucket)
        logger.info(f"Bucket '{bucket}' já existe.")
    except ClientError as e:
        error_code = e.response["Error"].get("Code")
        if error_code == "404":
            try:
                client.create_bucket(Bucket=bucket)
                logger.info(f"Bucket '{bucket}' criado com sucesso.")
            except Exception as create_error:
                logger.error(f"Erro ao criar bucket '{bucket}': {create_error}")
        else:
            logger.error(f"Erro ao verificar bucket: {e}")
```

---

### 8.3 app/domain/article.py

-   **Descrição:**
    *   Define o modelo de dados para os artigos.
    *   Utiliza o Pydantic para validação e serialização.
    *   Inclui campos como ID, título, autores, resumo, data de publicação, data de atualização, categorias, link e link PDF.   

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Author(BaseModel):
    name: str

class Article(BaseModel):
    id: str
    title: str
    authors: List[Author]
    summary: str
    published: datetime
    updated: datetime
    categories: List[str]
    link: str
    pdf_link: Optional[str] = None
```

---

### 8.3.1 app/domain/repository.py

-   **Descrição:**
    *   Define o protocolo (interface) para o repositório, permitindo Injeção de Dependência.

```python
from typing import Protocol, Dict, Any

class RepositoryProtocol(Protocol):
    async def save_json(self, key: str, data: Dict[str, Any]) -> None:
        """Salva um dicionário como JSON no repositório."""
        ...
```

### 8.3.2 app/domain/scraper.py

-   **Descrição:**
    *   Define o protocolo (interface) para o scraper, permitindo diferentes implementações de coleta.

```python
from typing import Protocol, List
from app.domain.article import Article

class ScraperProtocol(Protocol):
    async def fetch_articles(self, query: str, max_results: int, start: int = 0) -> List[Article]:
        """Busca artigos com base na query, paginação e offset."""
        ...
```

---

### 8.4 app/repositories/s3_repository.py

-   **Descrição:**
    *   Implementa o `RepositoryProtocol`.
    *   Foca exclusivamente na persistência de dados (SRP).
    *   Não gerencia mais criação de buckets (bootstrap removido).
    
```python
import json
import boto3
import asyncio
from app.core.config import settings
from app.core.logger import logger


class S3Repository:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT if settings.USE_S3 else None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    async def save_json(self, key: str, data: dict):
        try:
            await asyncio.to_thread(
                self.client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                ContentType="application/json",
            )
            logger.info(f"Objeto salvo com sucesso: {key}")
        except Exception as e:
            logger.error(f"Erro ao salvar objeto {key}: {e}")
```

---

### 8.5 app/services/ingestion_service.py

-   **Descrição:**
    *   Orquestra a ingestão: Utiliza o Scraper para buscar dados e o Repositório para salvar.
    *   Segue o Single Responsibility Principle (SRP) e Dependency Inversion Principle (DIP).

```python
from app.domain.repository import RepositoryProtocol
from app.domain.scraper import ScraperProtocol
from app.core.logger import logger
import random
import asyncio
from datetime import datetime


class IngestionService:
    def __init__(self, repository: RepositoryProtocol, scraper: ScraperProtocol):
        self.repo = repository
        self.scraper = scraper

    async def run(self, query: str, max_results: int = 50):
        logger.info(f"Iniciando ingestão de até {max_results} artigos para query='{query}'...")
        
        collected_count = 0
        start = 0
        batch_size = 50 # Padrão do arXiv
        
        while collected_count < max_results:
            # Garante que não pede mais do que o batch permite ou o que falta
            logger.info(f"Buscando página iniciando em {start}...")
            
            # Limita a busca ao tamanho do batch
            articles = await self.scraper.fetch_articles(query, batch_size, start=start)

            if not articles:
                logger.info("Nenhum artigo retornado. Encerrando busca.")
                break

            count_saved = 0
            for article in articles:
                payload = {
                    "ingestion_timestamp": datetime.now().isoformat(),
                    "ingestion_source": "arxiv_html",
                    "search_query": query,
                    "article_data": article.model_dump(mode="json"),
                }
                await self.repo.save_json(f"{article.id}.json", payload)
                count_saved += 1
            
            collected_count += count_saved
            start += len(articles)
            
            logger.info(f"Página processada. Coletados: {collected_count}/{max_results}")

            # Se veio menos artigos que o batch, significa que acabou a fonte
            if len(articles) < batch_size:
                break
                
            # Anti-Ban: Pausa se ainda não acabou
            if collected_count < max_results:
                wait_time = random.uniform(80.0, 90.0)
                logger.info(f"Aguardando {wait_time:.2f}s para próxima página (Anti-Ban)...")
                await asyncio.sleep(wait_time)
                
        logger.info(f"Ingestão concluída. Total coletado: {collected_count}")
```

### 8.5.1 app/scrapers/arxiv_scraper.py

-   **Descrição:**
    *   Implementação concreta do `ScraperProtocol` para o arXiv.
    *   Contém a lógica de HTTP Request, Parsing (BeautifulSoup) e transformação para modelo de domínio.

```python
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
from app.domain.article import Article, Author
from app.domain.scraper import ScraperProtocol
from app.core.logger import logger

class ArxivScraper:
    async def fetch_articles(self, query: str, max_results: int, start: int = 0) -> List[Article]:
        url = f"https://arxiv.org/search/?query={query}&searchtype=all&abstracts=show&order=-announced_date_first&size={max_results}&start={start}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) IngestionService/1.0"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Falha ao buscar página: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("li.arxiv-result")[:max_results]

        if not results:
            logger.warning(
                "Nenhum resultado encontrado. Verifique a query ou mudanças no layout do arXiv."
            )
            return []

        articles = []
        processed_count = 0
        for result in results:
            try:
                # Título
                title_elem = result.select_one("p.title")
                title = title_elem.get_text(strip=True) if title_elem else "Sem título"

                # ID do arXiv (Prioridade: PDF -> Abs -> Unknown)
                arxiv_id = None
                
                # Tenta pegar do Link PDF
                pdf_link_elem = result.select_one("p.list-pdf a[href*='/pdf/']")
                if pdf_link_elem:
                    href = pdf_link_elem["href"]
                    pdf_link = (
                        href if href.startswith("http") else f"https://arxiv.org{href}"
                    )
                    arxiv_id = pdf_link.split("/")[-1].replace(".pdf", "")
                else:
                    pdf_link = None

                # Tenta pegar do Link Abstract se falhou no PDF
                page_link_elem = result.select_one("a[href*='/abs/']")
                if page_link_elem:
                    href = page_link_elem["href"]
                    link = (
                        href if href.startswith("http") else f"https://arxiv.org{href}"
                    )
                    if not arxiv_id:
                        arxiv_id = link.split("/")[-1]
                else:
                    link = ""
                
                # Fallback final (garante unicidade global)
                if not arxiv_id:
                    unique_index = start + processed_count
                    arxiv_id = f"unknown_{unique_index}"

                # Autores
                authors_elems = result.select("p.authors a")
                authors = [Author(name=a.get_text(strip=True)) for a in authors_elems]

                # Abstract
                abstract_elem = result.select_one("span.abstract-full")
                summary = (
                    abstract_elem.get_text(separator=" ", strip=True)
                    if abstract_elem
                    else ""
                )

                # Datas (submitted / updated)
                date_span = result.find("span", string=lambda t: t and "Submitted" in t)
                if date_span:
                    try:
                        date_text = date_span.get_text(strip=True)
                        parts = date_text.split(";")
                        published_str = parts[0].replace("Submitted ", "").strip()
                        published = datetime.strptime(published_str, "%d %B %Y")

                        if len(parts) > 1:
                            updated_str = parts[1].replace("updated ", "").strip()
                            updated = datetime.strptime(updated_str, "%d %B %Y")
                        else:
                            updated = published
                    except (ValueError, IndexError) as e:
                        logger.warning(
                            f"Erro no parse de data '{date_text}' ({e}). Usando data atual."
                        )
                        published = updated = datetime.now()
                else:
                    published = updated = datetime.now()

                # Categorias
                categories = [
                    tag.get_text(strip=True)
                    for tag in result.select("span.primary-subject, span.subjects")
                ]

                article = Article(
                    id=arxiv_id,
                    title=title,
                    authors=authors,
                    summary=summary,
                    published=published,
                    updated=updated,
                    categories=categories or [query],
                    link=link,
                    pdf_link=pdf_link,
                )
                articles.append(article)
                processed_count += 1

            except Exception as e:
                logger.error(f"Erro ao processar um artigo: {e}")
                continue
        
        return articles
```

---

### 8.6 app/api/routes.py

-   **Descrição:**
    *   Define as rotas para o serviço de ingestão.
    *   Utiliza o FastAPI para definição de rotas.
    *   Inclui rotas para health check e ingestão de artigos.

```python
from fastapi import APIRouter, Query
from app.services.ingestion_service import IngestionService
from app.repositories.s3_repository import S3Repository
from app.scrapers.arxiv_scraper import ArxivScraper

router = APIRouter()

@router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}

@router.post("/ingest")
async def ingest(
    query: str = Query("cs.CL", description="Termo de busca no arXiv"),
    max_results: int = Query(
        50, description="Máximo de artigos a ingerir (paginação automática)"
    ),
):
    service = IngestionService(repository=S3Repository(), scraper=ArxivScraper())
    await service.run(query=query, max_results=max_results)
    return {
        "status": "ok",
        "message": f"Ingestão concluída para query='{query}' (até {max_results} resultados)"
    }
```

---

### 8.7 app/main.py

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.storage import initialize_buckets

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_buckets()
    yield
    # Shutdown

app = FastAPI(
    title="Ingestion Service - arXiv Bronze",
    description="Microserviço de ingestão de artigos do arXiv para camada Bronze",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)
```

---

## 9. Testes Automatizados

### 9.1 Unitários: tests/test_domain.py

Testa a lógica de negócio e validação dos modelos (Pydantic).

```python
from datetime import datetime
from app.domain.article import Article, Author

def test_article_model_creation():
    author = Author(name="Saulo")
    article = Article(
        id="123",
        title="Test Title",
        authors=[author],
        summary="Summary",
        published=datetime.now(),
        updated=datetime.now(),
        categories=["cs.CL"],
        link="http://test.com",
        pdf_link="http://test.com/pdf",
    )

    assert article.title == "Test Title"
    assert article.authors[0].name == "Saulo"
    assert "cs.CL" in article.categories

### 9.2 Scraper (Mock HTML): tests/test_scraper.py

Testa a lógica de parsing HTML isoladamente.

```python
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.scrapers.arxiv_scraper import ArxivScraper

MOCK_HTML = """
<li class="arxiv-result">
    <p class="title">Fake Article</p>
    <span class="abstract-full">Fake Summary</span>
    <p class="authors"><a href="#">Fake Author</a></p>
    <p class="list-pdf"><a href="/pdf/1234.5678">pdf</a></p>
    <span class="primary-subject">cs.CL</span>
</li>
"""

@pytest.mark.asyncio
@patch("app.scrapers.arxiv_scraper.httpx.AsyncClient")
async def test_scraper_fetch_articles_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = MOCK_HTML

    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_response
    mock_client_cls.return_value = mock_client

    scraper = ArxivScraper()
    articles = await scraper.fetch_articles("test", 1)

    assert len(articles) == 1
    assert articles[0].title == "Fake Article"
    assert articles[0].id == "1234.5678"

@pytest.mark.asyncio
@patch("app.scrapers.arxiv_scraper.httpx.AsyncClient")
async def test_scraper_network_failure(mock_client_cls):
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.side_effect = Exception("Network Down")
    mock_client_cls.return_value = mock_client

    scraper = ArxivScraper()

    with pytest.raises(Exception):
        await scraper.fetch_articles("test", 1)
```

### 9.2.1 Infraestrutura (Mock Boto3): tests/test_storage.py

Testa a inicialização dos buckets (infraestrutura).

```python
from unittest.mock import patch
from botocore.exceptions import ClientError
from app.core.storage import initialize_buckets

@patch("app.core.storage.settings")
@patch("app.core.storage.boto3.client")
def test_initialize_buckets_creates_if_missing(mock_boto, mock_settings):
    # Configurações do Mock
    mock_settings.USE_S3 = True
    mock_settings.S3_BUCKET_NAME = "arxiv-bronze"
    
    # Mock do Boto3 Client
    mock_client = mock_boto.return_value
    
    # Simula erro 404 (Not Found) ao checar o bucket
    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

    # Executa a função
    initialize_buckets()

    # Verifica se create_bucket foi chamado corretamente
    mock_client.create_bucket.assert_called_once_with(Bucket="arxiv-bronze")
```

### 9.3 Repositório (Mock Boto3): tests/test_repository.py

Testa a interação com o S3 simulando o cliente boto3. Verifica se arquivos são salvos corretamente.

```python
from unittest.mock import patch
import pytest
from app.repositories.s3_repository import S3Repository


@pytest.mark.asyncio
@patch("boto3.client")
async def test_save_json_calls_put_object(mock_boto):
    mock_client = mock_boto.return_value
    repo = S3Repository()

    data = {"key": "value"}
    await repo.save_json("test.json", data)

    mock_client.put_object.assert_called_once()
    call_args = mock_client.put_object.call_args[1]
    assert call_args["Bucket"] == "arxiv-bronze"
    assert call_args["Key"] == "test.json"
    assert b'{\n  "key": "value"\n}' in call_args["Body"]

```

### 9.4 Integração (Mock Requests): tests/test_ingestion.py

Testa o fluxo completo, incluindo tratamento de falhas e estrutura final.

```python
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.ingestion_service import IngestionService

@pytest.fixture(autouse=True)
def mock_sleep():
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_ingestion_success_flow(mock_sleep):
    # Setup Mock Scraper
    mock_scraper = AsyncMock()

    # Create a Fake Article object
    fake_article = MagicMock()
    fake_article.id = "1234.5678"
    fake_article.title = "Fake Article"
    fake_article.model_dump.return_value = {
        "id": "1234.5678",
        "title": "Fake Article",
        "authors": [{"name": "Fake"}],
        "summary": "Fake Summary",
    }

    mock_scraper.fetch_articles.return_value = [fake_article]

    # Setup Repo
    mock_repo = AsyncMock()

    service = IngestionService(repository=mock_repo, scraper=mock_scraper)
    await service.run(query="test", max_results=1)

    # Asserts
    mock_scraper.fetch_articles.assert_called_once()
    mock_repo.save_json.assert_called_once()

    args, _ = mock_repo.save_json.call_args
    filename, payload = args

    assert filename == "1234.5678.json"
    assert payload["ingestion_source"] == "arxiv_html"


@pytest.mark.asyncio
async def test_ingestion_scraper_failure(mock_sleep):
    # Setup Falha no Scraper
    mock_scraper = AsyncMock()
    mock_scraper.fetch_articles.side_effect = Exception("Scraper Failed")

    mock_repo = AsyncMock()
    service = IngestionService(repository=mock_repo, scraper=mock_scraper)

    # Deve propagar a exceção
    with pytest.raises(Exception):
        await service.run(query="test")
```

### 9.5 Paginação (Mock Loop): tests/test_pagination.py

Testa a lógica de loop e incremento de offset no `IngestionService`.

```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.ingestion_service import IngestionService
from app.domain.article import Article
from datetime import datetime

@pytest.mark.asyncio
async def test_pagination_loop_max_results():
    # Mock do Repositório
    mock_repo = AsyncMock()
    
    # Mock do Scraper
    mock_scraper = MagicMock()
    
    # Simula 2 páginas de resultados
    # 1ª chamada: 50 artigos
    page1 = [Article(
        id=f"1_{i}", title=f"Title {i}", authors=[], summary="", 
        published=datetime.now(), updated=datetime.now(), categories=[], link="", pdf_link=""
    ) for i in range(50)]
    
    # 2ª chamada: 10 artigos (totalizando 60, mas o teste pede 60)
    page2 = [Article(
        id=f"2_{i}", title=f"Title {i}", authors=[], summary="", 
        published=datetime.now(), updated=datetime.now(), categories=[], link="", pdf_link=""
    ) for i in range(10)]
    
    # Configura o side_effect para retornar page1, depois page2
    mock_scraper.fetch_articles = AsyncMock(side_effect=[page1, page2])
    
    service = IngestionService(repository=mock_repo, scraper=mock_scraper)
    
    # Mock do sleep para não esperar 80s de verdade
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await service.run(query="test", max_results=60)
        
        # Verifica se chamou fetch_articles 2 vezes
        assert mock_scraper.fetch_articles.call_count == 2
        
        # Verifica os argumentos de cada chamada (start deve incrementar)
        calls = mock_scraper.fetch_articles.call_args_list
        assert calls[0].kwargs['start'] == 0
        assert calls[1].kwargs['start'] == 50
        
        # Verifica se save_json foi chamado 60 vezes
        assert mock_repo.save_json.call_count == 60
        
        # Verifica se o sleep foi chamado (anti-ban)
        assert mock_sleep.call_count >= 1
```

### 9.6 Executando os testes

```bash
make install
make test
```

---

## 10. Dockerfile

-   **Descrição:**
    *   Define a imagem Docker para o serviço de ingestão.
    *   Utiliza o Python 3.12-slim como base.
    *   Define o diretório de trabalho como /app.
    *   Instala o Poetry e configura o Poetry para não criar virtualenvs.
    *   Instala as dependências do projeto.
    *   Copia o código-fonte para o diretório /app.
    *   Define o comando de execução como o Uvicorn.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


---

## 11. docker-compose.yml


```yaml
services:
  minio:
    image: minio/minio:latest # Imagem do MinIO
    command: server /data --console-address ":9001" # Comando para iniciar o MinIO
    ports:
      - "9000:9000" # Porta para o MinIO
      - "9001:9001" # Porta para o console do MinIO
    environment:
      MINIO_ROOT_USER: minioadmin # Usuário do MinIO
      MINIO_ROOT_PASSWORD: minioadmin # Senha do MinIO
    volumes:
      - minio_data:/data # Volume para persistência dos dados do MinIO

  ingestion_service:
    build: .
    env_file:
      - .env # Arquivo de variáveis de ambiente
    ports:
      - "8000:8000" # Porta para a API
    depends_on:
      - minio
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"] # Teste de saúde
      interval: 30s # Intervalo entre testes
      timeout: 10s # Timeout para o teste
      retries: 3 # Número de tentativas 

volumes:
  minio_data:
```

---

## 12. Execução (Via Makefile)

Para rodar tudo usando o Docker Compose:
 
 ```bash
 make run
 ```
 
 Acesse:
 
 *   API + Documentação interativa (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
 *   Console do MinIO: [http://localhost:9001](http://localhost:9001) (usuário: `minioadmin` | senha: `minioadmin`)
 
 Para verificar a saúde do serviço (comando executado):
 
 ```bash
 curl -v http://localhost:8000/health
 ```
 
 > **Resultado:** Status 200 OK (`{"status":"ok"}`).
 
 Para testar a ingestão:
 
1.  Abra o Swagger em `/docs`
2.  Execute `POST /ingest`
3.  Opcionalmente altere os parâmetros `query` (ex: "machine learning") e `max_results`
4.  Os arquivos JSON serão salvos no bucket `arxiv-bronze` do MinIO.

---

## 13. Versionamento (Primeiro Commit - Fase 1 Concluída)

Este passo consolida todo o trabalho da Fase 1. Certifique-se de estar na raiz do projeto (pasta `arxiv`).

```bash
# Na raiz do projeto (\arxiv)
git init
git add .
git commit -m "feat: initial commit ingestion service (fase 1)"
git branch -M main
git remote add origin <URL_DO_REPO>
git push -u origin main
```

---

## 14. Conclusão

*   Um microserviço totalmente funcional e testado (Concluído em 2025 / início de 2026)
*   Scraping robusto e atualizado do arXiv
*   Persistência correta na camada Bronze com chaves únicas
*   Ambiente Dockerizado idêntico ao de produção
*   Base sólida, limpa e preparada para a Fase 2 (Processing → Silver)

