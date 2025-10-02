"""
Activity Log Schema

Activity logs are used to optionally track changes or
notes associated with transactions in the application.

Users can create, update, and retrieve activity logs
for movements (transactions).

TODO: Activity logs can be deleted. If a transaction
with an activity log is deleted, the activity log
will also be deleted.

* Each activity log is associated with a movement.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.orm import relationship

class ActivityLogBase(SQLModel):
    description: str = Field(min_length=1, nullable=False)

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogPublic(ActivityLogBase):
    id: int
    movement_id: int

class ActivityLogUpdate(SQLModel):
    description: str = Field(min_length=1, nullable=False)

class ActivityLog(ActivityLogBase, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    movement_id: int = Field(foreign_key="movement.id",
                                unique=True)

    if TYPE_CHECKING:
        from schema.movement import Movement

    movement: "Movement" = Relationship(
        back_populates="activity_log",
        sa_relationship=relationship("Movement",
                                     back_populates="activity_log",
                                     uselist=False)
                                    )
