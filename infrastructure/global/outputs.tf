# This file exports the identifiers (ARNs) of the shared resources created
# in the global module, so they can be used by environment-specific modules.

# --- IAM Role Outputs ---

output "ecs_task_execution_role_arn" {
  description = "The ARN of the IAM role that allows ECS to manage resources."
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "The ARN of the IAM role for the application running in the task."
  value       = aws_iam_role.ecs_task_role.arn
}

output "ecs_instance_profile_name" {
  description = "The name of the IAM instance profile for the EC2 instances."
  value       = aws_iam_instance_profile.ecs_instance_profile.name
}

# --- Secrets Manager Outputs ---

output "db_password_secret_arn" {
  description = "The ARN of the secret for the RDS database password."
  value       = aws_secretsmanager_secret.db_password.arn
}

output "app_secret_key_arn" {
  description = "The ARN of the secret for the application's SECRET_KEY."
  value       = aws_secretsmanager_secret.app_secret_key.arn
}

output "app_algorithm_arn" {
  description = "The ARN of the secret for the application's ALGORITHM."
  value       = aws_secretsmanager_secret.app_algorithm.arn
}

output "app_token_expire_arn" {
  description = "The ARN of the secret for the application's ACCESS_TOKEN_EXPIRE_MINUTES."
  value       = aws_secretsmanager_secret.app_token_expire.arn
}

output "app_google_api_key_arn" {
  description = "The ARN of the secret for the application's GOOGLE_API_KEY."
  value       = aws_secretsmanager_secret.app_google_api_key.arn
}

