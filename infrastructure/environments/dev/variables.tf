# ------------------------------------------------------------------------------
# GENERAL VARIABLES
# ------------------------------------------------------------------------------
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

variable "availability_zones" {
  description = "A list of availability zones to use for the VPC subnets."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ------------------------------------------------------------------------------
# RDS (DATABASE) VARIABLES
# ------------------------------------------------------------------------------
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
  sensitive   = true # Prevents Terraform from showing the password in logs
}

# ------------------------------------------------------------------------------
# ECS (COMPUTE) VARIABLES
# ------------------------------------------------------------------------------
variable "instance_type" {
  description = "The EC2 instance type for the ECS cluster nodes."
  type        = string
  default     = "t2.micro" # Free-tier eligible
}

variable "min_size" {
  description = "The minimum number of EC2 instances in the Auto Scaling Group."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "The maximum number of EC2 instances in the Auto Scaling Group."
  type        = number
  default     = 2
}

variable "desired_capacity" {
  description = "The desired number of EC2 instances to run."
  type        = number
  default     = 1
}

variable "ec2_key_name" {
  description = "The name of the EC2 key pair for SSH access (optional)."
  type        = string
  default     = null # Set to your key name if you created one
}

variable "container_port" {
  description = "The port the application container listens on."
  type        = number
  default     = 8080
}

