# This file defines the secure "lockboxes" in AWS Secrets Manager for the
# application's sensitive environment variables.

resource "aws_secretsmanager_secret" "app_secret_key" {
  name = "${var.project_name}-${var.environment}-app-secret-key"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_algorithm" {
  name = "${var.project_name}-${var.environment}-app-algorithm"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_token_expire" {
  name = "${var.project_name}-${var.environment}-app-token-expire"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret" "app_google_api_key" {
  name = "${var.project_name}-${var.environment}-app-google-api-key"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

