"""
A FastAPI application for managing marginal income and expenses.
This application provides endpoints for user registration, authentication,
and managing categories and movements (transactions).
"""

from dotenv import load_dotenv
from fastapi import FastAPI

from config.database import create_db_and_tables
from routers import users, categories, movements, planned_expenses, activity_logs, auth

load_dotenv()

app = FastAPI(
    title="Marginal Wallet API",
    description="API for managing marginal income and expenses.",
    version="1.0.0"
    )

@app.on_event("startup")
def on_startup():
    from schema.user import User
    from schema.category import Category
    from schema.movement import Movement
    from schema.planned_expense import PlannedExpense
    from schema.activity_log import ActivityLog
    create_db_and_tables()

@app.get("/")
def home():
    """
    This is the root endpoint of the FastAPI app.
    It returns a simple message.
    """
    return {"greeting": "Welcome to the Marginal Wallet API!"}


app.include_router(users.router)
app.include_router(categories.router)
app.include_router(movements.router)
app.include_router(planned_expenses.router)
app.include_router(activity_logs.router)
app.include_router(auth.router)
