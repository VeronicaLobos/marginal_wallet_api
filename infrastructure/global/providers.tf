# This file configures the AWS provider.
# It uses the "aws_region" variable, allowing for flexibility.
provider "aws" {
  region = var.aws_region
}