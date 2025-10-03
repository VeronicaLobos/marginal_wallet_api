# Resources Created by Terraform in the VPC Module

* aws_vpc.main (1 resource)

What it is: The Virtual Private Cloud (VPC).

Analogy: This is the plot of land for your house. It's a completely isolated and private section of the AWS cloud that belongs only to you. All your other resources will be built inside this VPC.

* aws_subnet.public (2 resources)

What it is: Two public subnets, one in each availability zone (us-east-1a and us-east-1b).

Analogy: These are the rooms in your house that have windows and doors to the outside world, like a foyer or a living room. We will place resources here that need to be accessible from the internet, like our load balancer. Creating two provides high availability in case one of AWS's data centers has an issue.

* aws_subnet.private (2 resources)

What it is: Two private subnets, one in each availability zone.

Analogy: These are the secure, windowless rooms in the center of your house, like a safe or a pantry. We will place our secure resources here, like the database, which should never be directly exposed to the internet.

* aws_internet_gateway.main (1 resource)

What it is: The Internet Gateway (IGW).

Analogy: This is the single front door to your entire property. It's attached to the VPC and is the only way traffic can get from the internet into your network.

* aws_route_table.public (1 resource)

What it is: The public route table.

Analogy: This is the "GPS" or the set of directions for your public rooms. It has one simple rule: "To get to the outside world (any address 0.0.0.0/0), go through the front door (the Internet Gateway)."

* aws_route_table_association.public (2 resources)

What it is: Two route table associations.

Analogy: This is the "glue" that puts the directions (the route table) inside your public rooms (the subnets). It explicitly links the public route table to each of the public subnets, giving them a path to the internet.