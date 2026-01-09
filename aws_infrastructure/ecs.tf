resource "aws_ecs_cluster" "main" {
  name = "arxiv-cluster-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "ingestion" {
  family                   = "arxiv-ingestion-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ingestion_task.arn

  container_definitions = jsonencode([
    {
      name      = "ingestion"
      image     = "${aws_ecr_repository.ingestion.repository_url}:latest"
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/arxiv-ingestion"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
          awslogs-create-group  = "true"
        }
      }
    }
  ])
}
