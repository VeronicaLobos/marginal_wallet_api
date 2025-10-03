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

| Component | Technology |
|-----------|--------------------------|
| Backend | Python 3.12, FastAPI, Uvicorn, Gunicorn |
| Database | PostgreSQL |
| ORM & Data | SQLModel, SQLAlchemy, Pydantic |
| Migrations | Alembic |
| Authentication | JWT (PyJWT), OAuth2, Passlib (bcrypt) |
| AI Integration | Google Gemini API |
| Testing | Pytest, Bandit |
| Formatting | Black |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Frontend | Jinja2 Templating, Bootstrap |

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

---

## Code Quality & Testing

All development tools are listed in `requirements-dev.txt`.

**Unit Tests (pytest)**: Run the full test suite. A pre-commit hook also runs this automatically.

```bash
pytest
```

**Code Formatting (black)**: Check for style issues or reformat files automatically.

```bash
black --check .
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

**Enable APIs**: In your GCP project, enable the Cloud Run Admin API, Cloud SQL Admin API, and Compute Engine API.

**Create a PostgreSQL Instance (Cloud SQL)**:

- Create a new PostgreSQL 17 instance.
- Set a strong password for the postgres user and save it.
- Under Connections, enable Public IP and add `0.0.0.0/0` as an authorized network.
- After the instance is created, go to its Databases tab and create a new database named exactly `marginal-wallet`.

**Create a Service Account**:

- Go to IAM & Admin → Service Accounts and create a new account.
- Grant it the roles: Cloud Run Admin and Cloud SQL Client.
- Create and download a JSON key for this service account.

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
