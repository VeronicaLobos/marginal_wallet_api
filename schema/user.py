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

class UserUpdate(UserBase):
    name: str | None = None
    email: int | None = None
    password: str | None = None

class User(UserBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    password: str

    #categories: List["Category"] = Relationship(back_populates="user")
    #transactions: List["Transaction"] = Relationship(back_populates="user")
    #planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")

