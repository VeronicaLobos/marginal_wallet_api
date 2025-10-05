# This file defines the core compute infrastructure: the ECS cluster, the
# launch template for our EC2 instances, and the Auto Scaling Group that
# manages those instances.

# 1. The ECS Cluster Resource
# This is the logical grouping for our containers and services.
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  tags = {
    Name    = "${var.project_name}-${var.environment}-cluster"
    Project = var.project_name
  }
}

# 2. The EC2 Launch Template
# This is a blueprint that defines exactly how to configure the EC2 virtual
# servers that will run our Docker containers.
resource "aws_launch_template" "ecs_instances" {
  name_prefix            = "${var.project_name}-${var.environment}-"
  image_id               = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.ec2_key_name
  vpc_security_group_ids = [aws_security_group.ecs_instance.id]

  # This is a critical part: the user_data script. This script runs automatically
  # when a new EC2 instance starts up. It tells the instance which ECS cluster
  # to join.
  user_data = base64encode(<<-EOF
              #!/bin/bash
              echo ECS_CLUSTER=${aws_ecs_cluster.main.name} >> /etc/ecs/ecs.config
              EOF
  )

  # Attach the IAM role that allows the instance to join the cluster.
  iam_instance_profile {
    name = var.ecs_instance_profile_name
  }

  tags = {
    Name    = "${var.project_name}-${var.environment}-ecs-instance"
    Project = var.project_name
  }
}

# 3. The Auto Scaling Group (ASG)
# This is the "HR department." It ensures that we always have the desired
# number of EC2 instances running, based on the Launch Template. If an
# instance fails, the ASG will automatically terminate it and launch a new one.
resource "aws_autoscaling_group" "ecs_cluster" {
  name_prefix = "${var.project_name}-${var.environment}-asg-"
  min_size    = var.min_size
  max_size    = var.max_size
  desired_capacity = var.desired_capacity

  vpc_zone_identifier = var.private_subnet_ids

  launch_template {
    id      = aws_launch_template.ecs_instances.id
    version = "$Latest"
  }

  # This tag is required so that the ECS cluster can discover and manage
  # the instances created by this ASG.
  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }
}

