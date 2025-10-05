# This module creates a secure, private RDS PostgreSQL instance.

# 1. DB Subnet Group: A list of approved private subnets where the DB can exist.
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-rds-sng"
  subnet_ids = var.private_subnet_ids
  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sng"
  }
}

# 2. Security Group: The firewall for the database.
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow inbound traffic from the application"
  vpc_id      = var.vpc_id

  # Ingress (Inbound) Rule: Allow PostgreSQL traffic (port 5432) ONLY from
  # within the same VPC. We will later add a specific rule from the ECS tasks.
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block] # Allows access from anywhere inside the VPC
  }

  # Egress (Outbound) Rule: Allow all outbound traffic.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}

# 3. The RDS Database Instance
resource "aws_db_instance" "main" {
  identifier           = "${var.project_name}-${var.environment}-rds"
  engine               = "postgres"
  engine_version       = "16.3"
  instance_class       = "db.t3.micro" # Free Tier eligible
  allocated_storage    = 20
  storage_type         = "gp2"
  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible  = false
  skip_final_snapshot  = true
  apply_immediately    = false

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-instance"
  }
}

# 4. Create a secret in Secrets Manager for the full database URL.
resource "aws_secretsmanager_secret" "db_url" {
  name = "${var.project_name}-${var.environment}-db-url"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 5. Populate that secret with the database connection string.
resource "aws_secretsmanager_secret_version" "db_url_value" {
  secret_id     = aws_secretsmanager_secret.db_url.id
  secret_string = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
}
