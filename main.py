"""
A FastAPI application for managing marginal income and expenses.
This application provides endpoints for user registration, authentication,
and managing categories and movements (transactions).
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from config.database import create_db_and_tables
from routers import users, categories, movements, planned_expenses, activity_logs, auth


load_dotenv()

# Lifespan context manager to handle startup events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Application starting up...")
    create_db_and_tables()
    yield
    # Code to run on shutdown (if any)
    print("Application shutting down...")


app = FastAPI(
    title="Marginal Wallet API",
    description="API for managing marginal income and expenses.",
    version="1.0.0",
    lifespan=lifespan  # Use the new lifespan event handler
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Note: Rate limiting middleware is commented out for simplicity in local dev/testing.
# You can uncomment it for production or specific staging environments.
# from slowapi.middleware import SlowAPIMiddleware
# from auth.rate_limit import limiter
# app.state.limiter = limiter
# app.add_middleware(SlowAPIMiddleware)

@app.get("/")
async def home(request: Request):
    """
    This is the root endpoint of the FastAPI app.
    It returns the main landing page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login(request: Request):
    """
    This endpoint serves the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/profile")
async def profile(request: Request):
    """
    This endpoint serves the user profile page.
    """
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/dashboard")
async def dashboard(request: Request):
    """
    This endpoint serves the user dashboard page.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/user_settings")
async def user_settings(request: Request):
    """
    This endpoint serves the user settings page.
    """
    return templates.TemplateResponse("user_settings.html", {"request": request})


@app.get("/insights")
async def insights(request: Request):
    """
    This endpoint serves the financial insights page.
    """
    return templates.TemplateResponse("insights.html", {"request": request})


@app.get("/delete_user_confirm")
async def delete_user_confirm(request: Request):
    """
    This endpoint serves the delete user confirmation page.
    """
    return templates.TemplateResponse("delete_user_confirm.html", {"request": request})


@app.get("/register")
async def register(request: Request):
    """
    This endpoint serves the user registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/movements_page")
async def movements_page(request: Request):
    """
    This endpoint serves the movements list page.
    """
    return templates.TemplateResponse("movements.html", {"request": request})


@app.get("/add_movement_page")
async def add_movement_page(request: Request):
    """
    This endpoint serves the add movement page.
    """
    return templates.TemplateResponse("add_movement.html", {"request": request})


# Include all the API routers
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(movements.router)
app.include_router(planned_expenses.router)
app.include_router(activity_logs.router)
app.include_router(auth.router)
