# This file defines the 'dev' environment by calling our reusable modules.

# Call the VPC module to create our network
module "vpc" {
  source = "../../modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  availability_zones = var.availability_zones
}

# Call the RDS module to create our database
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

# Call the ECR module to create our container registry
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

# Call the ALB module to create our load balancer
module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}
