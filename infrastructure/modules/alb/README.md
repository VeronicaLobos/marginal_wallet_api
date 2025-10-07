# Terraform AWS Application Load Balancer (ALB) Module

This Terraform module provisions a complete, public-facing Application Load Balancer (ALB) designed to route HTTP traffic to a backend service, such as an ECS cluster.

## Resources Created

The module creates the following core resources:

- **Application Load Balancer** (`aws_lb`) - The main load balancer resource that distributes incoming application traffic
- **ALB Security Group** (`aws_security_group`) - Acts as a virtual firewall for the load balancer, configured to allow inbound HTTP traffic from the internet (`0.0.0.0/0`) on port 80
- **Target Group** (`aws_lb_target_group`) - A logical grouping of targets, such as ECS tasks, that will receive traffic from the load balancer. It includes a health check configuration to ensure traffic is only sent to healthy targets
- **HTTP Listener** (`aws_lb_listener`) - A process that checks for connection requests on port 80 and forwards them to the specified target group

## Usage

This module is called from an environment-specific configuration (e.g., `environments/dev/main.tf`). It requires the ID of the VPC and the IDs of the public subnets where it should be deployed.

```hcl
module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}
```

## Inputs

The following input variables are defined in `variables.tf`:

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | The name of the project, used to prefix resource names | `string` | n/a | yes |
| environment | The deployment environment (e.g., dev, staging) | `string` | n/a | yes |
| vpc_id | The ID of the VPC where the ALB will be deployed | `string` | n/a | yes |
| public_subnet_ids | A list of public subnet IDs for the ALB | `list(string)` | n/a | yes |

## Outputs

The following outputs are defined in `outputs.tf`:

| Name | Description |
|------|-------------|
| alb_dns_name | The public DNS name of the Application Load Balancer |
| target_group_arn | The ARN of the main target group for the ECS service |
| alb_security_group_id | The ID of the security group attached to the ALB |
| alb_listener_arn | The ARN of the HTTP listener, used for creating dependencies |

## Requirements

- Terraform >= 1.0
- AWS Provider
- Existing VPC with public subnets