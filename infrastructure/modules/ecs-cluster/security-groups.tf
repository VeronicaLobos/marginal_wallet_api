# This file defines the "key card access" (Security Groups) for the EC2 instances.

# 1. Security Group for the EC2 Instances themselves
resource "aws_security_group" "ecs_instance" {
  name        = "${var.project_name}-${var.environment}-ecs-instance-sg"
  description = "Security group for the ECS EC2 instances"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-instance-sg"
  }
}

# 2. Ingress (Inbound) Rule: Allow traffic from the ALB
# This allows our public "front door" to send requests to our application "employees".
resource "aws_security_group_rule" "ingress_from_alb" {
  type                     = "ingress"
  from_port                = 0 # Allow any port
  to_port                  = 0
  protocol                 = "-1" # Allow any protocol
  security_group_id        = aws_security_group.ecs_instance.id
  source_security_group_id = var.alb_security_group_id
  description              = "Allow all traffic from the ALB"
}

# 3. Egress (Outbound) Rule: Allow all outbound traffic to the internet.
# This is needed so the instances can pull the ECS agent and Docker images.
resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.ecs_instance.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound traffic"
}

# 4. Egress (Outbound) Rule: Allow traffic to the RDS database.
# This allows our application "employees" to talk to the "secure vault" (the database).
resource "aws_security_group_rule" "egress_to_rds" {
  type                          = "egress"
  from_port                     = 5432
  to_port                       = 5432
  protocol                      = "tcp"
  security_group_id             = aws_security_group.ecs_instance.id
  source_security_group_id      = var.rds_security_group_id
  description                   = "Allow outbound traffic to the RDS instance"
}

