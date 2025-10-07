# Terraform AWS VPC Module

This Terraform module provisions a foundational **Amazon Virtual Private Cloud (VPC)**. It creates a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network that you define.

This module is the first and most critical building block of the infrastructure, creating a secure and highly available network environment.

## Resources Created

The module creates the following core resources:

- **Virtual Private Cloud** (`aws_vpc`) - The main network container
- **Public Subnets** (`aws_subnet`) - Two subnets distributed across different Availability Zones, intended for public-facing resources like the Application Load Balancer
- **Private Subnets** (`aws_subnet`) - Two subnets also distributed across Availability Zones, intended for secure backend resources like the RDS database and ECS container instances
- **Internet Gateway** (`aws_internet_gateway`) - The "front door" of the VPC, allowing communication between resources in the public subnets and the internet
- **Public Route Table** (`aws_route_table`) - Provides a route to the Internet Gateway, which is then associated with the public subnets

## Usage

This module is called from an environment-specific configuration (e.g., `environments/dev/main.tf`) to create the network for that environment.

```hcl
module "vpc" {
  source = "../../modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  availability_zones = var.availability_zones
}
```

## Inputs

The following input variables are defined in `variables.tf`:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | The name of the project, used to prefix resource names | `string` | n/a | yes |
| environment | The deployment environment (e.g., dev, staging) | `string` | n/a | yes |
| availability_zones | A list of two availability zones to use for the subnets | `list(string)` | n/a | yes |

## Outputs

The following outputs are defined in `outputs.tf`:

| Name | Description |
|------|-------------|
| vpc_id | The ID of the created VPC |
| public_subnet_ids | A list of IDs for the public subnets |
| private_subnet_ids | A list of IDs for the private subnets |
| vpc_cidr_block | The primary IPv4 CIDR block for the VPC |

## Architecture

This module creates a multi-AZ VPC architecture with the following design:

- **High Availability**: Resources are distributed across two Availability Zones
- **Network Segmentation**: Separate public and private subnets for different resource types
- **Internet Access**: Public subnets have direct internet access via the Internet Gateway

## Requirements

- Terraform >= 1.0
- AWS Provider
- Two availability zones in your chosen region
