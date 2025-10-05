# This file defines the secure "lockboxes" in AWS Secrets Manager where our
# application's sensitive environment variables will be stored.

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.project_name}-${var.environment}-db-password"
  tags = {
    Name        = "${var.project_name}-${var.environment}-db-password"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_secret_key" {
  name = "${var.project_name}-${var.environment}-app-secret-key"
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-secret-key"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_algorithm" {
  name = "${var.project_name}-${var.environment}-app-algorithm"
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-algorithm"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_token_expire" {
  name = "${var.project_name}-${var.environment}-app-token-expire"
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-token-expire"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_google_api_key" {
  name = "${var.project_name}-${var.environment}-app-google-api-key"
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-google-api-key"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
