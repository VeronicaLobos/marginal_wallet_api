import os
import sys
from sqlmodel import create_engine, SQLModel, Session

# Add the project root to the Python path if it's not already there
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Try a direct import again now that the path is hopefully correct
from src.models import User, Category, Transaction, PlannedExpense, Activity_log

DATABASE_DIR = "data"
DATABASE_FILE = "database.db"
DATABASE_URL = os.path.join(DATABASE_DIR, DATABASE_FILE)
engine = create_engine(f"sqlite:///{DATABASE_URL}")
# engine = create_engine("postgresql://user:password@host:port/database_name")

def create_db_and_tables():
    """
    Create the database and tables if they don't exist.
    This function will be called when this file is run directly.
    It will create the database and tables using SQLModel.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True)
    print("create_db_and_tables() function called")
    SQLModel.metadata.create_all(engine)
    print("SQLModel.metadata.create_all(engine) executed")
    print("Database created")

def get_session():
    """
    Dependency to get a database session.
    This function contains a generator with the session as a context manager.
    It will be used in the FastAPI app to get a session for each request.
    """
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    # Create the database and tables when this file is run directly
    create_db_and_tables()
    