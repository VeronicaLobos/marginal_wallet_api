# /infrastructure/global/variables.tf

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "project_name" {
  description = "The overall name for the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
}

