# O projeto segue uma arquitetura de microserviços evolutiva, onde cada fase corresponde a um microserviço independente.

## Status da Arquitetura:

- ✔ Fase 1 – Ingestion Service: IMPLEMENTADO
- ✔ Fase 2 – Processing Service: IMPLEMENTADO
- ✔ Fase 3 – Frontend Service: IMPLEMENTADO
- ⏳ Fase 4 – AWS: PLANEJADO


# Frontend Service (Busca Semântica & Visualização)

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat&logo=minio&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=flat&logo=poetry&logoColor=white)
![Bump2Version](https://img.shields.io/badge/bump2version-semantic-ff69b4?style=flat)

Microserviço responsável pela **Interface de Usuário (UI)**, permitindo a busca semântica nos artigos processados utilizando Embeddings e filtros interativos.

## 📋 Visão Geral

Este projeto compõe a **Fase 3** da arquitetura.
Ele consome os dados da camada **Silver** (MinIO), carrega os vetores em memória e oferece uma interface amigável via **Streamlit** para que pesquisadores possam encontrar artigos relevantes através de linguagem natural.

### ✨ Funcionalidades Principais
*   **Busca Semântica (Vector Search)**: Encontra artigos pelo sentido da frase, não apenas por palavras-chave exatas (usando BERT + Cosine Similarity).
*   **Interface Interativa**: Slider para definir quantidade de resultados (`top_k`), visualização de score de relevância e expansão de detalhes.
*   **Integração com MinIO**: Carrega automaticamente os dados processados da camada Silver.
*   **Performance**: Utiliza cache (`@st.cache_resource`) para evitar recarregar modelos pesados a cada interação.

### 📸 Screenshot
![Demo da Busca Semântica](../docs/img/semantic_search_demo.jpg)

### Tecnologias
*   **Python 3.12**
*   **Streamlit** (Framework de UI)
*   **pandas** (Manipulação de Dados)
*   **scikit-learn** (Cálculo de Similaridade)
*   **Transformers (HuggingFace)** (Modelo de Embedding)
*   **Docker & Docker Compose**

## 🚀 Como Executar

### 📝 Documentação
* Instruções detalhadas de implementação: `docs/passo_a_passo_fase_3.md`.

### Pré-requisitos
*   Docker instalado.
*   Rede compartilhada criada (`docker network create arxiv-shared`).
*   Camada Silver populada (Fase 2 executada previamente).

### Passos Rápidos (Docker)
1.  **Importante**: Crie a rede compartilhada (caso não exista):
    ```bash
    docker network create arxiv-shared || true
    ```
2.  Suba a aplicação:
    ```bash
    make run
    # ou: docker compose up --build -d
    ```
3.  Acesse no navegador:
    *   [http://localhost:8501](http://localhost:8501)

## 🛠️ Desenvolvimento Local

### Instalação
```bash
poetry install
poetry run pre-commit install
```

### Rodando sem Docker
Para desenvolvimento rápido (Hot-reload):
```bash
make run-local
# ou: poetry run streamlit run app/main.py
```

### Testes
Executa testes unitários (mockando S3 e Modelos):
```bash
make test
```

## 📂 Estrutura
*   `app/`: Código da aplicação Streamlit.
    *   `services/`: Lógica de busca (`SearchEngine`).
    *   `core/`: Configurações.
*   `tests/`: Testes automatizados.
*   `Dockerfile`: Configuração da imagem.

## 📝 Autor
*   **Saulo Santos**
    *   [GitHub](https://github.com/Prof-Saulo-Santos)
    *   [LinkedIn](https://www.linkedin.com/in/santossaulo/)
