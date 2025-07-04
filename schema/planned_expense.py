"""
Planned Expense Schema

Planned expenses are future expenses that users
can plan for.

Users can create, update, delete and retrieve
planned expenses.

* One User can have multiple planned expenses.
"""

from __future__ import annotations
from datetime import date
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import relationship, Mapped

from schema.enums import CurrencyType, FrequencyType

class PlannedExpenseBase(SQLModel):
    aprox_date: date = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)
    description: str = Field(min_length=1)

class PlannedExpenseCreate(PlannedExpenseBase):
    pass

class PlannedExpenseUpdate(SQLModel):
    # TODO: Correct the typo in the field name
    aprox_date: Optional[date] = Field(default=None)
    value: Optional[float] = Field(default=None)
    currency: Optional[CurrencyType] = Field(default=None)
    frequency: Optional[FrequencyType] = Field(default=None)
    description: Optional[str] = Field(default=None, min_length=1)

class PlannedExpensePublic(PlannedExpenseBase):
    id: int
    user_id: int

class PlannedExpense(PlannedExpenseBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")

    if TYPE_CHECKING:
        from schema.user import User

    user: Mapped["User"] = Relationship(
        back_populates="planned_expenses",
        sa_relationship=relationship("User",
                        back_populates="planned_expenses")
    )
