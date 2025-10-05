# /infrastructure/modules/alb/outputs.tf

output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "The ARN of the main target group."
  value       = aws_lb_target_group.main.arn
}

output "alb_security_group_id" {
  description = "The ID of the security group attached to the ALB."
  value       = aws_security_group.alb.id
}

output "alb_listener" {
  description = "The ARN of the ALB listener."
  value       = aws_lb_listener.http.arn
}



