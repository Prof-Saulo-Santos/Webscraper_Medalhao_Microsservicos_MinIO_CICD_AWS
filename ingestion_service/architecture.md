# Ingestion Service — arXiv (Camada Bronze)

## Visão Geral

Este repositório implementa um **microserviço de ingestão de dados** responsável por coletar artigos científicos do **arXiv** via **web scraping HTML** e persistir os dados **brutos** na **Camada Bronze** de um pipeline de dados.

O serviço foi projetado com foco em **arquitetura de microserviços**, **separação de responsabilidades**, **testabilidade** e **evolução futura**, servindo como base para processamento posterior (Silver), indexação e busca semântica.

---

## Arquitetura Interna do Microserviço

O microserviço de ingestão adota princípios derivados de **Clean Architecture** e **Hexagonal Architecture (Ports and Adapters)**, aplicados de forma pragmática e orientada a microserviços.

### Camadas

```text
API (FastAPI)
 └── Service Layer (IngestionService)
     └── Domain (Modelos + Protocolos)
         └── Infrastructure (Scraper / S3 / Storage)
```

### Responsabilidades

#### API Layer
*   **Exposição de endpoints:**
    *   `/health`
    *   `/ingest`
*   **Nenhuma lógica de negócio.**
*   Responsável apenas por receber requisições e delegar ao serviço.

#### Service Layer
*   **Orquestra o fluxo completo de ingestão.**
*   Coordena scraper e persistência.
*   **Não conhece detalhes de:**
    *   Scraping
    *   Storage
*   Depende apenas de abstrações (protocolos).

#### Domain
*   **Modelos de dados** usando Pydantic.
*   **Contratos (Protocols)** para:
    *   Scraper
    *   Repositório
*   Núcleo da aplicação, independente de frameworks.

#### Infrastructure
*   **Implementação concreta** de scraping (arXiv via HTML).
*   **Persistência** em storage S3 compatível:
    *   MinIO (local)
    *   AWS S3 (produção)
*   **Bootstrap de infraestrutura:**
    *   Criação e verificação de bucket.

### Princípios Arquiteturais Aplicados
*   **Single Responsibility Principle (SRP)**
*   **Dependency Inversion Principle (DIP)**
*   Separação clara entre Domínio e Infraestrutura.
*   Baixo acoplamento e alta coesão.
*   **Testabilidade como requisito de design:** O serviço depende exclusivamente de abstrações, permitindo troca futura de:
    *   Fonte de dados (ex: API oficial do arXiv).
    *   Tipo de storage.
    *   Estratégia de ingestão.

### Tecnologias Utilizadas
*   **Linguagem:** Python 3.12
*   **Framework Web:** FastAPI
*   **Gerenciamento de dependências:** Poetry
*   **Scraping:** httpx + BeautifulSoup
*   **Persistência:** S3 compatível (MinIO / AWS S3)
*   **Containerização:** Docker + Docker Compose
*   **Qualidade de Código:** Ruff, Black
*   **Testes:** Pytest (unitários, integração e mocks)

### Estrutura de Diretórios

```text
ingestion_service/
├── app/
│   ├── api/            # Endpoints FastAPI
│   ├── core/           # Configurações, logging e bootstrap
│   ├── domain/         # Modelos e contratos (Protocols)
│   ├── repositories/   # Persistência (S3)
│   ├── scrapers/       # Scraper do arXiv
│   ├── services/       # Orquestração da ingestão
│   └── main.py
├── tests/              # Testes automatizados
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### Funcionamento da Ingestão (Camada Bronze)
1.  O endpoint `/ingest` é acionado via API.
2.  O Scraper coleta artigos do arXiv via HTML.
3.  Cada artigo é convertido para o modelo de domínio.
4.  Os dados são persistidos **sem qualquer transformação**.
5.  Cada registro contém metadados de ingestão:
    *   Timestamp
    *   Fonte
    *   Query utilizada
6.  A Camada Bronze preserva os dados exatamente como coletados, garantindo:
    *   Rastreabilidade
    *   Reprocessamento futuro
    *   Auditoria de origem

### Testes Automatizados
O projeto possui uma suíte completa de testes, cobrindo:
*   Testes de domínio (modelos).
*   Testes de scraper com HTML mockado.
*   Testes de repositório com boto3 mockado.
*   Testes de infraestrutura (bootstrap de bucket).
*   Testes de fluxo de ingestão:
    *   Happy path.
    *   Falhas e exceções.

### Benefícios
*   Confiabilidade do sistema.
*   Evolução segura.
*   Facilidade de refatoração.
*   Redução de regressões.

---

## Execução Local

### Subir o ambiente completo (API + MinIO)
```bash
make run
```

### Acessos
*   **API / Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
*   **Console MinIO:** [http://localhost:9001](http://localhost:9001)
    *   **Usuário:** `minioadmin`
    *   **Senha:** `minioadmin`

---

## Evolução Planejada

Este microserviço é a base de um ecossistema de dados orientado a microserviços, incluindo:
*   Pipeline Silver (limpeza e geração de embeddings).
*   Indexação vetorial.
*   Busca semântica.
*   Frontend de consulta.
*   Orquestração por eventos.

**A arquitetura atual não exige retrabalho para essas evoluções — apenas extensão.**

---

## Status do Projeto
*   **Fase 1 — Ingestion / Bronze:** Concluída
*   **Arquitetura:** Microserviços
*   **Maturidade:** Base pronta para produção
