# Exemplo inicial: Criação dos repositórios ECR para guardar as imagens Docker

resource "aws_ecr_repository" "ingestion" {
  name                 = "${var.project_name}-ingestion-${var.environment}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Cuidado em produção!

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "processing" {
  name                 = "${var.project_name}-processing-${var.environment}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "${var.project_name}-frontend-${var.environment}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}
