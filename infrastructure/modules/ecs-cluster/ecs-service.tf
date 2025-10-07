# This file defines the "project manager" (ECS Service) that keeps your
# application running.

resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_capacity
  launch_type     = "EC2"

  # This block tells the service where to place the tasks on the network.
  # It is required when using the 'awsvpc' network mode.
  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.ecs_instance.id]
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-${var.environment}-container"
    container_port   = 8080 # The port inside the container
  }

  # This ensures the service doesn't try to start until the ALB is ready.
  depends_on = [var.alb_listener]
}
