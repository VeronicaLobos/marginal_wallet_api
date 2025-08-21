"""
A FastAPI application for managing marginal income and expenses.
This application provides endpoints for user registration, authentication,
and managing categories and movements (transactions).
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Response, Request, status
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.database import create_db_and_tables
from routers import users, categories, movements, planned_expenses, activity_logs, auth

from slowapi.middleware import SlowAPIMiddleware
from auth.rate_limit import limiter, custom_rate_limit_exceeded_handler


load_dotenv()

app = FastAPI(
    title="Marginal Wallet API",
    description="API for managing marginal income and expenses.",
    version="1.0.0"
    )

# --- START: Rate Limiting Setup (Conditional) ---
# Attach the limiter instance to the app's state for global access
#app.state.limiter = limiter
# Register the custom exception handler for rate limit exceeded errors
#app.add_exception_handler(StarletteHTTPException, custom_rate_limit_exceeded_handler)

# Only add the SlowAPIMiddleware if not running in a Pytest environment
# PYTEST_CURRENT_TEST is set by pytest during test runs
#if not os.environ.get("PYTEST_CURRENT_TEST"): # <-- ADDED CONDITIONAL CHECK
#    app.add_middleware(SlowAPIMiddleware)
# --- END: Rate Limiting Setup ---


@app.on_event("startup")
def on_startup():
    from schema.user import User
    from schema.category import Category
    from schema.movement import Movement
    from schema.planned_expense import PlannedExpense
    from schema.activity_log import ActivityLog
    create_db_and_tables()

@app.get("/")
async def home():
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
