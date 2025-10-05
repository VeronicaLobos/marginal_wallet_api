# This file defines the security groups (firewalls) for the EC2 instances that
# will host our application containers.

# 1. Security Group for the EC2 Instances
resource "aws_security_group" "ecs_instance" {
  name        = "${var.project_name}-${var.environment}-ecs-instance-sg"
  description = "Allows inbound traffic from the ALB and outbound to the internet"
  vpc_id      = var.vpc_id

  # Allow all outbound traffic so the instance can pull updates and Docker images.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-${var.environment}-ecs-instance-sg"
    Project = var.project_name
  }
}

# 2. Inbound Rule: Allow traffic from the ALB
# This rule allows our load balancer to forward HTTP requests to the EC2 instances.
# It uses the ALB's security group ID to ensure only the ALB can connect.
resource "aws_security_group_rule" "ingress_from_alb" {
  type                     = "ingress"
  from_port                = 0 # Allows traffic on any port from the source
  to_port                  = 0
  protocol                 = "tcp"
  source_security_group_id = var.alb_security_group_id
  security_group_id        = aws_security_group.ecs_instance.id
}

# 3. Outbound Rule: Allow traffic to the Database
# This rule allows our application containers to connect to the PostgreSQL
# database on port 5432.
resource "aws_security_group_rule" "egress_to_rds" {
  type                     = "egress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  destination_security_group_id = var.rds_security_group_id
  security_group_id        = aws_security_group.ecs_instance.id
}

