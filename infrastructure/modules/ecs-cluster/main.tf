# This file defines the core components of the ECS Cluster using EC2 instances.

# 1. The ECS Cluster itself
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }
}

# 2. The Launch Template for EC2 Instances
# This is the "onboarding manual" for new servers, telling them what OS to use,
# what role to assume, and what startup script to run.
resource "aws_launch_template" "main" {
  name_prefix            = "${var.project_name}-${var.environment}-"
  image_id               = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.ec2_key_name
  vpc_security_group_ids = [aws_security_group.ecs_instance.id]

  iam_instance_profile {
    name = var.ecs_instance_profile_name
  }

  # This user_data script is crucial. It runs when the EC2 instance first starts.
  # It tells the instance which ECS cluster to join.
  user_data = base64encode(<<-EOF
              #!/bin/bash
              echo ECS_CLUSTER=${aws_ecs_cluster.main.name} >> /etc/ecs/ecs.config
              EOF
  )

  tags = {
    Name = "${var.project_name}-${var.environment}-launch-template"
  }
}

# 3. The Auto Scaling Group (ASG)
# This is the "HR department" that ensures we have the correct number of EC2
# instances running, based on the launch template.
resource "aws_autoscaling_group" "main" {
  name_prefix         = "${var.project_name}-${var.environment}-asg"
  vpc_zone_identifier = var.private_subnet_ids

  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }

  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity

  tag {
    key                 = "Name"
    value               = "${var.project_name}-${var.environment}-ecs-instance"
    propagate_at_launch = true
  }

  # NOTE: The incorrect depends_on block has been removed from here.
}

# 4. Capacity Provider
# This tells the ECS cluster that it can use the servers from our Auto Scaling
# Group to place application containers.
resource "aws_ecs_capacity_provider" "main" {
  name = "${var.project_name}-${var.environment}-cp"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.main.arn
    managed_scaling {
      status          = "ENABLED"
      target_capacity = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = [aws_ecs_capacity_provider.main.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.main.name
  }
}
