resource "aws_scheduler_schedule" "ingestion_daily" {
  name = "arxiv-ingestion-daily-${var.environment}"
  
  # Cronograma: Seg-Sex 14h-17h BRT (+3h UTC) = 17h-20h UTC
  # Nota: RunTask dispara uma task. Para rodar das 14 as 17, precisaria ser um Service com scale-out/in
  # Como definimos Ingestion como BATCH (roda e morre), vamos agendar para disparar AS 14h (UTC 17h)
  
  schedule_expression = "cron(0 17 ? * MON-FRI *)"
  
  target {
    arn      = aws_ecs_cluster.main.arn
    role_arn = aws_iam_role.eventbridge_role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.ingestion.arn
      launch_type         = "FARGATE"

      network_configuration {
        # Como nao temos subnets criadas neste exemplo simplificado, 
        # vamos assumir variáveis (o usuario deve criar vpc.tf ou usar default)
        # Para simplificar o example, deixaremos comentado partes dependentes de VPC
        assign_public_ip = true
        subnets          = ["subnet-12345678"] # Placeholder - requer modulo de VPC
        security_groups  = []
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
