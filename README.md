[![CI/CD Pipeline Status](https://github.com/VeronicaLobos/marginal_wallet_mvp/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/VeronicaLobos/marginal_wallet_mvp/actions)

# Marginal Wallet API

Marginal Wallet is a robust RESTful API designed to help users manage their personal finances, with a focus on tracking non-fixed income and expenses. Built with Python and FastAPI, it provides a secure and feature-rich backend for a personal finance application.

This project was developed as a graduation requirement, demonstrating a full development lifecycle from an initial Minimum Viable Product (MVP) to a more advanced Version 2 with modern DevOps practices, AI integration, and a functional frontend.

## Features

The application is structured with a clear separation of features developed across two main versions.

### Core Features (MVP)

- **Secure User Authentication**: User registration and login system using JWT (JSON Web Tokens) for secure, token-based authentication. Passwords are fully encrypted using bcrypt.

- **User Management**: Endpoints for users to manage their profiles, including updating personal details and changing passwords.

- **Category Management**: Full CRUD (Create, Read, Update, Delete) operations for user-defined income and expense categories (e.g., Minijob, Freelance, Expenses).

- **Transaction (Movement) Tracking**: Full CRUD operations for financial movements linked to user-defined categories. Each transaction includes amount, currency, payment method, and date.

- **Planned Expenses**: Functionality for users to create and manage future planned expenses.

- **Activity Logs**: Optional logs can be attached to transactions to track notes or changes.

### Advanced Features (V2)

- **AI-Powered Financial Insights**: Integration with the Google Gemini API (`gemini-1.5-flash`) to provide users with an AI-generated natural language summary of their financial activity.

- **API Rate Limiting**: Implemented rate limiting on sensitive endpoints (like login and registration) to prevent abuse and enhance security.

- **Unit Testing & CI/CD**:  A comprehensive test suite using `pytest` integrated into a Continuous Integration / Continuous Deployment (CI/CD) pipeline.

- **Pre-Commit Hooks**: A Git pre-commit hook is configured to run the test suite automatically before allowing a commit.

- **Containerization with Docker**: The application is fully containerized using Docker and Docker Compose, allowing for consistent and reproducible environments.

- **Cloud Deployment**: Experience deploying the application to cloud platforms, including Render (MVP), Google Cloud Run (V2), and AWS EC2 (V2).

- **Templated Frontend**: A functional frontend prototype built with Jinja2 and Bootstrap to demonstrate the API's capabilities.

## Tech Stack

| Component | Technology               |
|-----------|--------------------------|
| Backend | Python 3.12, FastAPI, Uvicorn, Gunicorn |
| Database | PostgreSQL               |
| ORM & Data | SQLModel, SQLAlchemy, Pydantic |
| Migrations | Alembic                  |
| Authentication | JWT (PyJWT), OAuth2, Passlib (bcrypt) |
| AI Integration | Google Gemini API        |
| Testing | Pytest, Bandit           |
| Formatting & Linting | Black                   |
| Containerization | Docker, Docker Compose   |
| CI/CD | GitHub Actions           |
| Frontend | Jinja2 Templating, Bootstrap |

## CI/CD Pipeline
This project utilizes a full CI/CD pipeline managed by GitHub Actions. The pipeline automates testing and deployment, ensuring code quality and a streamlined release process.

The pipeline consists of two main stages:

### Continuous Integration (CI)
These jobs run on every *push* and *pull request* to the main branch to validate changes.

* **Run Unit Tests**: Executes the entire `pytest` suite against a dedicated SQLite database to ensure all business logic and endpoints work as expected.

* **Check Code Style**: Uses the `black` code formatter 🍰✨ to verify that all Python code adheres to a consistent and clean style.

* **Run Security Scan**: Employs the `bandit`  security scanner to analyze the codebase for common security vulnerabilities.

### Continuous Deployment (CD)
This job runs *only* when changes are pushed (or merged) to the main branch, and only after all CI jobs have passed.

* *Deploy to Google Cloud Run:*

1. Authenticates with Google Cloud using a service account.

2. Logs in to Docker Hub.

3. Builds a new Docker image of the application and pushes it to the Docker Hub registry.

4. Connects to the production database and applies any new alembic migrations.

5. Deploys the newly published Docker image to Google Cloud Run, updating the live service.

Secret environment variables (like database URLs and API keys) are securely managed via GitHub Secrets, ensuring sensitive information is not exposed in the codebase.


## API Documentation

This API provides comprehensive, interactive documentation via Swagger UI. Once the application is running, you can explore and test all available endpoints directly from your browser.

**Swagger UI**: http://localhost:8000/docs

## Getting Started: Local Development

Follow these instructions to set up and run the project locally.

### 1. Prerequisites

- Python 3.12+
- PostgreSQL installed and running
- Docker and Docker Compose (Optional, for containerized setup)

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

# Install all required packages (production + development)
pip install -r requirements-dev.txt
```

### 4. Database and Environment Configuration

**Create a PostgreSQL Database**: Create a new PostgreSQL database named `marginal-wallet`.

**Configure Environment Variables**: Create a `.env` file in the project root with the following content, filling in your specific details.

```env
# For local development (uvicorn)
DATABASE_URL="postgresql://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@localhost:5432/marginal-wallet"

# --- General Settings ---
SECRET_KEY="a-strong-and-random-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_API_KEY="your-google-api-key-here"
```

> **Note**: You need to obtain a `GOOGLE_API_KEY` from Google AI Studio to use the financial insights feature.

### 5. Run Database Migrations

Apply all database migrations to set up your schema:
```bash
alembic upgrade head
```

### 6. Run the Application

You can now start the FastAPI development server:
```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

## Running with Docker

For a consistent and isolated environment, you can use Docker Compose.

**Configure `.env` for Docker**: In your `.env` file, comment out the localhost URL and use the `host.docker.internal` URL. This special DNS name allows the container to connect to the PostgreSQL database running on your host machine.

```env
# For local development (uvicorn)
# DATABASE_URL="postgresql://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@localhost:5432/marginal-wallet"

# For Docker container connecting to a local host DB
DATABASE_URL="postgresql://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@host.docker.internal:5432/marginal-wallet"
```

Build and run the container:
```bash
docker-compose up --build
```

The application will be accessible at http://localhost:8000.

## Code Quality & Testing

This project uses a suite of tools to ensure code quality, consistency, and security. All development tools are listed in `requirements-dev.txt`.

### Running Unit Tests

This project uses `pytest for unit testing. A pre-commit hook is also configured to run tests before each commit.

To run the full test suite manually:
```bash
pytest
```

### Code Formatting

The codebase is formatted using `black`.

To check for formatting issues:
```bash
# Check for formatting issues
black --check .

# Automatically reformat files
black .
```

### Security Scanning

A static security analysis is performed using bandit.

To run the scanner on the application code (excluding tests and dependencies):
```
bandit -r . -x ./env,./tests
```
