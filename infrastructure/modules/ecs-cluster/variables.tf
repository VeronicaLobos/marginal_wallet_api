# This file defines all the inputs (the "settings") that the ECS Cluster
# module requires to build its resources.

# ------------------------------------------------------------------------------
# Basic Information
# ------------------------------------------------------------------------------
variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
}

variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

# ------------------------------------------------------------------------------
# Networking Inputs (from the VPC module)
# ------------------------------------------------------------------------------
variable "vpc_id" {
  description = "The ID of the VPC where the cluster will be deployed."
  type        = string
}

variable "private_subnet_ids" {
  description = "A list of private subnet IDs for the EC2 instances."
  type        = list(string)
}

# ------------------------------------------------------------------------------
# Compute (EC2 Instance) Configuration
# ------------------------------------------------------------------------------
variable "instance_type" {
  description = "The EC2 instance type for the ECS container instances."
  type        = string
}

variable "ami_id" {
  description = "The ID of the Amazon Machine Image (AMI) to use for the EC2 instances."
  type        = string
}

variable "ec2_key_name" {
  description = "The name of the EC2 key pair for SSH access (optional)."
  type        = string
  default     = null
}

# ------------------------------------------------------------------------------
# Auto Scaling Configuration
# ------------------------------------------------------------------------------
variable "min_size" {
  description = "The minimum number of EC2 instances in the Auto Scaling Group."
  type        = number
}

variable "max_size" {
  description = "The maximum number of EC2 instances in the Auto Scaling Group."
  type        = number
}

variable "desired_capacity" {
  description = "The desired number of EC2 instances in the Auto Scaling Group."
  type        = number
}

# ------------------------------------------------------------------------------
# IAM Role Inputs (from the global module)
# ------------------------------------------------------------------------------
variable "ecs_instance_profile_name" {
  description = "The name of the IAM instance profile for the EC2 instances."
  type        = string
}

variable "ecs_task_execution_role_arn" {
  description = "The ARN of the IAM role that allows ECS to manage resources."
  type        = string
}

variable "ecs_task_role_arn" {
  description = "The ARN of the IAM role for the application running in the task."
  type        = string
}

# ------------------------------------------------------------------------------
# Application Container & ALB Inputs
# ------------------------------------------------------------------------------
variable "ecr_repository_url" {
  description = "The URL of the ECR repository containing the application image."
  type        = string
}

variable "target_group_arn" {
  description = "The ARN of the ALB target group to which tasks will be registered."
  type        = string
}

variable "alb_listener" {
  description = "The ALB listener to which the service depends on."
  type        = string
}

variable "rds_security_group_id" {
  description = "The ID of the RDS security group to allow outbound traffic to."
  type        = string
}

variable "alb_security_group_id" {
  description = "The ID of the ALB security group to allow inbound traffic from."
  type        = string
}

# ------------------------------------------------------------------------------
# Secret Inputs (from the global module)
# ------------------------------------------------------------------------------
variable "db_url_secret_arn" {
  description = "The ARN of the secret containing the full database URL."
  type        = string
}

variable "app_secret_key_arn" {
  description = "The ARN of the secret for the application's SECRET_KEY."
  type        = string
}

variable "app_algorithm_arn" {
  description = "The ARN of the secret for the application's ALGORITHM."
  type        = string
}

variable "app_token_expire_arn" {
  description = "The ARN of the secret for the ACCESS_TOKEN_EXPIRE_MINUTES."
  type        = string
}

variable "app_google_api_key_arn" {
  description = "The ARN of the secret for the GOOGLE_API_KEY."
  type        = string
}

