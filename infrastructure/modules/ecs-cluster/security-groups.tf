# This file defines the "key card access" (Security Groups) for the EC2 instances.
# This version uses inline ingress/egress rules, which is a more robust pattern.

resource "aws_security_group" "ecs_instance" {
  name        = "${var.project_name}-${var.environment}-ecs-instance-sg"
  description = "Security group for the ECS EC2 instances"
  vpc_id      = var.vpc_id

  # Ingress (Inbound) Rule: Allow traffic FROM the ALB.
  # This allows our public "front door" to send requests to our application.
  ingress {
    from_port       = 0 # Allow any port
    to_port         = 0
    protocol        = "-1" # Allow any protocol
    security_groups = [var.alb_security_group_id] # CORRECTED: "security_groups" and expects a list
    description     = "Allow all traffic from the ALB"
  }

  # Egress (Outbound) Rule: Allow all outbound traffic to anywhere.
  # This is necessary for the EC2 instance to:
  # 1. Contact the ECS control plane to join the cluster.
  # 2. Pull the Docker image from the ECR repository.
  # 3. Connect to the RDS database (since its IP is within 0.0.0.0/0).
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-instance-sg"
  }
}

