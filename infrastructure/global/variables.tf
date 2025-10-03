# Global variables that can be used across all environments.

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "us-east-1" # Change this to your preferred region
}

variable "project_name" {
  description = "The overall name for the project, used to prefix resource names."
  type        = string
  default     = "marginal-wallet" # Change this to your project name
}
