"""
Transaction Schema

Users can create, update, and retrieve transactions.

TODO: Transactions can be deleted, and any associated activity
logs will also be deleted.

* Each transaction is associated with a user and a category
from that user.
* Each User and Category can have multiple transactions.
* Each transaction can optionally have an activity log for
tracking changes or notes.

- Value represents the amount of the transaction, which will be
negative for Categories of type "Expenses" and positive for
Categories of type "Minijob", "Freelance", or "Commission".
- Date is a string in the format "YYYY-MM-DD" representing
the date of the transaction, which might be in the past,
therefore a timestamp is not used.
"""

from __future__ import annotations
import enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    bank_transfer = "Bank Transfer"

class CurrencyType(str, enum.Enum):
    euro = "EURO"
    usd = "USD"

class TransactionBase(SQLModel):
    date: str = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    payment_method: PaymentMethodType = Field(nullable=False)

class TransactionCreate(TransactionBase):
    category_id: int

class TransactionUpdate(TransactionBase):
    date: str | None = None
    value: float | None = None
    currency: CurrencyType | None = None
    payment_method: PaymentMethodType | None = None

class TransactionPublic(TransactionBase):
    id: int
    user_id: int
    category_id: int

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    from schema.user import User
    user: "User" = Relationship(back_populates="transactions")
    from schema.category import Category
    category: "Category" = Relationship(back_populates="transactions")
    from schema.activity_log import ActivityLog
    activity_log: Optional["ActivityLog"] = Relationship(back_populates="transaction")
