# Configures Terraform to store its state file remotely in an AWS S3 bucket.
# This backend will be used for the global resources like IAM roles.
terraform {
  backend "s3" {
    bucket         = "marginal-wallet-api-tfstate-veronica" # Use your globally unique bucket name
    key            = "global/iam/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
