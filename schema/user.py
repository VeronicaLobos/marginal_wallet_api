"""
User schema definitions.

Users can:
- Create an account with a name, email, and password.
- Update their name and email.
- Update their password.
- Retrieve their public profile without the password.
- Have multiple categories, transactions, and planned
expenses associated with them.
"""

from __future__ import annotations

import calendar
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from schema.category import Category
    from schema.movement import Movement
    from schema.planned_expense import PlannedExpense


class UserBase(SQLModel):
    name: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str


class UserNameEmailUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[str] = None


class UserPasswordUpdate(SQLModel):
    current_password: str
    new_password: str
    confirm_new_password: str


class UserDeleteConfirmation(SQLModel):
    password: str


class MinijobsBalanceSummary(SQLModel):
    minijobs_balance: float = Field(default=0.0)
    max_earnings: str = Field(default="556€")
    current_month: str
    current_year: int


class CategoryTypeBalanceSummary(SQLModel):
    category_type: str
    balance: float = Field(default=0.0)
    current_month: str
    current_year: int


class UserDashboard(SQLModel):
    balance: float = Field(default=0.0)
    num_categories: int = Field(default=0)
    num_movements: int = Field(default=0)


class User(UserBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    password: str

    categories: Mapped[List["Category"]] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship=relationship(
            "Category", back_populates="user", cascade="all, delete-orphan"
        ),
    )
    movements: Mapped[List["Movement"]] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship=relationship(
            "Movement", back_populates="user", cascade="all, delete-orphan"
        ),
    )
    planned_expenses: Mapped[List["PlannedExpense"]] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship=relationship(
            "PlannedExpense", back_populates="user", cascade="all, delete-orphan"
        ),
    )
