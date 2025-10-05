# This file defines the input variables for the global module.

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "project_name" {
  description = "The overall name for the project, used to prefix resource names."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
}
