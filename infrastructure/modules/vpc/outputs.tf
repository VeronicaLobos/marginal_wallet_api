# /infrastructure/modules/vpc/outputs.tf

# This file defines the "outputs" of our VPC module. These are values that
# other modules will need to use. For example, the RDS and ECS modules will need
# to know the IDs of the VPC and subnets to place resources inside them.

output "vpc_id" {
  description = "The ID of the VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "A list of the public subnet IDs."
  value       = aws_subnet.public.*.id
}

output "private_subnet_ids" {
  description = "A list of the private subnet IDs."
  value       = aws_subnet.private.*.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC."
  value       = aws_vpc.main.cidr_block
}
