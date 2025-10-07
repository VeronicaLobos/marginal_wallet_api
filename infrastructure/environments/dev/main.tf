# This file defines the 'dev' environment by calling all reusable modules.

# --- Data Sources ---
# Looks up the latest ECS-optimized Amazon Linux AMI ID.
data "aws_ami" "ecs_optimized_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
}

# --- Global Resources ---
# Calls the global module to create/reference shared IAM roles and secrets.
module "global" {
  source = "../../global"

  aws_region   = var.aws_region
  project_name = var.project_name
  environment  = var.environment
}

# --- VPC Module ---
module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  availability_zones = var.availability_zones
  vpc_cidr           = "10.0.0.0/16"
}

# --- RDS Module ---
module "rds" {
  source = "../../modules/rds"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  vpc_cidr_block        = module.vpc.vpc_cidr_block
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
}

# --- ECR Module ---
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

# --- ALB Module ---
module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}

# --- ECS Cluster Module (Final Assembly) ---
# This block connects all the other modules together.
module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  # General Info
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  # Networking
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # EC2 Configuration
  instance_type    = var.instance_type
  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity
  ec2_key_name     = var.ec2_key_name
  ami_id           = data.aws_ami.ecs_optimized_linux.id

  # ALB & RDS Integration
  alb_security_group_id = module.alb.alb_security_group_id
  rds_security_group_id = module.rds.rds_security_group_id
  target_group_arn      = module.alb.target_group_arn
  alb_listener          = module.alb.alb_listener

  # IAM Roles from global module
  ecs_instance_profile_name   = module.global.ecs_instance_profile_name
  ecs_task_execution_role_arn = module.global.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.global.ecs_task_role_arn

  # ECR Image & Container Port
  ecr_repository_url = module.ecr.repository_url
  container_port     = var.container_port

  # Secrets from global and rds modules
  db_url_secret_arn        = module.rds.db_url_secret_arn
  app_secret_key_arn       = module.global.app_secret_key_arn
  app_algorithm_arn        = module.global.app_algorithm_arn
  app_token_expire_arn     = module.global.app_token_expire_arn
  app_google_api_key_arn   = module.global.app_google_api_key_arn
}

