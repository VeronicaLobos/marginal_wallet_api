# Terraform AWS RDS Module

This Terraform module provisions a production-ready **Amazon Relational Database Service (RDS)** instance for PostgreSQL. It is designed to be deployed within a private network, ensuring the database is not exposed to the public internet.

## Resources Created

The module creates the following core resources:

- **RDS DB Instance** (`aws_db_instance`) - The managed PostgreSQL database server. It is configured to be `t3.micro` for Free Tier eligibility and is not publicly accessible
- **DB Subnet Group** (`aws_db_subnet_group`) - This tells RDS which private subnets within your VPC the database is allowed to be placed in, ensuring high availability across multiple Availability Zones
- **Security Group** (`aws_security_group`) - Acts as a virtual firewall for the database, with a rule that only allows inbound traffic on the PostgreSQL port (5432) from within the VPC
- **AWS Secrets Manager Secret** (`aws_secretsmanager_secret`) - A secure "lockbox" is created to store the database's full connection URL, which the application can then retrieve at runtime

## Usage

This module is called from an environment-specific configuration (e.g., `environments/dev/main.tf`). It requires information from the VPC module to place itself correctly within the network.

```hcl
module "rds" {
  source = "../../modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  vpc_cidr_block     = module.vpc.vpc_cidr_block
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password
}
```

## Inputs

The following input variables are defined in `variables.tf`:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | The name of the project, used to prefix resource names | `string` | n/a | yes |
| environment | The deployment environment (e.g., dev, staging) | `string` | n/a | yes |
| vpc_id | The ID of the VPC where the database will be deployed | `string` | n/a | yes |
| private_subnet_ids | A list of private subnet IDs for the DB Subnet Group | `list(string)` | n/a | yes |
| vpc_cidr_block | The CIDR block of the VPC, used for the security group rule | `string` | n/a | yes |
| db_name | The name of the database to create in the instance | `string` | n/a | yes |
| db_username | The master username for the database | `string` | n/a | yes |
| db_password | The master password for the database | `string` | n/a | yes |

## Outputs

The following outputs are defined in `outputs.tf`:

| Name | Description |
|------|-------------|
| rds_endpoint | The connection endpoint for the database instance |
| rds_security_group_id | The ID of the security group attached to the RDS instance |
| db_url_secret_arn | The ARN of the secret that stores the full database connection URL |

## Security Notes

- The database is **not publicly accessible** and is deployed in private subnets
- Database credentials are securely stored in AWS Secrets Manager
- Security group restricts access to port 5432 from within the VPC only

## Requirements

- Terraform >= 1.0
- AWS Provider
- Existing VPC with private subnets
