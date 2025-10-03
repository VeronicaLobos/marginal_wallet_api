# This file defines the Identity and Access Management (IAM) roles that AWS
# services will use to operate and interact with each other securely.

# ------------------------------------------------------------------------------
# ECS Task Execution Role
# ------------------------------------------------------------------------------
# This role is assumed by the ECS agent to perform essential actions on your
# behalf, such as pulling the Docker image from ECR and sending logs to
# CloudWatch.
# ------------------------------------------------------------------------------
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.project_name}-ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
    ManagedBy = "Terraform"
  }
}

# Attach the standard AWS-managed policy for ECS task execution.
# This policy includes all the necessary permissions for ECR and CloudWatch.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ------------------------------------------------------------------------------
# ECS Task Role
# ------------------------------------------------------------------------------
# This role is assumed by the application running inside the container.
# You would add policies here if your FastAPI code needed to access other AWS
# services, such as reading/writing to an S3 bucket for user avatars.
# For now, it's a placeholder for future use.
# ------------------------------------------------------------------------------
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.project_name}-ecs-task-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
    ManagedBy = "Terraform"
  }
}
