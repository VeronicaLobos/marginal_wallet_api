[![CI/CD Pipeline Status](https://github.com/VeronicaLobos/marginal_wallet_mvp/actions/workflows/cicd.yml/badge.svg)](https://github.com/VeronicaLobos/marginal_wallet_api/actions)

# Marginal Wallet API (Production-Ready)

**Live URL (Cloud):** https://marginal-wallet-api-774137592559.us-central1.run.app/

**MVP Presentation**: [View the Google Slides Presentation](https://docs.google.com/presentation/d/1msF1SwGYIN_q2wsHnYTRJqkjZpCoKzkPilyAUUZoiGw/)

Marginal Wallet is a robust RESTful API designed to help users manage their personal finances, with a focus on tracking non-fixed income and expenses. Built with Python and FastAPI, it provides a secure and feature-rich backend for a personal finance application.

This project was initially developed for a Software Engineering - Backend diploma (Masterschool's 14month program), and was later enhanced with professional DevOps and Cloud engineering practices learned during a 2 months internship at Webeet. It demonstrates a full development lifecycle from an initial MVP to a production-grade, automatically deployed application.

## Table of Contents

- [Database Schema](#database-schema)
- [Project Evolution](#project-evolution)
- [Tech Stack](#tech-stack)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Documentation](#api-documentation)
- [Getting Started: Local Development](#getting-started-local-development)
- [Running with Docker](#running-with-docker)
- [Code Quality & Testing](#code-quality--testing)
- [Automated Deployment to Google Cloud Run](#automated-deployment-to-google-cloud-run)
- [Automated Deployment to AWS (Terraform & ECS)](#automated-deployment-to-aws-(terraform--ecs))


## Database Schema
The database schema was designed using DBML (Database Markup Language) to model entities and their relationships. The live, interactive diagram can be viewed at the link below.

View the [Live Database Diagram](https://dbdiagram.io/d/Copy-of-expense_income_tracker-68dfb58dd2b621e42221f7f5) on dbdiagram.io

## Project Evolution

### Core Application Features (Diploma Project: MVP & V2)

This section covers the core features of the application itself.

- **Secure User Authentication:** Full user registration and login system using JWT (JSON Web Tokens) for secure, token-based authentication. Passwords are fully encrypted using bcrypt.

- **User & Data Management:** Full CRUD (Create, Read, Update, Delete) endpoints for managing user profiles, income/expense categories, financial transactions (movements), and planned expenses.

- **AI-Powered Financial Insights:** Integration with the Google Gemini API (gemini-1.5-flash) to provide users with an AI-generated natural language summary of their financial activity.

- **API Security:** Implemented rate limiting on sensitive endpoints to prevent abuse and brute-force attacks.

- **Templated Frontend:** A functional frontend prototype built with Jinja2 and Bootstrap to demonstrate the API's capabilities.

### Professional Enhancements (Internship Experience)

This section covers the professional DevOps, Security, and Cloud practices applied to the project.

- **End-to-End CI/CD Pipeline:** Automated the entire build, test, and deployment process using GitHub Actions. The pipeline ensures code quality and automatically deploys the application to Google Cloud Run.

- **Containerization:** The application and its environment are fully containerized using Docker and Docker Compose, ensuring consistency from local development to production.

- **Cloud-Native Deployment:** Deployed the containerized application to Google Cloud Run, a modern serverless platform. This includes automated database migrations against a Google Cloud SQL (PostgreSQL) production database.

- **Automated Quality Gates:**
  - **Unit Testing:** A comprehensive test suite using pytest is run automatically on every commit.
  - **Code Formatting:** Code style is enforced automatically using black.
  - **Security Scanning:** The codebase is scanned for common vulnerabilities using bandit.
  - **Pre-Commit Hooks:** A local Git pre-commit hook runs pytest before every commit, preventing broken code from entering the repository.

## Tech Stack

| Component | Technology & Notes                                                                                                                                                           |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Backend** | `Python 3.12`, `FastAPI`. Served by `Uvicorn` for development and managed by `Gunicorn` with Uvicorn workers for production, providing a robust, multi-process architecture. |
| **Database** | `PostgreSQL` for reliable relational data storage.                                                                                                                           |
| **ORM & Data** | `SQLModel` built on SQLAlchemy V2 and `Pydantic` for type-safe models and data validation.                                                                                   |
| **IaC & Cloud** | `Terraform`, `AWS (ECS, RDS, VPC, ALB, ECR)`, `Google Cloud (Cloud Run, Cloud SQL)`                                                                                             |
| **Modeling & Design** | `DBML` (dbdiagram.io) for database schema design and visualization.                                                                                                          |
| **Migrations** | `Alembic` for managing database schema evolution.                                                                                                                            |
| **Authentication** | `JWT` (PyJWT) and `OAuth2`, with `Passlib (bcrypt)` for password hashing.                                                                                                    |
| **AI Integration** | `Google Gemini API` for generating financial insights.                                                                                                                       |
| **Testing** | `Pytest` for unit testing and `Bandit` for security scanning.                                                                                                                |
| **Formatting** | `Black` for opinionated, consistent code formatting.                                                                                                                         |
| **Containerization** | `Docker` and `Docker Compose` for portable application environments.                                                                                                         |
| **CI/CD** | `GitHub Actions` for automating the entire testing and deployment workflow.                                                                                                  |
| **Frontend** | `Jinja2` Templating with `Bootstrap` and JavaScript` for a responsive UI prototype. Prototyped with `Gemini CLI`.                                                             |

## CI/CD Pipeline

This project utilizes a full CI/CD pipeline managed by GitHub Actions to automate testing and deployment.

### Continuous Integration (CI)

Runs on every push and pull request to the main branch.

- Run Unit Tests: Executes the pytest suite against a dedicated SQLite database.
- Check Code Style: Uses black to verify consistent code formatting.
- Run Security Scan: Uses bandit to analyze the codebase for common vulnerabilities.

### Continuous Deployment (CD)

Runs only on a push/merge to the main branch after all CI jobs pass.

- Authenticates with Google Cloud and Docker Hub.
- Builds and pushes a new Docker image to Docker Hub.
- Connects to the production database and applies alembic migrations.
- Deploys the new image to Google Cloud Run, updating the live service.

## API Documentation

Interactive API documentation is available via Swagger UI.

- **Local Swagger UI:** http://localhost:8000/docs
- **Live Swagger UI:** https://marginal-wallet-api-774137592559.us-central1.run.app/docs

## Getting Started: Local Development

### 1. Prerequisites

- Python 3.12+
- PostgreSQL installed and running
- Docker and Docker Compose (Optional)

### 2. Clone the Repository

```bash
git clone git@github.com:VeronicaLobos/marginal-wallet-api.git
cd marginal-wallet-api
```

### 3. Environment and Dependencies

```bash
# Create and activate a virtual environment
python3 -m venv env
source env/bin/activate

# Install all packages (production + development)
pip install -r requirements-dev.txt
```

### 4. Database and Environment Configuration

#### Create the PostgreSQL Database

If psql is not in your PATH, you may need to add it first (e.g., `export PATH="/Library/PostgreSQL/17/bin:$PATH"` on macOS).

```bash
# Connect as the postgres superuser
psql -U postgres
```

Inside the psql shell:

```sql
-- Drop the database if it exists from a previous run
DROP DATABASE IF EXISTS "marginal-wallet";

-- Create the clean database
CREATE DATABASE "marginal-wallet";

-- Exit the psql shell
\q
```

#### Configure Environment Variables

Create a `.env` file in the project root with the following content, filling in your details:

```env
# For local development (uvicorn)
DATABASE_URL="postgresql://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@localhost:5432/marginal-wallet"

# General Settings
SECRET_KEY="a-strong-and-random-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_API_KEY="your-google-api-key-here"
```

**Note:** Obtain a `GOOGLE_API_KEY` from Google AI Studio.

### 5. Run Database Migrations

Apply all migrations to set up your schema:

```bash
alembic upgrade head
```

### 6. Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

## Running with Docker

Configure your `.env` file to point to your host machine's database. `host.docker.internal` is a special DNS name that lets the container connect to services on your computer.

```env
# For Docker container connecting to a local host DB
DATABASE_URL="postgresql://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@host.docker.internal:5432/marginal-wallet"
```

Then, build and run the container:

```bash
docker-compose up --build
```

**Note on Ports:** The `compose.yaml` file maps port 8000 on your local machine to port 8080 inside the container. The application listens on the `$PORT` environment variable (defaulting to 8080), a best practice for compatibility with cloud platforms like Google Cloud Run.

## Code Quality & Testing

All development tools are listed in `requirements-dev.txt`.

**Unit Tests (pytest):**

```bash
pytest
```

**Code Formatting (black):**

```bash
# Check for formatting issues
black --check .

# Automatically reformat files
black .
```

**Security Scanning (bandit):**

```bash
bandit -r . -x ./env,./tests
```

## Automated Deployment to Google Cloud Run

### 1. Prerequisites

- A Google Cloud Platform (GCP) account with billing enabled.
- A Docker Hub account.

### 2. Google Cloud Setup

#### Create a Google Cloud Project

- Go to the Google Cloud Console and sign in.
- In the top menu bar, click the project selector dropdown and then click New Project.
- Give your project a unique name (e.g., marginal-wallet-production) and link a billing account.

#### Enable APIs

In your new GCP project, enable the following APIs:

- Cloud Run Admin API
- Cloud SQL Admin API
- Compute Engine API

#### Create a PostgreSQL Instance (Cloud SQL)

- Create a new PostgreSQL 17 instance.
- Set a strong password for the postgres user and save it.
- Under Connections, enable Public IP and add 0.0.0.0/0 as an authorized network.
- After the instance is created, go to its Databases tab and create a new database named exactly `marginal-wallet`.

#### Create a Service Account for Deployment

- Go to IAM & Admin → Service Accounts and create a new account (e.g., github-actions-deployer).
- Grant it the role Cloud Run Admin.
- Go to the IAM main page, find the Compute Engine default service account (`<PROJECT_NUMBER>-compute@...`), and grant your github-actions-deployer account the Service Account User role on it.
- Create and download a JSON key for your github-actions-deployer service account.

### Managing Costs (Important!)

To avoid incurring charges, the Cloud SQL instance should be stopped when not in use.

⚠️ **Important**: The deployment pipeline will fail if the Cloud SQL instance is stopped. Remember to start it before pushing changes to the main branch.

**To Stop (via GUI):**

- Go to the Cloud SQL Instances page.
- Check the box next to your instance.
- Click the STOP button that appears in the top menu bar.

**To Stop/Start (via CLI):**

```bash
# To stop the instance
gcloud sql instances patch INSTANCE_ID --activation-policy NEVER

# To start the instance
gcloud sql instances patch INSTANCE_ID --activation-policy ALWAYS
```

**Note:** The Cloud Run service itself scales to zero automatically and incurs no cost when idle. You only need to manage the database instance.

### 3. GitHub Repository Configuration

Navigate to your repository's Settings → Secrets and variables → Actions and add the following secrets:

| Secret Name | Description |
|-------------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username. |
| `DOCKERHUB_TOKEN` | A Docker Hub Access Token. |
| `GCP_PROJECT_ID` | The ID of your Google Cloud project. |
| `GCP_SA_KEY` | The full content of the downloaded Service Account JSON key file. |
| `PROD_DATABASE_URL` | The connection string for your Cloud SQL database: `postgresql://postgres:YOUR_DB_PASSWORD@DB_PUBLIC_IP/marginal-wallet` |
| `SECRET_KEY` | Your application's secret key for JWT signing. |
| `ALGORITHM` | The JWT algorithm (e.g., `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | The token expiration time (e.g., `30`). |
| `GOOGLE_API_KEY` | Your API key for the Google Gemini service. |

### 4. Trigger Deployment

The deployment workflow will run automatically on every push or merge to the main branch.

---

## Automated Deployment to AWS (Terraform & ECS)
This section guides you through deploying the application to AWS using the Terraform configurations located in the `/infrastructure` directory.

### Phase 0 - Local Setup
Prerequisites (MacOS):
- A free tier AWS account with programmatic access (Access Key ID and Secret Access Key)
- Homebrew installed
- Terraform (≥ 1.0.0) installed
- AWS CLI installed and configured with your credentials

 · Install Terraform on macOS
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform -v
```
You should see the Terraform version number printed.

 · Install and Configure the AWS CLI
```bash
brew install awscli
aws --version
# Configure the AWS CLI with your credentials
aws configure
```
When prompted, enter your credentials:
- AWS Access Key ID and AWS Secret Access Key:  
Go to your AWS Console, click on your **account name in the top right -> Security credentials -> Access keys -> Create access key**. Choose "Command Line Interface (CLI)". Save the Key and Secret Key somewhere safe! You only get to see the secret key once.
- Default region name: Enter `us-east-1` (or your preferred region).
- Default output format: You can just press Enter (it will default to `json`).

To verify your configuration, run:
```bash
aws sts get-caller-identity
```
You should see your AWS account details.

### Phase 0 - Setting Up the Terraform Project Structure
 · Project Structure
The Terraform configurations are organized into a modular structure to promote reusability and maintainability.
- `infrastructure/global`: Contains resources shared across all environments, such as the S3 bucket and DynamoDB table for Terraform state management.
- `infrastructure/environment/dev`: Contains resources specific to the development environment, such as VPCs, ECS clusters, and RDS instances.
- `infrastructure/modules`: Contains reusable Terraform modules for common components like VPCs, ECS services, and RDS databases.

 · Create S3 bucket and DynamoDB table for Terraform remote state
Terraform needs a remote place to store its "state" file. You must create an S3 bucket and a DynamoDB table for this manually one time before running any Terraform commands.
```bash
# Navigate to the global directory
cd ../global
# Create the S3 bucket (use your unique name)
aws s3api create-bucket \
    --bucket marginal-wallet-api-tfstate-veronica \
    --region us-east-1
# Create the DynamoDB table for state locking
aws dynamodb create-table \
    --table-name terraform-lock \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

 · Running Terraform
All Terraform commands should be run from the development environment directory.

* Initialize Terraform
```bash
# Navigate back to the dev environment directory
cd ../environment/dev
# Initialize Terraform with the remote backend configuration
terraform init
```
This command downloads the AWS provider and connects to the S3 remote state backend you just created.

* Plan the Infrastructure
```bash
terraform plan
```
This command shows you what resources Terraform will create, change, or destroy. It's a dry run.

* Apply the Infrastructure
```bash
terraform apply --auto-approve
```
This command builds the infrastructure defined in the code.

### Phase 1 - Building the Network (VPC Module).
The VPC module creates a Virtual Private Cloud (VPC) with:
- A Virtual Private Cloud (VPC)
- Public subnets (load balancer)
- Private subnets (ECS tasks and RDS instance)
- Internet Gateway and Route Tables for routing traffic to/from the internet
Then run `terraform plan` and `terraform apply --auto-approve` to create the VPC and subnets.

### Phase 2: Building the RDS Database Module
The RDS module creates a managed PostgreSQL database instance within the private subnets of the VPC. It includes:
- An RDS DB instance
- A DB subnet group
- A security group allowing access from the ECS tasks
Run `terraform plan` and `terraform apply --auto-approve` to create the RDS resources.

### Phase 3: Build the Container Registry (ECR)
This creates a private Docker container registry to store your application image.
Run `terraform plan` and `terraform apply --auto-approve` to create the ECR repository.

### Phase 4: Build the Compute Layer (ECS, ALB, IAM)
This is the final and largest phase. It builds the Application Load Balancer, the ECS Cluster, the EC2 instances, and all the necessary IAM roles and secrets.
Run `terraform plan` and `terraform apply --auto-approve` to create the ECS resources.

### Phase 5: Deploy the Application
