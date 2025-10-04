The "ID Card" Analogy for ECS Roles

The Two ID Cards: Your application needs two different "ID cards" to do its job in the cloud.

Execution Role (The "Setup Crew" ID): This ID card gives the ECS service itself permission to do basic setup work, like pulling your Docker image from the ECR warehouse and sending logs to the logging service.

Task Role (The "Application" ID): This is the ID card your actual application code wears. If your FastAPI app needs to access an S3 bucket to save a user's avatar, you would add "S3 Access" permission to this specific ID card.

iam.tf (The "ID Card Office"): Your infrastructure/global/iam.tf file is the office where these ID cards are created. It defines what permissions each card has.

outputs.tf (The "Wallet"): The infrastructure/global/outputs.tf file is like a wallet where you put the newly created ID cards. It makes them easily accessible.

The ecs-cluster module (The "Employee"): Later, when we build the ECS Cluster module, it will reach into that global "wallet" (outputs.tf) and grab the correct ID cards to give to the "Setup Crew" and the "Application."