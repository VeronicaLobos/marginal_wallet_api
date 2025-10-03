# /infrastructure/modules/rds/variables.tf

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The environment name (e.g., dev, staging, prod)."
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC where the RDS instance will be deployed."
  type        = string
}

variable "vpc_cidr_block" {
  description = "The CIDR block of the VPC."
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs for the RDS instance."
  type        = list(string)
}

variable "db_instance_class" {
  description = "The instance class for the RDS database."
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "The master username for the RDS database."
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "The master password for the RDS database."
  type        = string
  sensitive   = true # Marks this variable as sensitive in Terraform outputs
}

variable "db_name" {
  description = "The name of the initial database to create."
  type        = string
  default     = "marginal_wallet"
}
