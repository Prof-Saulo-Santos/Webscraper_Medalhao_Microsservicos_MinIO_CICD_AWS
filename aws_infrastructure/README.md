# AWS Infrastructure (IaC)

![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=flat&logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)

Este diretório contém os scripts de **Infraestrutura como Código (IaC)** para provisionar o ambiente de produção na Amazon Web Services.

## 📋 Visão Geral

Substitui a infraestrutura local (Docker Compose) por serviços gerenciados de alta disponibilidade:

*   **Networking:** VPC, Subnets Públicas/Privadas, NAT Gateway.
*   **Storage:** S3 (para Camadas Bronze/Silver).
*   **Compute:** ECS Fargate (Serverless Containers) para rodar Ingestion, Processing e Frontend.
*   **Registry:** ECR (Elastic Container Registry).

## 🚀 Como Executar

### 📝 Documentação
* Leia o guia completo (incluindo **FinOps e Monitoramento**): `../docs/passo_a_passo_fase_4.md`.

### Pré-requisitos
*   [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) instalado (v1.5+).
*   [AWS CLI](https://aws.amazon.com/cli/) instalado e configurado (`aws configure`).

### Comandos Básicos

1.  **Inicializar:** Baixa os providers necessários.
    ```bash
    terraform init
    ```

2.  **Planejar:** Mostra o que será criado (dry-run).
    ```bash
    terraform plan
    ```

3.  **Aplicar:** Cria a infraestrutura real (Custo envolvido!).
    ```bash
    terraform apply
    ```

4.  **Destruir:** Remove tudo (para evitar cobranças).
    ```bash
    terraform destroy
    ```

## 📂 Estrutura

*   `main.tf`: Definição principal dos recursos.
*   `variables.tf`: Variáveis configuráveis (nomes, regiões).
*   `outputs.tf`: Dados de saída (URLs, IDs).
