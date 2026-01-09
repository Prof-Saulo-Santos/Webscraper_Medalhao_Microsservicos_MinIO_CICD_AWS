# O projeto segue uma arquitetura de microserviços evolutiva, onde cada fase corresponde a um microserviço independente, com deploy, ciclo de vida e responsabilidade próprios.

## Status da Arquitetura:

- ✔ Fase 1 – Ingestion Service: IMPLEMENTADO
- ⏳ Fase 2 – Processing Service: PLANEJADO
- ⏳ Fase 3 – Frontend Service: PLANEJADO
- ⏳ Fase 4 – AWS: PLANEJADO


# Ingestion Service (Camada Bronze)

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat&logo=minio&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=flat&logo=poetry&logoColor=white)
![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Bump2Version](https://img.shields.io/badge/bump2version-semantic-ff69b4?style=flat)

Microserviço responsável pela coleta de artigos (via web scraping com paginação automática) do arXiv e persistência na camada Bronze (MinIO) sem transformações.

## 📋 Visão Geral

Este projeto compõe a **Fase 1** da arquitetura de microserviços.
Ele realiza o scraping de dados brutos do arXiv baseados em queries (ex: "cs.CL") e salva os resultados em arquivos JSON em um bucket S3 (MinIO).

### ✨ Funcionalidades Principais
*   **Scraping via HTML**: Coleta robusta simulando um navegador, independente da API oficial.
*   **Paginação Automática**: Capaz de coletar milhares de artigos (loop automático de páginas).
*   **Mecanismo Anti-Ban**: Sistema inteligente de rate-limiting (espera 80-90s entre páginas) para evitar bloqueios de IP.
*   **Resiliência**: Tratamento de erros de conexão e parse, garantindo que uma falha não pare todo o processo.
*   **Clean Architecture**: Separação clara entre Domínio, Aplicação (Service), Infraestrutura (Repository) e Interface (API).

### Tecnologias
*   **Python 3.12**
*   **FastAPI** (API REST)
*   **Poetry** (Gerenciamento de Dependências)
*   **Docker & Docker Compose** (Containerização)
*   **MinIO** (Object Storage compatível com S3)
*   **Bump2Version** (Versionamento Semântico)

## 🚀 Como Executar

### 📝 Documentação
* Você pode encontrar a documentação completa do projeto no arquivo `docs/passo_a_passo_fase_1.md` caso deseje estudar o processo de desenvolvimento.

### Pré-requisitos
*   Docker e Docker Compose instalados.

### Passos Rápido (Docker)


1.  Suba os containers:
    ```bash
    docker compose up --build -d
    ```
2.  Acesse a documentação da API:
    *   [http://localhost:8000/docs](http://localhost:8000/docs)
3.  **Exemplo de Uso (Ingestão)**:
    *   Endpoint: `POST /ingest`
    *   Parâmetros:
        *   `query`: Termo de busca (ex: "cs.CL")
        *   `max_results`: Quantidade total de artigos (ex: 100).
    *   > **Nota:** Se `max_results > 50`, o serviço entrará em modo de paginação, aguardando ~85s entre cada lote de 50 para evitar bloqueios.
4.  Acesse o Console do MinIO:
    *   [http://localhost:9001](http://localhost:9001)
    *   **User:** `minioadmin`
    *   **Password:** `minioadmin`

## 🛠️ Desenvolvimento Local

### Instalação
```bash
poetry install
poetry run pre-commit install
```

### Testes
Para rodar a suíte de testes automatizados (inclui testes de paginação mockados):
```bash
poetry run pytest tests/ -v
```

### Versionamento
Para subir a versão (patch, minor, major):
```bash
poetry run bump2version patch --verbose
```

## 📂 Estrutura
*   `app/`: Código fonte do serviço.
*   `tests/`: Testes unitários e de integração.
*   `Dockerfile` / `docker-compose.yml`: Configuração de containers.

## 📝 Autor
*   **Saulo Santos**    
    *   [GitHub](https://github.com/Prof-Saulo-Santos)
    *   [LinkedIn](https://www.linkedin.com/in/santossaulo/)


