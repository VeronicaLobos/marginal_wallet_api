# /infrastructure/environments/dev/main.tf

# This is the entry point for our 'dev' environment. It calls the reusable
# modules and provides them with the specific values for this environment.

provider "aws" {
  region = var.aws_region
}

# This "data" block retrieves information about your AWS account.
# We will use the account ID later for our ECR repository URL.
data "aws_caller_identity" "current" {}

# Call the VPC Module
# This tells Terraform to use our VPC module to create a network.
module "vpc" {
  source = "../../modules/vpc" # Path to the module

  # Pass variables to the module
  project_name       = var.project_name
  environment        = var.environment
  availability_zones = var.availability_zones
}
