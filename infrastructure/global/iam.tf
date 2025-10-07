# This file defines the Identity and Access Management (IAM) roles.

# --- ECS Task Execution Role (The "Setup Crew") ---
# This role allows the ECS agent to pull images and send logs.
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "marginal-wallet-ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
  tags = { Project = var.project_name }
}

# Attach the standard AWS-managed policy for ECS task execution.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# --- ECS Task Role (The "Application's" ID) ---
# This role is used by the application code inside the container.
resource "aws_iam_role" "ecs_task_role" {
  name               = "marginal-wallet-ecs-task-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
  tags = { Project = var.project_name }
}

# --- Secrets Read Policy ---
# This custom policy allows reading all secrets for this project.
resource "aws_iam_policy" "secrets_read_policy" {
  name        = "${var.project_name}-${var.environment}-secrets-read-policy"
  description = "Allows reading all application secrets from Secrets Manager"
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = "secretsmanager:GetSecretValue",
        Effect   = "Allow",
        Resource = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}-${var.environment}-*"
      }
    ]
  })
}

# --- Policy Attachments ---
# Attach the secrets read policy to the application's Task Role.
resource "aws_iam_role_policy_attachment" "ecs_task_role_secrets_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.secrets_read_policy.arn
}

# --- THIS IS THE FIX ---
# Attach the SAME secrets read policy to the Task Execution Role.
# This allows the ECS agent to fetch the secrets to start the container.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_secrets_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.secrets_read_policy.arn
}

# --- EC2 Instance Role (The "Server's" ID) ---
resource "aws_iam_role" "ecs_instance_role" {
  name               = "marginal-wallet-ecs-instance-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "ec2.amazonaws.com" }
      }
    ]
  })
  tags = { Project = var.project_name }
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "marginal-wallet-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

