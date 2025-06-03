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

Value represents the amount of the transaction, which will be
negative for Categories of type "Expenses" and positive for
Categories of type "Minijob", "Freelance", or "Commission".
"""

from __future__ import annotations
import enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship, Mapped

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    bank_transfer = "Bank Transfer"

class CurrencyType(str, enum.Enum):
    euro = "EURO"
    usd = "USD"

class MovementBase(SQLModel):
    date: str = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    payment_method: PaymentMethodType = Field(nullable=False)

class MovementCreate(MovementBase):
    category_id: int

class MovementUpdate(MovementBase):
    date: str | None = None
    value: float | None = None
    currency: CurrencyType | None = None
    payment_method: PaymentMethodType | None = None

class MovementPublic(MovementBase):
    id: int
    user_id: int
    category_id: int

class Movement(MovementBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    if TYPE_CHECKING:
        from schema.user import User
        from schema.category import Category
        from schema.activity_log import ActivityLog

    user: "User" = Relationship(
        back_populates="movements",
        sa_relationship=relationship("User",
                                     back_populates="movements")
    )
    category: "Category" = Relationship(
        back_populates="movements",
        sa_relationship=relationship("Category",
                                     back_populates="movements")
    )
    activity_log: Optional["ActivityLog"] = Relationship(
        back_populates="movement",
        sa_relationship=relationship("ActivityLog",
                                     back_populates="movement",
                                     uselist=False)
    )
