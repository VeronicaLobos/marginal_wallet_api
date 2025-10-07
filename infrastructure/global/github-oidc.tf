# OIDC Provider for GitHub Actions
resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1"
  ]
}

# IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "github-actions-deployment-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:VeronicaLobos/marginal_wallet_api:*"
          }
        }
      }
    ]
  })
}

# Attach necessary policies
resource "aws_iam_role_policy_attachment" "github_actions_ecr" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy_attachment" "github_actions_ecs" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
  description = "ARN of the IAM role for GitHub Actions"
}

# Policy for Terraform state in S3
resource "aws_iam_policy" "github_actions_terraform_state" {
  name        = "github-actions-terraform-state-access"
  description = "Allow GitHub Actions to access Terraform state in S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::marginal-wallet-api-tfstate-veronica/environments/dev/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = "arn:aws:s3:::marginal-wallet-api-tfstate-veronica"
      }
    ]
  })
}

# Attach the S3 policy to the GitHub Actions role
resource "aws_iam_role_policy_attachment" "github_actions_terraform_state" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_terraform_state.arn
}

# Policy for DynamoDB state locking
resource "aws_iam_policy" "github_actions_dynamodb_lock" {
  name        = "github-actions-dynamodb-lock-access"
  description = "Allow GitHub Actions to use DynamoDB for Terraform state locking"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:us-east-1:198961800007:table/marginal-wallet-api-tfstate-lock"
      }
    ]
  })
}

# Attach the DynamoDB policy
resource "aws_iam_role_policy_attachment" "github_actions_dynamodb_lock" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions_dynamodb_lock.arn
}