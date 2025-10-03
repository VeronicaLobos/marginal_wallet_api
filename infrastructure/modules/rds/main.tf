# /infrastructure/modules/rds/main.tf

# This Terraform module provisions an AWS RDS instance along with a
# corresponding database subnet group and security group.

# 1. Database Subnet Group: Tells RDS which subnets it is allowed to live in.
# We will place our database in the private subnets for security.
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-rds-sng"
  subnet_ids = var.private_subnet_ids # Input from the VPC module

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sng"
  }
}

# 2. RDS Security Group: Acts as a virtual firewall for the database.
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow inbound traffic from the application"
  vpc_id      = var.vpc_id # Input from the VPC module

  # Ingress Rule: Allow PostgreSQL traffic (port 5432) only from within the VPC.
  # We will later refine this to only allow traffic from the ECS tasks' security group.
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block] # Allows traffic from anywhere inside the VPC
  }

  # Egress Rule: Allow all outbound traffic.
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

# 3. RDS Database Instance: The actual PostgreSQL database.
resource "aws_db_instance" "main" {
  identifier           = "${var.project_name}-${var.environment}-rds"
  engine               = "postgres"
  engine_version       = "16.3" # Latest stable version
  instance_class       = var.db_instance_class # Free Tier eligible: "db.t3.micro"
  allocated_storage    = 20
  storage_type         = "gp2"
  username             = var.db_username
  password             = var.db_password # Securely passed in as a variable
  db_name              = var.db_name
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot  = true # Important for dev/testing to allow easy deletion
  publicly_accessible  = false # Crucial for security - only accessible from within the VPC

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-instance"
  }
}
