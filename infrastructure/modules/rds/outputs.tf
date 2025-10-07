# This file defines the outputs of the RDS module.

output "rds_endpoint" {
  description = "The connection endpoint for the RDS instance."
  value       = aws_db_instance.main.endpoint
}

output "rds_security_group_id" {
  description = "The ID of the security group attached to the RDS instance."
  value       = aws_security_group.rds.id
}

output "db_url_secret_arn" {
  description = "The ARN of the secret containing the full database connection URL."
  value       = aws_secretsmanager_secret.db_url.arn
}

