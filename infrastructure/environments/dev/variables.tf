# /infrastructure/environments/dev/variables.tf

# General variables for the dev environment
variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "marginal-wallet"
}

variable "environment" {
  description = "The deployment environment."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "The AWS region to deploy to."
  type        = string
  default     = "us-east-1"
}

# Variable for the VPC module
variable "availability_zones" {
  description = "A list of availability zones to use for the VPC subnets."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# RDS specific variables
variable "db_name" {
  description = "The name of the RDS database."
  type        = string
  default     = "marginal_wallet"
}

variable "db_username" {
  description = "The master username for the RDS database."
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "The master password for the RDS database."
  type        = string
  sensitive   = true # This prevents Terraform from showing the password in logs
}
