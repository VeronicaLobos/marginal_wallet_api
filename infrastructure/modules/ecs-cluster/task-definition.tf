# This file defines the "job description" for the application container.

resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "awsvpc" # Required for ECS on EC2 with ALB
  requires_compatibilities = ["EC2"]
  cpu                      = "256"  # 1/4 of a vCPU
  memory                   = "512"  # 512 MB
  execution_role_arn       = var.ecs_task_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-${var.environment}-container",
      image     = var.ecr_repository_url,
      essential = true,
      portMappings = [
        {
          containerPort = 8080, # The port your application listens on
          hostPort      = 8080
        }
      ],
      # This is the most important part for security.
      # Instead of defining environment variables directly, we tell the ECS agent
      # to fetch them from AWS Secrets Manager at runtime.
      secrets = [
        {
          name      = "DATABASE_URL",
          valueFrom = var.db_url_secret_arn
        },
        {
          name      = "SECRET_KEY",
          valueFrom = var.app_secret_key_arn
        },
        {
          name      = "ALGORITHM",
          valueFrom = var.app_algorithm_arn
        },
        {
          name      = "ACCESS_TOKEN_EXPIRE_MINUTES",
          valueFrom = var.app_token_expire_arn
        },
        {
          name      = "GOOGLE_API_KEY",
          valueFrom = var.app_google_api_key_arn
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}-${var.environment}-task",
          "awslogs-region"        = var.aws_region,
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-${var.environment}-task-def"
  }
}

