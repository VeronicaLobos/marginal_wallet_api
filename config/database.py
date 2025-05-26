"""
Database configuration and session management for FastAPI application.

This module sets up the database connection, creates tables,
and provides a dependency for database sessions.

It uses SQLModel for ORM and dotenv for environment variable management.

    * create_db_and_tables: Function to create the database and tables
    if they do not exist.
    * get_session: Dependency to get a database session for each request,
    returning a generator that yields a session.
"""

import os
from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated, Generator

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """
    Create the database and tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)
    print("Database tables created (or checked)")

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    This function is used to create a new session for each request.
    """
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
