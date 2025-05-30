"""
Activity Log Schema

Activity logs are used to optionally track changes or
notes associated with transactions in the application.

Users can create, update, and retrieve activity logs
for transactions.

TODO: Activity logs can be deleted. If a transaction
with an activity log is deleted, the activity log
will also be deleted.

* Each activity log is associated with a transaction.
"""

from __future__ import annotations
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class ActivityLogBase(SQLModel):
    description: str = Field(nullable=False)

class ActivityLog(ActivityLogBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)

    from schema.transaction import Transaction
    transaction: "Transaction" = Relationship(back_populates="activity_log")
