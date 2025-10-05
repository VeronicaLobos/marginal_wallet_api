# This file defines the "job description" for a single instance of our
# application container. It specifies the Docker image, resources, ports,
# environment variables, and IAM roles.

resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "awsvpc" # Required for ECS on EC2 with ALB
  requires_compatibilities = ["EC2"]
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 512 MB

  # These are the IAM roles (the "ID cards") the task will use.
  task_role_arn            = var.ecs_task_role_arn            # For the application code
  execution_role_arn       = var.ecs_task_execution_role_arn  # For the ECS agent (setup crew)

  # This is the core of the task definition: the container itself.
  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-${var.environment}-container",
      image     = var.ecr_repository_url, # The Docker image to run
      essential = true,

      # Map the container's port (8080) so the load balancer can find it.
      portMappings = [
        {
          containerPort = 8080,
          hostPort      = 8080,
          protocol      = "tcp"
        }
      ],

      # This is the secure way to handle environment variables.
      # Instead of passing the values directly, we pass the ARNs of the secrets
      # stored in AWS Secrets Manager. The ECS agent, using the execution role,
      # will fetch these secrets and inject them as environment variables
      # just before the container starts.
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

      # Configure logging to send container output to AWS CloudWatch.
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
    Name    = "${var.project_name}-${var.environment}-task-def"
    Project = var.project_name
  }
}

