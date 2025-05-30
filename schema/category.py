"""
Category schemas

Users can create, update, and retrieve categories
for their transactions.
"""

from __future__ import annotations
import enum
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"

class CategoryBase(SQLModel):
    category_type: CategoryType = Field(nullable=False)
    counterparty: str = Field(nullable=False)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    category_type: CategoryType | None = None
    counterparty: str | None = None

class CategoryPublic(CategoryBase):
    id: int
    user_id: int

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")

    from schema.user import User
    user: "User" = Relationship(back_populates="categories")
    from schema.transaction import Transaction
    transactions: List["Transaction"] = Relationship(back_populates="category")
