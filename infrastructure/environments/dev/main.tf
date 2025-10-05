# This file defines the 'dev' environment by calling all our reusable modules.

# It calls the following modules in the order they have been implemented:
# - global: Creates shared resources like IAM roles and Secrets Manager secrets.
# Looks up the latest ECS-optimized AMI for our region.
# - vpc: Sets up the networking (VPC, subnets, route tables).
# - rds: Creates a PostgreSQL database in the private subnets.
# - ecr: Sets up a private Docker image repository.
# - alb: Creates a public-facing Application Load Balancer.
# - ecs_cluster: Creates the ECS cluster, EC2 instances, and services to run
#   our application containers.

# ------------------------------------------------------------------------------
# GLOBAL & SHARED RESOURCES
# ------------------------------------------------------------------------------
# The 'global' module creates resources that are not specific to an environment,
# like IAM roles and Secrets Manager secrets.
module "global" {
  source = "../../global"

  project_name = var.project_name
}

# ------------------------------------------------------------------------------
# DATA SOURCES
# ------------------------------------------------------------------------------
# This looks up the latest ECS-optimized AMI for our region.
data "aws_ami" "ecs_optimized_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
}


# ------------------------------------------------------------------------------
# NETWORKING
# ------------------------------------------------------------------------------
# The 'vpc' module creates our foundational network.
module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  availability_zones = var.availability_zones
}

# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------
# The 'rds' module creates our PostgreSQL database in the private subnets.
module "rds" {
  source = "../../modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  vpc_cidr_block     = module.vpc.vpc_cidr_block
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password # This is passed securely at runtime
}

# ------------------------------------------------------------------------------
# CONTAINER REGISTRY
# ------------------------------------------------------------------------------
# The 'ecr' module creates our private Docker image repository.
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

# ------------------------------------------------------------------------------
# LOAD BALANCER
# ------------------------------------------------------------------------------
# The 'alb' module creates our public-facing Application Load Balancer.
module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}


# ------------------------------------------------------------------------------
# COMPUTE (ECS CLUSTER)
# ------------------------------------------------------------------------------
# The 'ecs_cluster' module creates the EC2 instances, cluster, and services
# to run our application container. This is the final piece that connects
# everything together.
module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  # General Info
  project_name    = var.project_name
  environment     = var.environment
  aws_region      = var.aws_region

  # Networking Inputs (from VPC module)
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # EC2 Instance Configuration
  instance_type  = var.instance_type
  min_size       = var.min_size
  max_size       = var.max_size
  desired_capacity = var.desired_capacity
  ami_id         = data.aws_ami.ecs_optimized_linux.id
  ec2_key_name   = var.ec2_key_name

  # Security & IAM Inputs
  alb_security_group_id         = module.alb.alb_security_group_id
  db_security_group_id          = module.rds.rds_security_group_id
  ecs_instance_profile_name     = module.global.ecs_instance_profile_name
  ecs_task_execution_role_arn = module.global.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.global.ecs_task_role_arn

  # Application Container Configuration
  ecr_repository_url = module.ecr.repository_url
  container_port     = var.container_port
  target_group_arn   = module.alb.target_group_arn

  # Secrets Configuration (from global module)
  db_password_secret_arn      = module.global.db_password_secret_arn
  app_secret_key_arn          = module.global.app_secret_key_arn
  app_algorithm_arn           = module.global.app_algorithm_arn
  app_token_expire_arn        = module.global.app_token_expire_arn
  app_google_api_key_arn      = module.global.app_google_api_key_arn
}

