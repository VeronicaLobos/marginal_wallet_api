[![CI/CD Pipeline Status](https://github.com/VeronicaLobos/marginal_wallet_mvp/actions/workflows/cicd.yml/badge.svg)](https://github.com/VeronicaLobos/marginal_wallet_api/actions)

# Marginal Wallet API

Marginal Wallet is a robust RESTful API designed to help users manage their personal finances, with a focus on tracking non-fixed income and expenses. Built with Python and FastAPI, it provides a secure and feature-rich backend for a personal finance application.

This project was developed as a graduation requirement, demonstrating a full development lifecycle from an initial Minimum Viable Product (MVP) to a more advanced Version 2 with modern DevOps practices, AI integration, and a functional frontend.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Documentation](#api-documentation)
- [Getting Started: Local Development](#getting-started-local-development)
- [Running with Docker](#running-with-docker)
- [Code Quality & Testing](#code-quality--testing)
- [Automated Deployment to Google Cloud Run](#automated-deployment-to-google-cloud-run)

---

## Features

The application is structured with a clear separation of features developed across two main versions.

### Core Features (MVP)

- **Secure User Authentication**: User registration and login system using JWT (JSON Web Tokens) for secure, token-based authentication. Passwords are fully encrypted using bcrypt.
- **User Management**: Endpoints for users to manage their profiles, including updating personal details and changing passwords.
- **Category Management**: Full CRUD (Create, Read, Update, Delete) operations for user-defined income and expense categories.
- **Transaction (Movement) Tracking**: Full CRUD operations for financial movements linked to categories.
- **Planned Expenses**: Functionality for users to create and manage future planned expenses.
- **Activity Logs**: Optional logs can be attached to transactions to track notes or changes.

### Advanced Features (V2)

- **AI-Powered Financial Insights**: Integration with the Google Gemini API (gemini-1.5-flash) to provide users with an AI-generated natural language summary of their financial activity.
- **API Rate Limiting**: Implemented to prevent abuse and enhance security on sensitive endpoints.
- **Unit Testing & CI/CD**: A comprehensive test suite using pytest integrated into a Continuous Integration / Continuous Deployment (CI/CD) pipeline.
- **Pre-Commit Hooks**: A Git pre-commit hook to run the test suite automatically before allowing a commit.
- **Containerization with Docker**: Fully containerized application using Docker and Docker Compose.
- **Cloud Deployment**: Experience deploying to Render (MVP), Google Cloud Run (V2), and AWS EC2 (V2).
- **Templated Frontend**: A functional frontend prototype built with Jinja2 and Bootstrap.

---

## Tech Stack

| Component | Technology                                                                                                                                                                   |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Backend | `Python 3.12`, `FastAPI`. Served by `Uvicorn` for development and managed by `Gunicorn` with Uvicorn workers for production, providing a robust, multi-process architecture. |
| Database | `PostgreSQL` for reliable relational data storage.                                                                                                                           |
| ORM & Data | `SQLModel`, built on `SQLAlchemy` and `Pydantic` for type-safe database models and data validation.                                                                          |
| Migrations | `Alembic` for managing database schema evolution.                                                                                                                            |
| Authentication | `JWT` (PyJWT) and `OAuth2` for token-based security, with Passlib (bcrypt) for password hashing.                                                                             |
| AI Integration | `Google Gemini API` for generating financial insights (endpoint).                                                                                                            |
| Testing | `Pytest` for unit testing and `Bandit` for security scanning.                                                                                                                |
| Formatting | `Black` for opinionated, consistent code formatting.                                                                                                                         |
| Containerization | `Docker` and `Docker Compose for creating portable and reproducible application environments.                                                                                |
| CI/CD | `GitHub Actions` for automating the entire testing and deployment workflow.                                                                                                  |
| Frontend | `Jinja2` Templating, `Bootstrap` for a responsive UI prototype. Prototyping with Gemini CLI.                                                                                 |

---

## CI/CD Pipeline

This project utilizes a full CI/CD pipeline managed by GitHub Actions to automate testing and deployment.

### Continuous Integration (CI)

Runs on every push and pull request to the main branch.

- **Run Unit Tests**: Executes the pytest suite against a dedicated SQLite database.
- **Check Code Style**: Uses black to verify consistent code formatting.
- **Run Security Scan**: Uses bandit to analyze the codebase for common vulnerabilities.

### Continuous Deployment (CD)

Runs only on a push/merge to the main branch after all CI jobs pass.

- Authenticates with Google Cloud and Docker Hub.
- Builds and pushes a new Docker image to Docker Hub.
- Connects to the production database and applies alembic migrations.
- Deploys the new image to Google Cloud Run, updating the live service.

Secrets are managed securely via GitHub Secrets.

---

## API Documentation

Interactive API documentation is available via Swagger UI. Once the application is running, access it at:

**Swagger UI**: http://localhost:8000/docs

---

## Getting Started: Local Development

### 1. Prerequisites

- Python 3.12+
- PostgreSQL installed and running
- Docker and Docker Compose (Optional)

### 2. Clone the Repository

```bash
git clone git@github.com:VeronicaLobos/marginal_wallet_mvp.git
cd marginal_wallet_mvp
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

You can use a GUI tool or the psql command-line interface. If psql is not in your PATH, you may need to add it first (e.g., `export PATH="/Library/PostgreSQL/17/bin:$PATH"` on macOS).

```bash
# Connect as the postgres superuser
psql -U postgres
```

```sql
-- Inside the psql shell

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

**Note**: Obtain a `GOOGLE_API_KEY` from Google AI Studio.

### 5. Run Database Migrations

Apply all migrations to set up your schema:

```bash
alembic upgrade head

# To create new migrations in the future, use:
alembic revision --autogenerate -m "Your migration message"
alembic upgrade head
```

### 6. Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

https://marginal-wallet-api-774137592559.us-central1.run.app/docs
---

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
**Note on Ports**: The `compose.yaml` file maps port *8000* on your local machine to port *8080* inside the container. The application listens on the `$PORT` environment variable (defaulting to 8080), a best practice for compatibility with cloud platforms like Google Cloud Run.

---

## Code Quality & Testing

All development tools are listed in `requirements-dev.txt`.

**Unit Tests (pytest)**: Run the full test suite. A pre-commit hook also runs this automatically.

```bash
pytest
```

**Code Formatting (black)**: Check for style issues or reformat files automatically.

```bash
# Check for formatting issues
black --check .
# Automatically reformat files
black .
```

**Security Scanning (bandit)**: Scan the application code for vulnerabilities.

```bash
bandit -r . -x ./env,./tests
```

---

## Automated Deployment to Google Cloud Run

### 1. Prerequisites

- A Google Cloud Platform (GCP) project.
- A Docker Hub account.

### 2. Google Cloud Setup

**Step 1. Create a Google Cloud Project**:
- Go to the Google Cloud Console and sign in.
- In the top menu bar, click the project selector dropdown and then click New Project.
- Give your project a unique name (e.g., marginal-wallet-production) and link a billing account.

**Step 2. Enable APIs**
In your new GCP project, enable the following APIs:
· Cloud Run Admin API
· Cloud SQL Admin API
· Compute Engine API

**Step 3. Create a PostgreSQL Instance (Cloud SQL)**:
- Create a new PostgreSQL 17 instance.
- Set a strong password for the postgres user and save it.
- Under Connections, enable Public IP and add `0.0.0.0/0` as an authorized network.
- After the instance is created, go to its Databases tab and create a new database named exactly `marginal-wallet`.

**Step 4. Create a Service Account**:
- Go to *IAM & Admin* → *Service Accounts* and create a new account (e.g., `github-actions-deployer`).
- Grant it the role *Cloud Run Admin*.
- Go to the IAM main page, find the *Compute Engine default service account* (`<PROJECT_NUMBER>-compute@...`), and grant your `github-actions-deployer` account the *Service Account User* role on it. This is required for your deployer to act on behalf of the service that runs the container.
- Create and download a *JSON key* for your `github-actions-deployer` service account.

**Step 5. Managing Costs (Important!)**:
To avoid incurring charges, stop your Cloud SQL instance when you are not actively using the deployed application.
- Go to the [Cloud SQL Instances](https://console.cloud.google.com/sql/instances) page, select your instance, and click Stop.
- Remember to manually Start the instance before running the deployment workflow again.
- Alternatively you can use the CLI:
```bash
# To stop the instance
gcloud sql instances patch marginal-wallet-db --activation-policy NEVER
# To start the instance
gcloud sql instances patch marginal-wallet-db --activation-policy ALWAYS
```
**Note**: The Cloud Run service itself scales to zero automatically and incurs no cost when idle. You only need to manage the database instance.

Once you deploy your application successfully, you will be able to access it from a Service URL, e.g.: `https://marginal-wallet-api-774137592559.us-central1.run.app/`

### 3. GitHub Repository Configuration

Navigate to your repository's **Settings → Secrets and variables → Actions** and add the following secrets:

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

## Automated Deployment to AWS EC2

(Wip)
