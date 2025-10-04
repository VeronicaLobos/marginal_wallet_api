# /infrastructure/modules/ecr/main.tf

# This resource creates a new private ECR repository where our Docker images will be stored.
resource "aws_ecr_repository" "main" {
  name = "${var.project_name}-${var.environment}-ecr" # e.g., marginal-wallet-dev-ecr

  # This setting ensures that if an image tag is overwritten (e.g., we push a new 'latest' tag),
  # the old, untagged image is not automatically deleted.
  image_tag_mutability = "MUTABLE"

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecr"
    Project     = var.project_name
    Environment = var.environment
  }
}
