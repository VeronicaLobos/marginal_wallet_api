"""
Transaction Schema

Users can create, update, and retrieve transactions.

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
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship, Mapped

from schema.enums import PaymentMethodType, CurrencyType

class MovementBase(SQLModel):
    movement_date: date = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType
    payment_method: PaymentMethodType

class MovementCreate(MovementBase):
    pass

class MovementUpdate(SQLModel):
    movement_date: Optional[date] = Field(default=None)
    value: Optional[float] = Field(default=None)
    currency: Optional[CurrencyType] = Field(default=None)
    payment_method: Optional[PaymentMethodType] = Field(default=None)
    category_id: Optional[int] = None

class MovementPublic(MovementBase):
    id: int

class Movement(MovementBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")

    if TYPE_CHECKING:
        from schema.user import User
        from schema.category import Category
        from schema.activity_log import ActivityLog

    user: Mapped["User"] = Relationship(
        back_populates="movements",
        sa_relationship=relationship("User",
                                     back_populates="movements")
    )
    category: Mapped["Category"] = Relationship(
        back_populates="movements",
        sa_relationship=relationship("Category",
                                     back_populates="movements")
    )
    activity_log: Optional["ActivityLog"] = Relationship(
        back_populates="movement",
        sa_relationship=relationship("ActivityLog",
                                     back_populates="movement",
                                     uselist=False,
                                     cascade="all, delete-orphan")
    )
