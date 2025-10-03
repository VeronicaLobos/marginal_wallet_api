# /infrastructure/modules/rds/outputs.tf

output "db_instance_endpoint" {
  description = "The connection endpoint for the RDS instance."
  value       = aws_db_instance.main.endpoint
}

output "db_instance_port" {
  description = "The port for the RDS instance."
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "The name of the database."
  value       = aws_db_instance.main.db_name
}
