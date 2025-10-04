Terraform is my Infrastructure as Code (IaC) tool. It lets me define my entire cloud setup in readable, version-controlled files.

The VPC module acts as the foundational blueprint for a secure, private network—the "building" where my application will live.

The RDS module places a secure, managed database inside the "private rooms" (subnets) of that building, with no direct internet access.

The S3 State Bucket is my remote, shared storage for Terraform's state file (the "master blueprint"). The DynamoDB Table provides a locking mechanism to prevent concurrent modifications to the infrastructure, which is critical for both team collaboration and CI/CD automation.

The S3 Module will create a separate bucket for application assets like user images, which will be served to clients.

The ALB (Application Load Balancer) will act as the public-facing "smart front door," securely routing internet traffic to the application.

The ECS Cluster will be the "application management service," running my Docker containers on a fleet of EC2 instances (the "employees") inside the private subnets.