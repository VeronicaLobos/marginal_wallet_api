# Terraform AWS ECR Module

This Terraform module provisions a private **Amazon Elastic Container Registry (ECR)** repository. ECR is a fully-managed Docker container registry that makes it easy for developers to store, manage, and deploy Docker container images.

Using a private ECR repository is a best practice for AWS deployments as it provides secure, high-performance storage for application images and integrates seamlessly with AWS IAM and ECS.

## Resources Created

This module creates a single `aws_ecr_repository` resource with a lifecycle policy set to keep the image tag mutable.

## Usage

This module is called from an environment-specific configuration (e.g., `environments/dev/main.tf`) to create a dedicated repository for that environment's container images.

```hcl
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}
```

## Inputs

The following input variables are defined in `variables.tf`:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | The name of the project, used to prefix the repository name | `string` | n/a | yes |
| environment | The deployment environment (e.g., dev, staging) | `string` | n/a | yes |

## Outputs

The following outputs are defined in `outputs.tf`:

| Name | Description |
|------|-------------|
| repository_url | The URL of the ECR repository, used by Docker and ECS |

## Requirements

- Terraform >= 1.0
- AWS Provider
