# This file defines the outputs for the dev environment. After a successful
# 'apply', Terraform will print these values to the console.

output "application_url" {
  description = "The public URL of the Application Load Balancer."
  value       = "http://${module.alb.alb_dns_name}"
}
