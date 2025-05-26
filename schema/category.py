"""
Category Schemas

TODO: Separate schemas for Transaction, PlannedExpense, and ActivityLog.
"""

from __future__ import annotations

import enum
from datetime import datetime
from sqlmodel import (Field, Relationship,
            SQLModel, create_engine, inspect, select)
from typing import Annotated, List, Optional
from sqlalchemy.orm import Mapped, relationship

class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    bank_transfer = "Bank Transfer"

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


class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_type: CategoryType = Field(nullable=False)
    counterparty: str = Field(nullable=False)

    #user: Mapped["User"] = relationship(back_populates="categories")
    #transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    date: str = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    payment_method: PaymentMethodType = Field(nullable=False)

    # user: "User" = Relationship(back_populates="transactions")
    # category: "Category" = Relationship(back_populates="transactions")
    # activity_log: Optional["ActivityLog"] = Relationship(back_populates="transaction")

class PlannedExpense(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    date: Optional[datetime] = Field(nullable=True)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)

    # user: "User" = Relationship(back_populates="planned_expenses")

class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)
    description: str = Field(nullable=False)

    # transaction: "Transaction" = Relationship(back_populates="activity_log")