# This file defines the Identity and Access Management (IAM) roles that are
# shared across all environments.

# ------------------------------------------------------------------------------
# ECS Task Execution Role (The "Setup Crew" ID)
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
    Name      = "${var.project_name}-ecs-task-execution-role"
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

# Attach the standard AWS-managed policy for ECS task execution.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ------------------------------------------------------------------------------
# ECS Task Role (The "Application's" ID)
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
    Name      = "${var.project_name}-ecs-task-role"
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

# ------------------------------------------------------------------------------
# EC2 Instance Role (The "Server's" ID)
# ------------------------------------------------------------------------------
resource "aws_iam_role" "ecs_instance_role" {
  name               = "${var.project_name}-ecs-instance-role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name      = "${var.project_name}-ecs-instance-role"
    Project   = var.project_name
    ManagedBy = "Terraform"
  }
}

# Attach the standard policy that allows an EC2 instance to be part of an ECS cluster.
resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# The Instance Profile is the "uniform" that attaches the role to the EC2 instance.
resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "${var.project_name}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

