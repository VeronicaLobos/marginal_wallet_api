# /infrastructure/modules/ecr/outputs.tf

# We output the repository URL so our CI/CD pipeline knows where to push the Docker image.
output "repository_url" {
  description = "The URL of the ECR repository."
  value       = aws_ecr_repository.main.repository_url
}
