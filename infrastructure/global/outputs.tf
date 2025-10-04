# This file exports the ARNs (Amazon Resource Names) of the IAM roles
# created in iam.tf, so they can be used by other modules.

output "ecs_task_execution_role_arn" {
  description = "The ARN of the IAM role that allows ECS to manage resources."
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "The ARN of the IAM role for the application running in the task."
  value       = aws_iam_role.ecs_task_role.arn
}
