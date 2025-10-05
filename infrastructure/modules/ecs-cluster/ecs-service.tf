# This file defines the "project manager" (ECS Service) that keeps your
# application running.

resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_capacity # Run one instance of our app
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-${var.environment}-container"
    container_port   = 8080 # The port inside the container
  }

  # This is important for zero-downtime deployments.
  # It also ensures the service doesn't try to start until the ALB is ready.
  depends_on = [var.alb_listener]
}

