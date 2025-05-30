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
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional

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
    password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    password: str

    from schema.category import Category
    categories: List["Category"] = Relationship(back_populates="user")
    from schema.transaction import Transaction
    transactions: List["Transaction"] = Relationship(back_populates="user")
    from schema.planned_expense import PlannedExpense
    planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")
