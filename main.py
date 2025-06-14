"""
A FastAPI application for managing marginal income and expenses.
This application provides endpoints for user registration, authentication,
and managing categories and movements (transactions).
"""

import os
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated
from fastapi import (Depends, FastAPI,
                     HTTPException, status)
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth import authenticate_user, create_access_token
from config.database import create_db_and_tables, SessionDep
from routers import users, categories, movements, planned_expenses, activity_logs
from schema.auth import Token

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

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep) -> Token:
    """
    Login endpoint to authenticate a user and return an access token.
    This endpoint expects a POST request with form data containing
    the username and password of the user to authenticate.
    """
    user = authenticate_user(form_data.username,
                             form_data.password,
                             session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    secret_key = os.environ.get("SECRET_KEY")
    algorithm = os.environ.get("ALGORITHM")
    if not secret_key or not algorithm:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: "
                   "Missing secrets for token generation."
        )

    access_token_expires = timedelta(minutes=int(os.environ
                        .get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

app.include_router(users.router)
app.include_router(categories.router)
app.include_router(movements.router)
app.include_router(planned_expenses.router)
app.include_router(activity_logs.router)