output "db_endpoint" {
  description = "The endpoint of the RDS instance."
  value       = aws_db_instance.main.endpoint
}

output "db_port" {
  description = "The port of the RDS instance."
  value       = aws_db_instance.main.port
}

output "rds_security_group_id" {
  description = "The ID of the security group for the RDS instance."
  value       = aws_security_group.rds.id
}

output "db_url_secret_arn" {
  description = "The ARN of the secret containing the full database URL."
  value       = aws_secretsmanager_secret.db_url.arn
}
