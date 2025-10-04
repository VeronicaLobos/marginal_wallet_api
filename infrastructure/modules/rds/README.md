# Resources created by Terraform in the RDS Module

* aws_db_instance.main (1 resource)

What it is: The managed PostgreSQL database instance (the "safe" where your data is stored).

Analogy: This is the "safe" in your secure room where all your important data is stored. It's a fully managed database server that handles backups, patching, and scaling for you. It lives in the private subnets, so it's not directly accessible from the internet, greatly enhancing security.
 
* aws_db_subnet_group.main (1 resource)

What it is: The DB subnet group (the "list of approved rooms" to install the safe).

The Analogy: Imagine you're telling a security guard where they are allowed to place a valuable safe. You don't just say "put it somewhere in the house." You give them a specific list of approved, secure, internal rooms.

The Explanation: A DB Subnet Group is exactly that: a list of approved private subnets. You are telling AWS, "When you create my RDS database, you are only allowed to place it within one of these specific subnets." This is a mandatory requirement for creating a database inside a VPC. It also ensures your database is highly available, as a subnet group must contain subnets in at least two different Availability Zones.

* aws_security_group.main (1 resource)

What it is: The security group for the database (the firewall or "lock" to protect the safe).

Analogy: This is the "lock" on your safe. It controls who can access the database and on which ports. In our case, we allow inbound traffic on port 5432 (the PostgreSQL port) only from resources within the VPC, ensuring that only trusted components can communicate with the database.