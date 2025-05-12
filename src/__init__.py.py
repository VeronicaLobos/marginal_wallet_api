"""
"""

from sqlmodel import create_engine, Session, SQLModel
import os
from src.models import User, Category, Transaction, PlannedExpense
from src.models import CategoryType, PaymentMethodType, CurrencyType, FrequencyType

DATABASE_URL = os.join("data", "database.db")

engine = create_engine("sqlite:///" + DATABASE_URL)
#engine = create_engine("postgresql://user:password@host:port/database_name")

if __name__ == "__main__":
    # Create the database and tables
    SQLModel.metadata.create_all(engine)
    print("Database created")
