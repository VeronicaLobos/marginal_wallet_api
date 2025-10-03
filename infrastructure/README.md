# Marginal Wallet API - AWS Infrastructure with Terraform

This document summarizes the foundational steps taken to build the AWS infrastructure for the Marginal Wallet API using Terraform.

## Phase 0: Local Setup (Prerequisites)
** Goal **: Prepare the local machine for infrastructure development.
Why: We need the necessary tools (terraform, aws cli) installed and authenticated to communicate with our AWS account.
How:
- Installed Terraform using Homebrew.
- Installed the AWS CLI using Homebrew.
- Ran aws configure to securely store AWS credentials locally, allowing the CLI to act on our behalf.
Outcome: A local development environment capable of managing AWS resources via code.

## Phase 1: Terraform Project Foundation

** Goal **: Create a professional, scalable project structure and configure Terraform's remote state.
Why:
Structure: Separating code into modules (reusable blueprints) and environments (specific deployments) is a best practice that keeps code organized and avoids repetition.
Remote State: Storing the terraform.tfstate file (Terraform's "memory") in an S3 bucket is critical. It prevents state loss if your local machine fails and allows for collaboration (including with a CI/CD pipeline). The DynamoDB table acts as a "lock" to prevent multiple people or processes from making changes at the same time, which prevents corruption.
How:
- Created the infrastructure/ directory structure.
- Defined a backend.tf file in environments/dev to point Terraform to our S3 bucket and DynamoDB table.
- Manually created the S3 bucket and DynamoDB table using the AWS CLI. This is a one-time bootstrapping step because these resources must exist before Terraform can use them.
- Ran terraform init to connect Terraform to this remote backend and download the AWS provider plugin.
Outcome: A fully initialized Terraform project with a secure, remote state backend.

## Phase 2: Building the Network (VPC Module)

** Goal **: Create a secure and isolated virtual network to house all our application resources.
Why: A VPC is the foundational security boundary in AWS. By creating public subnets (for internet-facing resources like a load balancer) and private subnets (for secure resources like our database), we follow the principle of least privilege and protect our sensitive data.
How:
- We wrote our first reusable module in infrastructure/modules/vpc/.
- Inside main.tf, we defined resources like aws_vpc, aws_subnet, aws_internet_gateway, and aws_route_table.
- We used the module "vpc" block in environments/dev/main.tf to call our new module.
- We ran terraform plan to see a preview and terraform apply to build the 9 network resources in AWS.
Outcome: A live, highly-available, multi-zone network in AWS, ready to host our application.

## Phase 3: Building the Database (RDS Module)

** Goal **: Provision a managed PostgreSQL database inside our secure network.
Why: Using a managed service like Amazon RDS frees us from the responsibility of patching, backups, and managing the database server. Placing it in the private subnets ensures it is not exposed to the public internet, dramatically improving security.
How:
- We created a new reusable module in infrastructure/modules/rds/.
- Inside main.tf, we defined aws_db_instance, aws_db_subnet_group, and aws_security_group.
- Crucially, in environments/dev/main.tf, we passed outputs from the VPC module (like module.vpc.private_subnet_ids) as inputs to the RDS module. This is the core concept of modular IaC—connecting independent components together.
- We ran terraform plan and terraform apply to build the 3 database resources in AWS.
Outcome: A live, running, secure PostgreSQL database instance within our private network.

## Phase 4: Create a Home for Your Docker Image (ECR)

** What is it? ** We will create an Amazon ECR (Elastic Container Registry).

Why do we need it? ECR is AWS's private version of Docker Hub. It's a secure, fast, and highly-available place to store your application's Docker images. Using ECR is a best practice when deploying to AWS because it integrates seamlessly and securely with the container service (ECS).

What we will do: We'll add a new ecr Terraform module to create this private registry.

## Phase 5: Build the Application's "House" (ECS + ALB)

This is the most significant phase where we build the compute layer that will actually run your application.

** What is it? ** We will build two main components:

An Application Load Balancer (ALB).

An Elastic Container Service (ECS) Cluster running on EC2 instances.

Why do we need it?

The ALB will be our application's public entry point. It will live in your public subnets, accept incoming internet traffic (HTTP/HTTPS), and intelligently forward it to your running application containers. It's the "traffic cop."

The ECS Cluster is the "brain" that manages your Docker containers. We'll tell it to run your application on a fleet of small EC2 virtual servers that live securely in your private subnets. ECS will handle starting your containers, monitoring their health, and replacing them if they crash.

What we will do: We will create two new, more complex Terraform modules (alb and ecs-cluster) and call them from our dev environment, connecting them to the VPC and RDS database we've already defined.

Here is a high-level diagram of the final architecture we are building.

## Phase 6: Automate Everything (The AWS CI/CD Pipeline)

** What is it? ** We will create a new GitHub Actions workflow file, cicd-aws.yml.

Why do we need it? This is the final step that automates the entire process. Just like your Google Cloud pipeline, this new workflow will trigger every time you push to the main branch.

What it will do:

Run all the CI checks (tests, style, security).

If they pass, it will log in to AWS and ECR.

It will build a new Docker image of your application and push it to your ECR repository.

Finally, it will run terraform apply. Terraform will see that a new image has been pushed to ECR and will automatically deploy it to your ECS service with zero downtime.