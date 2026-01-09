# O projeto segue uma arquitetura de microserviços evolutiva, onde cada fase corresponde a um microserviço independente.

## Status da Arquitetura:

- ✔ Fase 1 – Ingestion Service: IMPLEMENTADO
- ✔ Fase 2 – Processing Service: IMPLEMENTADO
- ⏳ Fase 3 – Frontend Service: PLANEJADO
- ⏳ Fase 4 – AWS: PLANEJADO


# Processing Service (Camada Silver)

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat&logo=minio&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=flat&logo=PyTorch&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=flat&logo=poetry&logoColor=white)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Bump2Version](https://img.shields.io/badge/bump2version-semantic-ff69b4?style=flat)

Microserviço responsável pelo tratamento, limpeza e enriquecimento vetorial (Embeddings) dos artigos coletados na Fase 1. Persiste os dados na camada Silver.

## 📋 Visão Geral

Este projeto compõe a **Fase 2** da arquitetura de microserviços.
Ele lê os arquivos JSON brutos da camada **Bronze** (MinIO), aplica normalização textual e gera vetores semânticos (embeddings) utilizando modelos Transformers (BERT), salvando o resultado estruturado na camada **Silver**.

### ✨ Funcionalidades Principais
*   **Limpeza Textual (NLP)**: Pipeline robusto com Regex para remover caracteres especiais e stopwords científicas, mantendo a integridade semântica.
*   **Geração de Embeddings**: Utiliza o modelo `sentence-transformers/all-MiniLM-L6-v2` (otimizado para CPU) para converter resumos em vetores de 384 dimensões.
*   **Integração com MinIO**: Sistema automático de leitura (Bucket Bronze) e escrita (Bucket Silver) com verificação de idempotência (não reprocessa o que já existe).
*   **Arquitetura Híbrida**: Funciona como API (FastAPI) para gatilhos ou como Worker para processamento em lote.
*   **Otimização para CPU**: Configurado especificamente para rodar PyTorch em ambientes sem GPU (menor tamanho de imagem Docker).

### Tecnologias
*   **Python 3.12**
*   **FastAPI** (API REST / Entrypoint)
*   **PyTorch & Transformers** (Machine Learning)
*   **Poetry** (Gerenciamento de Dependências)
*   **Docker & Docker Compose** (Containerização Otimizada)
*   **MinIO** (Object Storage)

## 🚀 Como Executar

### 📝 Documentação
* Você pode encontrar a documentação completa do projeto no arquivo `docs/passo_a_passo_fase_2.md`.

### Pré-requisitos
*   Docker e Docker Compose instalados.
*   (Opcional) Fase 1 rodando ou dados pré-existentes no volume `ingestion_service_minio_data`.

### Passos Rápidos (Docker)
1.  Suba os containers:
    ```bash
    make run
    # ou: docker compose up --build -d
    ```
2.  Acesse a documentação da API:
    *   [http://localhost:8001/docs](http://localhost:8001/docs)
3.  **Exemplo de Uso (Processamento)**:
    *   Endpoint: `POST /process_batch`
    *   Parâmetros:
        *   `limit`: Quantidade de arquivos a processar (ex: 10).
    *   *O serviço buscará arquivos no Bronze, processará e salvará no Silver.*
4.  Acesse o Console do MinIO:
    *   [http://localhost:9001](http://localhost:9001) (Porta console mapeada)
    *   Credenciais: `minioadmin` / `minioadmin`

## 🛠️ Desenvolvimento Local

### Instalação
```bash
poetry install
poetry run pre-commit install
```

### Testes
Para rodar a suíte de testes automatizados (inclui mocks do S3 via `moto`):
```bash
make test
# ou: poetry run pytest tests/ -v
```

### Versionamento
Para subir a versão (patch, minor, major):
```bash
poetry run bump2version minor --verbose
```

## 📂 Estrutura (DDD Simplificado)
*   `app/domain`: Modelos e Protocolos (Interfaces).
*   `app/infrastructure`: Implementações Concretas (S3 Repository, Regex Cleaner, BERT Embedder).
*   `app/services`: Regras de Negócio e Orquestração.
*   `app/api`: Rotas FastAPI.
*   `tests/`: Testes unitários e de integração.

## 📝 Autor
*   **Saulo Santos**
    *   [GitHub](https://github.com/Prof-Saulo-Santos)
    *   [LinkedIn](https://www.linkedin.com/in/santossaulo/)
