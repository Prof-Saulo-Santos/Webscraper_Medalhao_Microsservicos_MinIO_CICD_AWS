# 1. Execution Role (Padrão ECS)
resource "aws_iam_role" "ecs_execution" {
  name = "arxiv-ecs-execution-${var.environment}"

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

# 2. Task Role - Ingestion (S3 Bronze Access)
resource "aws_iam_role" "ingestion_task" {
  name = "arxiv-ingestion-task-${var.environment}"

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
  name = "arxiv-ingestion-s3-policy-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
        Resource = [
            aws_s3_bucket.bronze.arn,
            "${aws_s3_bucket.bronze.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ingestion_attach" {
  role       = aws_iam_role.ingestion_task.name
  policy_arn = aws_iam_policy.ingestion_s3_policy.arn
}

# 3. Role para EventBridge invocar ECS
resource "aws_iam_role" "eventbridge_role" {
  name = "arxiv-eventbridge-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "eventbridge_invoke_ecs" {
  name = "arxiv-eventbridge-invoke-ecs-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ecs:RunTask"]
        Resource = [aws_ecs_task_definition.ingestion.arn]
      },
      {
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = [aws_iam_role.ecs_execution.arn, aws_iam_role.ingestion_task.arn]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_attach" {
  role       = aws_iam_role.eventbridge_role.name
  policy_arn = aws_iam_policy.eventbridge_invoke_ecs.arn
}
