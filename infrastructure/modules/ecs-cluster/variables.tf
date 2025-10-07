# This file defines the "settings panel" for the ECS Cluster module. It is the
# definitive list of all inputs this module requires to build the compute layer.

# --- General Info ---
variable "project_name" {
  description = "The name of the project."
  type        = string
}
variable "environment" {
  description = "The deployment environment."
  type        = string
}
variable "aws_region" {
  description = "The AWS region where resources are deployed."
  type        = string
}

# --- Networking Inputs (from VPC module) ---
variable "vpc_id" {
  description = "The ID of the VPC where the cluster will be deployed."
  type        = string
}
variable "private_subnet_ids" {
  description = "A list of private subnet IDs for the ECS tasks."
  type        = list(string)
}

# --- EC2 Instance Configuration ---
variable "instance_type" {
  description = "The EC2 instance type for the ECS cluster nodes."
  type        = string
}
variable "min_size" {
  description = "The minimum number of EC2 instances in the Auto Scaling Group."
  type        = number
}
variable "max_size" {
  description = "The maximum number of EC2 instances in the Auto Scaling Group."
  type        = number
}
variable "desired_capacity" {
  description = "The desired number of EC2 instances to run."
  type        = number
}
variable "ec2_key_name" {
  description = "The name of the EC2 key pair for SSH access (optional)."
  type        = string
  default     = null
}
variable "ami_id" {
  description = "The ID of the Amazon Machine Image (AMI) to use for the EC2 instances."
  type        = string
}

# --- ALB & RDS Integration ---
variable "alb_security_group_id" {
  description = "The ID of the security group for the Application Load Balancer."
  type        = string
}
variable "rds_security_group_id" {
  description = "The ID of the security group for the RDS database instance."
  type        = string
}
variable "target_group_arn" {
  description = "The ARN of the ALB target group to which the ECS service will register tasks."
  type        = string
}
variable "alb_listener" {
  description = "The ALB listener to ensure the service depends on it."
  type        = any # Used for depends_on, so type is not critical
}

# --- IAM Role Inputs (from Global module) ---
variable "ecs_instance_profile_name" {
  description = "The name of the IAM instance profile for the EC2 instances."
  type        = string
}
variable "ecs_task_execution_role_arn" {
  description = "The ARN of the IAM role for ECS task execution."
  type        = string
}
variable "ecs_task_role_arn" {
  description = "The ARN of the IAM role for the application task."
  type        = string
}

# --- Task Definition & Service Configuration ---
variable "ecr_repository_url" {
  description = "The URL of the ECR repository where the application image is stored."
  type        = string
}
variable "container_port" {
  description = "The port the application container listens on."
  type        = number
}

# --- Secrets (ARNs from Global & RDS modules) ---
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
  description = "The ARN of the secret for ACCESS_TOKEN_EXPIRE_MINUTES."
  type        = string
}
variable "app_google_api_key_arn" {
  description = "The ARN of the secret for the GOOGLE_API_KEY."
  type        = string
}
