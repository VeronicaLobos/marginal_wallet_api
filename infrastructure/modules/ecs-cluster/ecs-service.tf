# This file defines the ECS Service, which is the "project manager" responsible
# for running and maintaining our application tasks based on the Task Definition.

resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = var.ecs_cluster_id
  task_definition = var.ecs_task_definition_arn
  desired_count   = var.desired_capacity # How many instances of our container to run
  launch_type     = "EC2"

  # This block tells the service to connect to our Application Load Balancer.
  # It ensures that as new tasks are launched, they are automatically registered
  # with the ALB to start receiving traffic.
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-${var.environment}-container"
    container_port   = 8080
  }

  # This helps prevent issues during deployment where old tasks might not
  # deregister correctly.
  depends_on = [var.alb_listener]

  tags = {
    Name    = "${var.project_name}-${var.environment}-service"
    Project = var.project_name
  }
}

