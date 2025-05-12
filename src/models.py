"""
This file contains the database models for the project.

* I'll be using SQLite to start the project and later migrate to PostgreSQL with Alembic
* I will use Alembic to manage the migrations later
* I will use SQLModel (SQLAlchemy + Pydantic) to create the database models
* I will use enum for the categorical variables
"""

from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
import enum

## Before the tables I need the categorical variables for some of the tables

class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    banktransfer = "Bank Transfer"

class CurrencyType(str, enum.Enum):
    euro = "EURO"
    usd = "USD"

class FrequencyType(str, enum.Enum):
    weekly = "Weekly"
    monthly = "Monthly"
    quarterly = "Quarterly"
    biannually = "Biannually"
    yearly = "Yearly"
    one_time = "One Time"

## Here are the five tables I need to create for the project

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False)
    # TODO: hash the password before storing it
    password: str

    # One user can have many categories, transactions and planned expenses...
    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_type: CategoryType = Field(nullable=False)
    Counterparty: str = Field(nullable=False)

    # ...therefore many categories can belong to one user
    user: "User" = Relationship(back_populates="categories")
    # One category can have many transactions...
    transactions: List["Transaction"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    date: str = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    payment_method: PaymentMethodType = Field(nullable=False)

    # ... therefore many transactions can belong to one user
    user: "User" = Relationship(back_populates="transactions")
    # ... there many transactions can belong to one category
    category: "Category" = Relationship(back_populates="transactions")
    # One transaction can have one activity log...
    activity_log: Optional["Activity_log"] = Relationship(back_populates="transaction")


class PlannedExpense(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: Optional[datetime] = Field(nullable=True)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)

    # ...many planned expenses can belong to one user
    user: "User" = Relationship(back_populates="planned_expenses")

class Activity_log(SQLModel, table=True):
    id: int = Field(primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)
    description: str = Field(nullable=False)

    # ...one activity log can belong to one transaction
    transaction: "Transaction" = Relationship(back_populates="activity_log")


if __name__ == "__main__":
    print("Models file is being executed.")
    try:
        user = User(id=1, name="Test User", email="test@example.com", password="password")
        print(f"User object created: {user.name}")
        print("User class is defined correctly.")
    except NameError as e:
        print(f"Error creating User object: {e}")
