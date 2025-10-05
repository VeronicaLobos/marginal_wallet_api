# Terraform AWS ECS Cluster Module (EC2 Launch Type)

This module provisions a complete, production-ready ECS Cluster on AWS using the EC2 launch type. It is designed to be a reusable component for running containerized applications.

## Resources Created

The module creates the following core resources:

- **ECS Cluster** - Manages tasks and services
- **EC2 Launch Template** - Defines the configuration for the cluster's virtual servers, including the ECS-optimized AMI and the necessary IAM role
- **Auto Scaling Group (ASG)** - Manages the fleet of EC2 instances, ensuring the desired number of servers are always running and healthy across multiple Availability Zones
- **Security Group** - For the EC2 instances, with rules to allow traffic from the Application Load Balancer and to the RDS database
- **ECS Task Definition** - Acts as a blueprint for the application container, defining the Docker image, resource limits, and environment variables sourced securely from AWS Secrets Manager
- **ECS Service** - Maintains the desired number of running tasks (containers) and registers them with the Application Load Balancer

## Usage

This module is called from an environment-specific configuration (e.g., `environments/dev/main.tf`). You must provide it with information from your VPC, ALB, ECR, and global IAM modules.

```hcl
module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  # General Info
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  # Networking
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # EC2 Configuration
  instance_type    = var.instance_type
  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity
  ec2_key_name     = var.ec2_key_name
  ami_id           = data.aws_ami.ecs_optimized_linux.id

  # ALB & RDS Integration
  alb_security_group_id = module.alb.alb_security_group_id
  rds_security_group_id = module.rds.rds_security_group_id
  target_group_arn      = module.alb.target_group_arn
  alb_listener          = module.alb.alb_listener_arn # Note: Pass the ARN here for dependency

  # IAM Roles
  ecs_instance_profile_name   = module.global.ecs_instance_profile_name
  ecs_task_execution_role_arn = module.global.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.global.ecs_task_role_arn

  # ECR Image
  ecr_repository_url = module.ecr.repository_url

  # Secrets from AWS Secrets Manager
  db_url_secret_arn        = module.rds.db_url_secret_arn
  app_secret_key_arn       = module.global.app_secret_key_arn
  app_algorithm_arn        = module.global.app_algorithm_arn
  app_token_expire_arn     = module.global.app_token_expire_arn
  app_google_api_key_arn   = module.global.app_google_api_key_arn
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | The name of the project | `string` | n/a | yes |
| environment | The deployment environment (e.g., dev, staging, prod) | `string` | n/a | yes |
| aws_region | The AWS region where resources are deployed | `string` | n/a | yes |
| vpc_id | The ID of the VPC where the cluster will be deployed | `string` | n/a | yes |
| private_subnet_ids | A list of private subnet IDs for the ECS tasks | `list(string)` | n/a | yes |
| instance_type | The EC2 instance type for the ECS cluster nodes | `string` | n/a | yes |
| min_size | The minimum number of EC2 instances in the Auto Scaling Group | `number` | n/a | yes |
| max_size | The maximum number of EC2 instances in the Auto Scaling Group | `number` | n/a | yes |
| desired_capacity | The desired number of EC2 instances to run | `number` | n/a | yes |
| ec2_key_name | The name of the EC2 key pair for SSH access (optional) | `string` | `null` | no |
| ami_id | The ID of the Amazon Machine Image (AMI) to use for the EC2 instances | `string` | n/a | yes |
| alb_security_group_id | The ID of the security group for the Application Load Balancer | `string` | n/a | yes |
| rds_security_group_id | The ID of the security group for the RDS database instance | `string` | n/a | yes |
| target_group_arn | The ARN of the ALB target group for the ECS service | `string` | n/a | yes |
| alb_listener_arn | The ARN of the ALB listener to create a dependency | `string` | n/a | yes |
| ecs_instance_profile_name | The name of the IAM instance profile for the EC2 instances | `string` | n/a | yes |
| ecs_task_execution_role_arn | The ARN of the IAM role for ECS task execution | `string` | n/a | yes |
| ecs_task_role_arn | The ARN of the IAM role for the application task | `string` | n/a | yes |
| ecr_repository_url | The URL of the ECR repository where the application image is stored | `string` | n/a | yes |
| db_url_secret_arn | The ARN of the secret containing the full database URL | `string` | n/a | yes |
| app_secret_key_arn | The ARN of the secret for the application's SECRET_KEY | `string` | n/a | yes |
| app_algorithm_arn | The ARN of the secret for the application's ALGORITHM | `string` | n/a | yes |
| app_token_expire_arn | The ARN of the secret for ACCESS_TOKEN_EXPIRE_MINUTES | `string` | n/a | yes |
| app_google_api_key_arn | The ARN of the secret for the GOOGLE_API_KEY | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| ecs_cluster_name | The name of the created ECS cluster |

## Requirements

- Terraform >= 1.0
- AWS Provider
- Existing VPC, ALB, RDS, and IAM infrastructure modules

---
# Phase5: Infrastructure as Code for FastAPI Application on AWS ECS with EC2 Launch Type
This phase focuses on setting up the necessary infrastructure for deploying a FastAPI application using AWS ECS with the EC2 launch type. We will use Terraform to define and manage our infrastructure as code.
This phase is the most complex and involves multiple steps to ensure that all components are correctly configured and integrated.

Plan:

Update `infrastructure/global/` files:
We define shared resources like IAM Roles in the global/ directory and use outputs.tf to publish their ARNs so other environments can use them.
* [Step 5a.1](#phase-5a-step-1-of-3-create-the-global-secrets-in-aws-secrets-manager): Create the Global Secrets in AWS Secrets Manager (`sm.tf`)
* [Step 5a.2](#phase-5a-step-2-of-3-create-the-iam-roles): Create the IAM Roles (`iam.tf`)
* [Step 5a.3](#phase-5a-step-3-of-3-update-global-outputs): Update Global Outputs (`outputs.tf`)

Update `infrastructure/modules/ecs-cluster/` files:
We will create a new module for the ECS cluster that includes all the necessary resources and configurations that form the reusable "blueprint" for our application's compute layer.
* [Step 5b.1](#phase-5b-step-1-of-6-define-the-ecs-clusters-core-resources): Define the core cluster or "office space" and EC2 resources (`main.tf`)
* [Step 5b.2](#phase-5b-step-2-of-6-define-the-ecs-clusters-security): Define the "key card access" for your cluster (`security-groups.tf`)
* [Step 5b.3](#phase-5b-step-3-of-6-define-the-ecs-task-definition): Define the "job description" for your container (`task-definition.tf`)
* [Step 5b.4](#phase-5b-step-4-of-6-define-the-ecs-service): Define the "project manager" that runs your containers (`ecs-service.tf`)
* [Step 5b.5](#phase-5b-step-5-of-6-define-the-modules-variables): Define the module's "settings panel" (`variables.tf`)
* [Step 5b.6](#phase-5b-step-6-of-6-define-the-modules-outputs): Define the module's "connection points" (`outputs.tf)

Update `infrastructure/environments/dev/` files:
The final step will be to update the files in environments/dev/ to call this new ECS module and connect all the pieces together.
* [Step 5c.1](#phase-5c-step-1-of-3-update-the-maintf-to-include-the-ecs-cluster-module): Update the `main.tf` to include the ECS cluster module (the "master plan")
* [Step 5c.2](#phase-5c-step-2-of-3-update-the-variablestf-to-include-the-necessary-variables): Update the `variables.tf` to include the necessary variables (the "settings panel")
* [Step 5c.3](#phase-5c-step-3-of-3-update-the-outputstf-to-include-outputs-from-the-ecs-cluster-module): Update the `outputs.tf` to include outputs from the ECS cluster module (the "final output")

---
## Phase 5a, Step 1 of 3: Create the Global Secrets in AWS Secrets Manager
Before we set up the ECS cluster, we need to ensure that our application can securely access sensitive information like database credentials.
These secrets we originally set in the remote repository Secrets for the CD, but now we will store them in AWS Secrets Manager so that our ECS tasks can access them at runtime.
> 💡 `infrastructure/global/sm.tf` creates secrets to safely store sensitive information

## Phase 5a, Step 2 of 3: Create the IAM Roles
We need to create the "ID cards" (IAM Roles) that our virtual servers and application containers will use.

> 💡 `infrastructure/global/iam.tf` creates the following IAM roles:
* **ecs_task_execution_role (The "Setup Crew" ID)**:
This allows the ECS service to do its setup work: pull the container image from ECR and send logs to CloudWatch.
* **ecs_task_role (The "Application's" ID)**:
This is the one for the application code inside the container. This role gives your FastAPI app permission to talk to other AWS services. We will use this to grant it access to read secrets from Secrets Manager.
* **ecs_instance_role (The "Server's" ID)**:
This allows the EC2 virtual servers to communicate with and join the ECS cluster, effectively saying, "I'm here and ready for work!"

The following two roles are the "glue" that attaches the necessary permissions to the above roles, and the roles to the EC2 instances.
* **aws_iam_role_policy_attachment (The "Badge Printer")**:
This attaches the necessary policies to each role, ensuring they have the right permissions to perform their tasks.
* **aws_iam_instance_profile (The "Uniform")**:
This is the profile that EC2 instances will wear, linking them to their IAM role.

## Phase 5a, Step 3 of 3: Update Global Outputs
We've just updated `infrastructure/global/iam.tf` to define the three necessary IAM roles. file's job is to retrieve the ARNs (the unique "ID numbers") of these roles so we can pass them as inputs to our ecs-cluster module.

> 💡 `infrastructure/global/outputs.tf` exports the ARNs of the IAM roles we just created.

Now, we can reference these ARNs in our ECS cluster module to ensure that our EC2 instances and ECS tasks have the correct permissions to operate.

---
## Phase 5b, Step 1 of 6: Define the ECS Cluster's Core Resources
With the IAM roles in place, we can now define the core resources for our ECS cluster. This includes the ECS cluster itself, the EC2 instances that will run our containers, and the necessary networking components.
This module creates the "office building" (ECS Cluster) and the "employees" (EC2 instances) that will run our FastAPI application.
> 💡 `infrastructure/modules/ecs-cluster/main.tf`, defines three critical components:
* **The ECS Cluster itself (the management service)**:
This is where our FastAPI application will live and be managed.
* **The EC2 Launch Template (the "onboarding instructions" for a new server)**:
This template provides the necessary instructions for launching new EC2 instances, including which IAM role to use.
* **The Auto Scaling Group (the "HR department" that hires and fires servers)**:
This group ensures that we always have the right number of EC2 instances running to handle our application's load.

  ## Phase 5b, Step 2 of 6: Define the ECS Cluster's Security
Now that we have the blueprints for the servers, we need to create their "key card access" system, or Security Groups. This file acts as a virtual firewall for the EC2 instances that will run your application.
We will define two main rules:
1. **Security Group for the EC2 Instances** -> Allow inbound traffic from the ALB: Only the "front door" (our load balancer) should be allowed to talk to our application "employees" (the EC2 instances).
2. **Inbound Rule: Allow traffic from the ALB** -> Create an egress (outbound) rule to the RDS security group: The "employees" need access to the "secure vault" (the RDS database).

> 💡 `infrastructure/modules/ecs-cluster/security-groups.tf` creates the necessary security groups and rules to ensure secure communication between the ALB, EC2 instances, and RDS database.

## Phase 5b, Step 3 of 6: Define the ECS Task Definition
This file tells ECS everything it needs to know to run your container: the Docker image to use, the CPU/memory to allocate, the ports to open, and crucially, how to securely inject all the environment variables (like the database password) from AWS Secrets Manager.
During Deployment, before the container starts, an ECS Agent on the EC2 instance will reach out to AWS Secrets Manager, fetch the secrets, and inject them into the container as environment variables. This way, your sensitive information is never hardcoded into the container image or exposed in your codebase.
> 💡 `infrastructure/modules/ecs-cluster/task-definition.tf` defines the "job description" for your FastAPI application container, including:
> * The IAM role that the task will assume (ecs_task_role)
> * The Docker image to use (from ECR)
> * The CPU and memory requirements
> * The port mappings
> * The environment variables, securely pulled from AWS Secrets Manager
> * The logging configuration to send logs to CloudWatch

## Phase 5b, Step 4 of 6: Define the ECS Service
This file acts as the "project manager" that ensures your FastAPI application is always running and healthy. It uses the task definition we just created to know what to run and how to run it.
> 💡 `infrastructure/modules/ecs-cluster/ecs-service.tf` defines the ECS service, which includes:
> * The desired number of task instances (how many copies of your application to run)
> * The load balancer configuration to distribute traffic
> * The deployment strategy to ensure zero downtime during updates

## Phase 5b, Step 5 of 6: Define the Module's Variables
This file acts as the "settings panel" for our ECS cluster module. It defines all the configurable options that can be passed in when the module is called.
> 💡 `infrastructure/modules/ecs-cluster/variables.tf` defines the input variables for the ECS cluster module, including:
> * VPC ID and Subnet IDs (from the networking module)
> * IAM Role ARNs (from the global module)
> * ECS Cluster Name (a unique name for the cluster)
> * EC2 Instance Type and Key Pair Name (for SSH access)
> * Desired Task Count (number of application instances to run)
> * Container Port and Load Balancer ARN (for traffic routing)

## Phase 5b, Step 6 of 6: Define the Module's Outputs
This file acts as the "connection points" for our ECS cluster module. It defines what information will be outputted after the module is applied, which can be used by other modules or environments.
> 💡 `infrastructure/modules/ecs-cluster/outputs.tf` defines the output values for the ECS cluster module, including:
> * The ECS Cluster name

---
## Phase 5c, Step 1 of 3: Update the `main.tf` to Include the ECS Cluster Module
Now we call our newly created ECS cluster module from the `infrastructure/environments/dev/main.tf` file. This is where we bring everything together and define how our application will be deployed.
> 💡 Update `infrastructure/environments/dev/main.tf` to include the ECS cluster module

## Phase 5c, Step 2 of 3: Update the `variables.tf` to Include the Necessary Variables
We need to ensure that our `infrastructure/environments/dev/variables.tf` file includes all the necessary variables that our ECS cluster module requires.
> 💡 Update `infrastructure/environments/dev/variables.tf` to include the necessary variables for the ECS cluster module:
> * `instance_type`: The type of EC2 instance to use (t2.micro for free tier) 
> * `min_size`, `max_size`, `desired_capacity`: The scaling parameters for the Auto Scaling Group
> * `ec2_key_name`: The name of the EC2 Key Pair for SSH access
> * `container_port`: The port on which the FastAPI application will listen (8080 to match our Dockerfile)

## Phase 5c, Step 3 of 3: Update the `outputs.tf` to Include Outputs from the ECS Cluster Module
If the deployment is succesful we will receive the application URL to access the FastAPI application.
> 💡 Update `infrastructure/environments/dev/outputs.tf` to obtain the `application url` from the ECS cluster module:``

