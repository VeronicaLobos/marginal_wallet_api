# Infrastructure Components Overview

## 1. The Foundation: The Network (VPC Module)

* **What it is:** The "building." This was the very first thing Terraform created. It's your secure, private section of the AWS cloud.
* **How it connects:** It doesn't connect to anything; everything else connects *to it*. It provides the `vpc_id` and the lists of `public_subnet_ids` and `private_subnet_ids` that all other modules need.

## 2. The Shared Services: The "ID Cards" & "Lockboxes" (Global Module)

* **What it is:** The IAM Roles and the empty AWS Secrets Manager secrets.
* **How it connects:** These resources were created next. They don't depend on anything, but many other resources will depend on them. Think of this as the "central services office" for your building, preparing the security credentials and empty lockboxes before the employees arrive.

## 3. The Data Layer: The Database (RDS Module)

* **What it is:** The "secure vault." A fully managed PostgreSQL database.
* **How it connects:** Terraform placed this *inside* the `private_subnet_ids` provided by the VPC module. It also created its own firewall (`rds_security_group_id`) and a secure "lockbox" for its connection URL (`db_url_secret_arn`).

## 4. The Artifact Store: The Container Registry (ECR Module)

* **What it is:** The "private warehouse" for your Docker images.
* **How it connects:** This is a simple, standalone resource. Its main purpose is to provide its `repository_url` to the ECS module.

## 5. The Public Entrypoint: The Load Balancer (ALB Module)

* **What it is:** The "smart front door" and "receptionist" for your application.
* **How it connects:** Terraform placed this *inside* the `public_subnet_ids` from the VPC module. It created a "target group," which is like an empty waiting room where the receptionist will send visitors.

## 6. The Grand Finale: The Compute Layer (ECS Cluster Module)

* **What it is:** The "office space and employees." This was the final and most complex part, and it's what connects everything together.
* **How it connects (The Final Wiring):**
   * It built the **EC2 Instances** ("employees") and placed them inside the `private_subnet_ids`.
   * It gave each EC2 instance an "ID card" (`ecs_instance_profile_name`) from the `global` module, allowing them to join the cluster.
   * It created a "job description" (**Task Definition**) that references:
      * The `ecr_repository_url` (where to get the application code).
      * All the secret ARNs from the `global` and `rds` modules (where to get the passwords and API keys).
      * The `ecs_task_role_arn` (the "ID card" for the application itself).
   * Finally, it created the "project manager" (**ECS Service**), which launched your container and connected it to the `target_group_arn` of the ALB, telling the "receptionist" where to send traffic.