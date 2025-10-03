# /infrastructure/environments/dev/variables.tf

# This file defines the specific values for the 'dev' environment variables.

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "marginal-wallet"
}

variable "environment" {
  description = "The environment name."
  type        = string
  default     = "dev"
}

variable "availability_zones" {
  description = "A list of availability zones for the VPC subnets."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_password" {
  description = "The master password for the RDS database."
  type        = string
  sensitive   = true
}
