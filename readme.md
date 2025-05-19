Marginal Wallet is a web application that allows user to keep track of their marginal income and expenses.  
It is a Back end application built using FastAPI, SQLModel, and PostgreSQL.
It provides an API with endpoints for managing income and expenses, as well as user authentication and authorization.

Work in progress.

### Features

- User registration and login
- User authentication and authorization using OAuth2 and JWT tokens
- CRUD operations for categories and transactions
- Balance calculation
- Transaction history filtering by date and category
- Activity log for transactions

Users should be able to:
- Register and log in to their accounts (using OAuth2 and JWT tokens)
- Create, read, update, and delete categories for income and expenses (type of income and counterparties)
- Create, read, update, and delete transactions based on the categories
- Quickly view the balance of their accounts
- View the history of their transactions from most recent, for a certain period of time
- View the history of their transactions by category (which would allow to keep track of the income for current month for a certain category, such as Minijobs and make sure they don't surpass the tax-free allowance)
- Add an optional activity log to each transaction (e.g. a note about the transaction)

Endpoints:
- / - API root endpoint
- /docs - Swagger UI for API documentation
- /users/registration/ - User registration
- /users/login/ - User login
- /users/me/ - Get current user information, protected endpoint
- /token/ - Get access token, hidden endpoint


Create a virtual environment to isolate dependencies
1. python3 -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt

Run the app:
```uvicorn main:app --reload --app-dir .```
or
```python3 main.py```

Install PostgreSQL
1. Install PostgreSQL on your system. You can download it from the official website: https://www.postgresql.org/download/
2. Create a new PostgreSQL database and user for your application. You can do this using the `psql` command-line tool or a GUI tool like pgAdmin4.
3. Add your credentials before creating the engine in the `main.py` file. You can use the `.env` file to store your database credentials and other environment variables.

Tech stack
* Python:
* FastAPI: a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. It is designed to be easy to use and to provide high performance, making it a popular choice for building RESTful APIs and web applications.
* uvicorn: a lightweight and fast ASGI (Asynchronous Server Gateway Interface) server implementation commonly used for serving Python web applications, particularly those built with frameworks like FastAPI.
* SQLModel: a library for interacting with SQL databases using Python. It is built on top of SQLAlchemy and Pydantic, providing a simple and intuitive way to define database models and perform CRUD (Create, Read, Update, Delete) operations.
* psycopg2-binary: SQLModel (and SQLAlchemy underneath) will automatically use psycopg2-binary as the driver for communicating with your PostgreSQL database when you use a PostgreSQL connection URL.
