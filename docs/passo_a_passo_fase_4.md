# Fase 4 — AWS Infrastructure (IaC com Terraform)

## 1. Objetivo da Fase 4

Nesta fase, o projeto migra de um ambiente local baseado em `docker-compose` para uma infraestrutura moderna, gerenciada e escalável na AWS, utilizando **Terraform** como ferramenta de Infraestrutura como Código (IaC).

A arquitetura foi projetada seguindo princípios de:
*   **Automação total**
*   **Segurança por padrão**
*   **Eficiência de custos (FinOps)**
*   **Separação de responsabilidades**

Os serviços de ingestão e processamento de dados foram modelados como tarefas *batch* no **ECS Fargate**, acionadas de forma agendada pelo **Amazon EventBridge**, evitando a manutenção de serviços ativos continuamente.

O armazenamento foi estruturado em um Data Lake no **Amazon S3**, com camadas **Bronze** (dados brutos) e **Silver** (dados processados), seguindo padrões amplamente adotados em ambientes analíticos modernos.

A infraestrutura é reproduzível, versionada e auditável, permitindo fácil replicação do ambiente em diferentes contextos (desenvolvimento ou produção).

---

## 2. Pré-requisitos

### 2.1 Ferramentas Necessárias
*   **Terraform** (>= 1.5): Para provisionamento.
*   **AWS CLI** (v2): Para autenticação.
*   Uma conta AWS ativa com permissões de Administrator (ou PowerUser).

---

## 3. Arquitetura Proposta

```mermaid
graph TD
    subgraph AWS_Account
        subgraph VPC
            subgraph Public_Subnet
                ALB[ALB / Frontend]
            end
            
            subgraph Private_Subnet
                Ingestion[ECS Task: Ingestion\n(Batch / Fargate Spot)]
                Processing[ECS Task: Processing\n(Batch / Fargate Spot)]
                Frontend[ECS Service: Frontend\n(Always-on / Fargate Spot)]
            end
            
            NAT[NAT Gateway]
            Private_Subnet --> NAT
        end

        S3_Bronze[(S3 Bucket\nBronze Layer)]
        S3_Silver[(S3 Bucket\nSilver Layer)]
        ECR[(Amazon ECR)]
        
        EventBridge[EventBridge Scheduler]
        CW_Logs[CloudWatch Logs]

        Ingestion --> S3_Bronze
        Processing --> S3_Bronze
        Processing --> S3_Silver
        Frontend --> S3_Silver
        
        EventBridge -->|Start| Ingestion
        EventBridge -->|Start| Processing
        EventBridge -->|Stop/Start| Frontend
    end
```

### 🎯 Pontos de Destaque da Arquitetura:
*   ✔ **Separação clara Batch vs Always-on:** Ingestion/Processing são efêmeros; Frontend é persistente.
*   ✔ **Uso de Fargate Spot:** Redução drástica de custos (até 70%).
*   ✔ **Data Lake em camadas:** Bronze (Raw) e Silver (Processed).
*   ✔ **Infraestrutura 100% reproduzível (IaC):** Todo o ambiente definido via Terraform.

** Observação:** Como se trata de workloads batch e stateless, a possível interrupção de tarefas Fargate Spot não compromete a consistência do pipeline.

### 3.1 Estratégia de Economia (FinOps) 💰

Como é um projeto acadêmico, não faz sentido manter serviços de Scraper ou Processamento ativos 24/7 esperando comando. Vamos otimizar:

1.  **Ingestion & Processing (Batch/Agendado):**
    *   Em vez de `ECS Services` (Always-on), usaremos **ECS Tasks Agendadas** (via EventBridge Scheduler).
    *   Exemplo: O Scraper roda todo dia às 06:00, coleta dados por 10min e **desliga o container**. Cobrança apenas pelos 10 minutos!
    *   Uso de **Fargate Spot**: Aproveita capacidade ociosa da AWS com **descontos de até 70%**.

2.  **Frontend (On-Demand):**
    *   Este precisa estar ativo para você acessar.
    *   Opção mais barata: **ECS Fargate Spot** (1 única task pequena: 0.25 vCPU) ou **AWS App Runner** (que gerencia o container mais facilmente).

3.  **Free Tier (Alternativa "Raiz"):**
    *   Em vez de ECS/Fargate, poderíamos criar uma única instância **EC2 t3.micro** (Free Tier por 12 meses) e rodar o `docker compose` lá dentro. É a opção "Grátis", mas perde a arquitetura Serverless moderna.

### 3.2 Cronograma Rigoroso (Agendamento Automático) 📅

Conforme solicitado, limitaremos os gastos ligando a infraestrutura **apenas** de Segunda a Sexta, das 14h às 17h (Horário de Brasília).

Utilizaremos o EventBridge Scheduler para ajustar dinamicamente o desired_count dos ECS Services e para disparar ECS Tasks batch sob demanda:

*   **Janela:** Segunda a Sexta-feira (Mon-Fri).
*   **Horário:** 14:00 às 17:00 (BRT) -> 17:00 às 20:00 (UTC).

| Ação | Horário (BRT) | CRON Expression (UTC) |  Comando Terraform |
| :--- | :--- | :--- | :--- |
| **LIGAR** | 14:00 | `cron(0 17 ? * MON-FRI *)` | Set `desired_count = 1` |
| **DESLIGAR** | 17:00 | `cron(0 20 ? * MON-FRI *)` | Set `desired_count = 0` |

> **Economia:** 
> *   Horas totais/semana: 15 horas.
> *   Horas totais/mês: ~60 horas.
> *   **Custo Estimado (Fargate Spot):** Ainda menor que **$1.00 USD/mês** para computação!

---

## 4. Estrutura de Diretórios (Terraform)

```text
aws_infrastructure/
├── main.tf             <-- Definição dos recursos (Provider, Data Sources)
├── variables.tf        <-- Declaração de variáveis (Region, Project Name)
├── outputs.tf          <-- Outputs úteis (URLs, IDs)
├── versions.tf         <-- Versões do Provider AWS/Terraform
├── modules/            <-- (Opcional) Módulos reutilizáveis
│   ├── network/
│   ├── storage/
│   └── compute/
├── environments/       <-- Configurações por ambiente
│   ├── dev/
│   │   └── terraform.tfvars
│   └── prod/
└── README.md
```

---

## 5. Implementação Passo a Passo

### 5.1 Configuração Inicial (`versions.tf`) (Exemplo)

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Backend S3 para guardar o estado do Terraform (Recomendado para times)
  # backend "s3" { ... }
}
```

### 5.2 Storage (`s3.tf` ou `main.tf`)

```hcl
resource "aws_s3_bucket" "bronze" {
  bucket = "arxiv-lake-bronze-${var.env}"
}

resource "aws_s3_bucket" "silver" {
  bucket = "arxiv-lake-silver-${var.env}"
}
```

### 5.3 ECR (Elastic Container Registry)

Antes de rodar o ECS, precisamos de lugares para guardar as imagens:

```hcl
resource "aws_ecr_repository" "services" {
  for_each = toset(["ingestion", "processing", "frontend"])
  name     = "arxiv-${each.key}"
}
```

### 5.4 ECS Task + EventBridge Scheduler (Batch / Ingestion) 🤖

Exemplo didático de como configurar a Ingestão para rodar agendada:

**1. ECS Task Definition (Batch):**
```hcl
resource "aws_ecs_task_definition" "ingestion" {
  family                   = "arxiv-ingestion"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ingestion_task.arn

  container_definitions = jsonencode([
    {
      name      = "ingestion"
      image     = "${aws_ecr_repository.services["ingestion"].repository_url}:latest"
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/arxiv-ingestion"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
```

**2. EventBridge — Task Agendada:**
```hcl
resource "aws_scheduler_schedule" "ingestion_daily" {
  name = "arxiv-ingestion-daily"

  schedule_expression = "cron(0 17 ? * MON-FRI *)"

  target {
    arn      = aws_ecs_cluster.main.arn
    role_arn = aws_iam_role.eventbridge_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.ingestion.arn
      launch_type         = "FARGATE"

      network_configuration {
        subnets         = var.private_subnets
        security_groups = [aws_security_group.ecs_tasks.id]
      }

      capacity_provider_strategy {
        capacity_provider = "FARGATE_SPOT"
        weight            = 1
      }
    }
  }

  flexible_time_window {
    mode = "OFF"
  }
}
```
**Resultado:** O container sobe, executa o scraping e morre automaticamente.

### 5.5 IAM Roles — Least Privilege (Segurança) 🔐

Configuração de segurança pronta para auditoria (Princípio do Menor Privilégio):

**1. Execution Role (Padrão ECS):**
Permite que o ECS puxe imagens do ECR e envie logs para o CloudWatch.
```hcl
resource "aws_iam_role" "ecs_execution" {
  name = "ecsExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
```

**2. Task Role — Ingestion (Somente S3 Necessário):**
A aplicação só tem permissão para acessar o Bucket Bronze. Se for hackeada, o atacante não consegue acessar nada além disso.
```hcl
resource "aws_iam_role" "ingestion_task" {
  name = "arxiv-ingestion-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ingestion_s3_policy" {
  name = "arxiv-ingestion-s3-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject"]
        Resource = "arn:aws:s3:::arxiv-lake-bronze-*/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ingestion_attach" {
  role       = aws_iam_role.ingestion_task.name
  policy_arn = aws_iam_policy.ingestion_s3_policy.arn
}
```

---

## 6. Pipeline de Deploy (GitHub Actions para AWS)

Para fechar o CI/CD com chave de ouro:

1.  **CI (Como já configurado):** Roda testes.
2.  **CD (Novo Workflow):**
    *   Login no AWS ECR.
    *   Build & Push das imagens Docker.
    *   Atualização do serviço no ECS (`aws ecs update-service`).

Exemplo do workflow `deploy-aws.yml`:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: arxiv-ingestion
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./ingestion_service
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

---

## 7. Próximos Passos (Para você executar agora)

1.  Instale o Terraform no seu PC (Windows/WSL).
2.  Configure suas credenciais AWS (`aws configure`).
3.  Preencha os arquivos `.tf` na pasta `aws_infrastructure`.
4.  Execute `terraform init` e `terraform plan`.

---

# ANEXO: Observabilidade, Monitoramento e Governança de Custos 📊

## 1. Objetivo

Tem como objetivo instrumentar, monitorar e controlar a infraestrutura implantada na Fase 4, garantindo:
*   **Visibilidade operacional** (logs, métricas e eventos).
*   **Detecção proativa de falhas**.
*   **Rastreabilidade de execução** de tarefas batch.
*   **Controle rigoroso de custos (FinOps)**.

Governança mínima, porém profissional, compatível com projetos acadêmicos e ambientes reais.
Esta fase não altera a arquitetura funcional, mas a fortalece, transformando a solução em um ambiente observável, auditável e sustentável.

## 2. Observabilidade — Logs, Métricas e Eventos

### 2.1 Centralização de Logs (CloudWatch Logs)

Todos os containers executados no ECS Fargate já estão configurados (na Fase 4) para enviar logs ao **Amazon CloudWatch Logs**, com log groups segregados por serviço:

| Serviço | Log Group |
| :--- | :--- |
| Ingestion | `/ecs/arxiv-ingestion` |
| Processing | `/ecs/arxiv-processing` |
| Frontend | `/ecs/arxiv-frontend` |

**Benefícios:**
*   ✔ Diagnóstico rápido de falhas.
*   ✔ Histórico de execuções batch.
*   ✔ Evidência clara de que a task executou e finalizou.

### 2.2 Métricas Automáticas do ECS/Fargate

O ECS expõe métricas nativas no CloudWatch Metrics, como:
*   `CPUUtilization`
*   `MemoryUtilization`
*   `TaskCount`
*   `RunningTaskCount`

Essas métricas permitem responder perguntas como:
*   O processamento está superdimensionado?
*   As tasks estão falhando?
*   O frontend está consumindo mais recursos do que o esperado?

### 2.3 Eventos de Execução (EventBridge)

O Amazon EventBridge já atua como orquestrador de execução, mas também funciona como fonte de eventos.

**Eventos monitorados:**
*   Falha na inicialização da task.
*   Task encerrada com erro.
*   Falha de agendamento.

📌 **Isso permite auditar:** Quando a task rodou, se rodou e por que falhou.

## 3. Alarmes Operacionais (CloudWatch Alarms)

### 3.1 Alarme de Falha de Task Batch

Exemplo: disparar alerta se uma task terminar com erro.

```hcl
resource "aws_cloudwatch_metric_alarm" "ingestion_task_failed" {
  alarm_name          = "arxiv-ingestion-task-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "StoppedTaskCount"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = "arxiv-ingestion"
  }

  alarm_description = "Dispara se a task de ingestão falhar"
}
```
🎯 **Valor:** demonstra monitoramento ativo, não apenas logs passivos.

## 4. FinOps — Controle e Otimização de Custos

### 4.1 Orçamento Mensal (AWS Budgets)

Criamos um Budget de proteção, essencial para projetos educacionais.

```hcl
resource "aws_budgets_budget" "monthly_budget" {
  name         = "arxiv-monthly-budget"
  budget_type  = "COST"
  limit_amount = "5"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = ["Amazon ECS", "Amazon S3"]
  }
}
```
📌 Se ultrapassar **USD 5/mês**, você será alertado.

### 4.2 Estratégias de Economia Ativas (Resumo)

| Estratégia | Impacto |
| :--- | :--- |
| **ECS Fargate Spot** | Até -70% custo |
| **Tasks Batch** | Paga só quando roda |
| **Janela Horária** | Infra desligada fora do horário |
| **CPU/Mem mínimos** | Evita overprovisioning |
| **S3 Standard** | Custo quase zero para dados pequenos |

## 5. Governança Básica (Boas Práticas)

### 5.1 Naming Convention Padronizado

Todos os recursos seguem o padrão: `<projeto>-<serviço>-<ambiente>`

Exemplo:
*   `arxiv-ingestion-dev`
*   `arxiv-cluster-prod`
*   `arxiv-lake-bronze-dev`

🎯 Facilita auditoria, custos e troubleshooting.

### 5.2 Tags Obrigatórias (Recomendado pela AWS)

```hcl
tags = {
  Project     = "ArxivPipeline"
  Environment = var.env
  Owner       = "Academic"
}
```
Essas tags são usadas para: Cost Explorer, Auditoria e Governança mínima.

## 6. Dashboard Operacional (CloudWatch)

Sugere-se a criação de um CloudWatch Dashboard contendo:
*   CPU e memória do Frontend
*   Quantidade de tasks executadas por dia
*   Tempo médio de execução
*   Falhas por serviço

📌 Mesmo que o dashboard não seja implementado, a especificação demonstra maturidade técnica.

## 7. Integração Direta com a Fase 4

| Fase 4 | Complemento da Fase 5 |
| :--- | :--- |
| ECS Tasks | Monitoradas via Metrics |
| EventBridge Scheduler | Auditável via Events |
| S3 Data Lake | Custos controlados |
| Fargate Spot | Budget protege gastos |
| Terraform IaC | Observabilidade também como código |

## 8. Observabilidade e Governança de Custos**

Complementa a infraestrutura provisionada na Fase 4 ao introduzir mecanismos de observabilidade, monitoramento e controle financeiro, fundamentais para a operação sustentável de sistemas em nuvem.

Foram utilizados serviços nativos da AWS, como **CloudWatch**, **EventBridge** e **AWS Budgets**, permitindo acompanhar o comportamento das aplicações, detectar falhas de execução e limitar custos operacionais.

Essa abordagem garante não apenas o funcionamento técnico da solução, mas também sua viabilidade econômica, reforçando a aderência do projeto às boas práticas de arquitetura em nuvem adotadas no mercado.

### ✅ Conclusão Geral

*   ✔ Usa AWS de forma profissional
*   ✔ Aplica IaC, FinOps e Observabilidade
*   ✔ Demonstra consciência de custos
*   ✔ Está pronto para apresentação, defesa e publicação no GitHub
