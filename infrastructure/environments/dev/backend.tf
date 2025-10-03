# This configures the remote backend for the 'dev' environment.
# Note that it uses the same bucket as the global state, but a different 'key' (folder).
# This is a critical best practice to keep environment states separate.
terraform {
  backend "s3" {
    bucket         = "marginal-wallet-api-tfstate-veronica" # Use your globally unique bucket name
    key            = "environments/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
