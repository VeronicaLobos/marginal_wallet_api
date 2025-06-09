# Marginal Wallet

Marginal Wallet is a web application designed to help users keep track of their non-fixed income and expenses. It is built as a backend API using FastAPI, SQLModel, and PostgreSQL.

It provides a robust API with secure endpoints for managing user accounts, categories, financial transactions and activity logs. It provides balance calculations, transaction history filtering, and more to help users manage their finances effectively and thus, make better financial decisions thanks to a reliable and safe tracking system.

**Work in progress.**

## Key Features

### User Management & Security
- User registration and login using OAuth2 and JWT tokens ✅
- Partial updates to user account information (e.g., changing password, name, email) ✅

### Category Management
- Create, Read, Update, and Delete (CRUD) operations for income and expense categories (defined by category_type like Minijob, Freelance, Expenses, and counterparty) ✅

### Transaction Management
- Create, Read, Update, and Delete (CRUD) operations for financial transactions (movements), which are linked to user-defined categories ✅
- Transactions support value (amount), currency, payment_method, and date ✅

### Data Structure
- Associated activity log for transactions (schema defined, CRUD endpoints not yet implemented) ❌

### Core Financial Tracking
- Balance calculation ⏳
- Transaction history filtering by date and category ⏳
- Viewing transaction history by category to track income/expenses against allowances ⏳

## API Endpoints

This section lists the primary API endpoints currently implemented in the Marginal Wallet application.

**Base URL:** `/api`

### Documentation
- `GET /docs` - Swagger UI for interactive API documentation

### General Endpoints

- `GET /` - Root endpoint returns a welcome message to check if the API is running
- `POST /token` - Authenticates a user with username (email) and password to obtain a JWT access token

### User Endpoints
- `POST /users/registration/` - Register a new user account with a name, email, and password
- `GET /users/me/` - Retrieve details of the current authenticated user
- `GET /users/me/items/` - Retrieve categories associated with the current authenticated user
- `DELETE /users/delete/` - Delete the current authenticated user's account and all associated data, requiring password confirmation

### Category Endpoints
- `GET /categories/` - Retrieve a list of all categories belonging to the current authenticated user
- `POST /categories/add/` - Create a new category for the authenticated user, specifying type and counterparty

### Movement (Transaction) Endpoints
- `POST /movements/add/` - Create a new movement (transaction) for the authenticated user, linking it to a specific category
- `GET /movements/list/` - Retrieve a list of all movements associated with the current authenticated user


## Getting Started

### Setup a Virtual Environment

It's recommended to create a virtual environment to isolate your project's dependencies from your system's Python packages.

1. **Create the virtual environment:**
   ```bash
   python3 -m venv env
   ```

2. **Activate the virtual environment:**
   ```bash
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Run the Application

Once dependencies are installed, you can run the FastAPI application:

```bash
uvicorn main:app --reload --app-dir .
```

*(This command assumes your main.py is in the root directory. `--app-dir .` ensures Uvicorn finds it correctly.)*

Or, if you prefer to run it as a standard Python script (without auto-reloading):

```bash
python3 main.py
```

### Database Setup (PostgreSQL)

Marginal Wallet uses PostgreSQL for data storage.

1. **Install PostgreSQL:** Download and install PostgreSQL on your system from the official website: https://www.postgresql.org/download/

2. **Create Database & User:** Create a new PostgreSQL database and user for your application. You can do this using the `psql` command-line tool or a GUI tool like pgAdmin4.

3. **Add Credentials:** Add your database credentials (e.g., username, password, host, database name) to your application's configuration, ideally using environment variables (e.g., in a `.env` file) before creating the database engine in your `main.py` file.

###Tech Stack

This project leverages the following key technologies and libraries:
* Python: The core programming language.
* FastAPI (~0.115.12): A modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints. It is designed for ease of use and to provide high performance, making it popular for building RESTful APIs and web applications.
* Uvicorn (~0.34.2): A lightweight and fast ASGI (Asynchronous Server Gateway Interface) server implementation commonly used for serving Python web applications, particularly those built with frameworks like FastAPI.
* PostgreSQL: The robust relational database used for data storage and management in this application, providing reliable and scalable data handling capabilities.
* SQLModel (~0.0.24): A library for interacting with SQL databases using Python. It is built on top of SQLAlchemy and Pydantic, providing a simple and intuitive way to define database models and perform CRUD (Create, Read, Update, Delete) operations.
* Pydantic (~2.11.4): A powerful data validation and parsing library used by FastAPI and SQLModel. It enforces type hints at runtime and handles data serialization.
* SQLAlchemy (~2.0.40): The underlying Python SQL toolkit and Object Relational Mapper (ORM) that SQLModel is built upon, providing robust database interaction capabilities.
* Passlib [bcrypt]: A comprehensive password hashing library, specifically using the bcrypt scheme, for securely storing user passwords.
* PyJWT (~2.10.1): A popular library for encoding and decoding JSON Web Tokens (JWTs), complementing python-jose in handling authentication tokens.