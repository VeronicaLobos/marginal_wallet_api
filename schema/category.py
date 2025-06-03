"""
Category schemas

Users can create, update, and retrieve categories
for their transactions*.
"""

from __future__ import annotations
import enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship, Mapped

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

    if TYPE_CHECKING:
        from schema.user import User
        from schema.transaction import Movement

    user: "User" = Relationship(
        back_populates="categories",
        sa_relationship=relationship("User", back_populates="categories")
    )
    movements: Mapped[List["Movement"]] = Relationship(
        back_populates="category",
        sa_relationship=relationship("Movement", back_populates="category")
    )
