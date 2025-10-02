"""
This module contains helper functions to check ownership of
resources (categories, movements, planned expenses, and activity logs)
for the current user.

Thanks to FastAPI's dependency injection system,
these functions can be easily integrated into route handlers
to enforce ownership checks before performing any operations
on categories and movements.
"""

from sqlmodel import select
from typing import Annotated
from fastapi import Depends, HTTPException, status

## Importing necessary dependencies
from config.database import SessionDep
from auth.auth import get_current_active_user
from schema.activity_log import ActivityLog

## Importing necessary schemas
from schema.category import Category
from schema.enums import CategoryType
from schema.planned_expense import PlannedExpense
from schema.user import User
from schema.movement import Movement


def check_category_belongs_to_user(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
) -> Category:
    """
    Helper function to check if a category belongs to the current user.

    This function retrieves a category by its ID and checks if it
    belongs to the current user. If not, it raises an HTTPException.
    """
    categories_statement = (
        select(Category)
        .where(Category.id == category_id)
        .where(Category.user_id == current_user.id)
    )
    category = db.exec(categories_statement).first()

    if not category:
        raise HTTPException(
            status_code=404, detail="Category not found or does not belong to the user."
        )

    return category


def check_movement_belongs_to_user(
    movement_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
) -> Movement:
    """
    Helper function to check if a movement belongs to the current user.

    This function retrieves a movement by its ID and checks if it
    belongs to the current user. If not, it raises an HTTPException.
    """
    statement = select(Movement).where(
        Movement.id == movement_id, Movement.user_id == current_user.id
    )
    movement = db.exec(statement).first()

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found or does not belong to the user.",
        )

    return movement


async def check_planned_expense_belongs_to_user(
    planned_expense_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
) -> PlannedExpense:
    """
    Dependency to check if a planned expense with the given ID exists
    and belongs to the currently authenticated user.
    Fetches the planned expense if found, otherwise raises a 404 HTTPException.
    """
    statement = select(PlannedExpense).where(
        PlannedExpense.id == planned_expense_id,
        PlannedExpense.user_id == current_user.id,
    )
    planned_expense = db.exec(statement).first()
    if not planned_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned expense not found or does not belong to the current user.",
        )
    return planned_expense


async def check_activity_log_belongs_to_user(
    activity_log_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
) -> ActivityLog:
    """
    Dependency to check if an activity log with the given ID exists
    and if its associated movement belongs to the currently authenticated user.
    Fetches the activity log if found, otherwise raises a 404 HTTPException.
    """
    statement = (
        select(ActivityLog)
        .join(Movement)
        .where(ActivityLog.id == activity_log_id, Movement.user_id == current_user.id)
    )
    activity_log = db.exec(statement).first()
    if not activity_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found or does not belong "
            "to the current user's movements.",
        )
    return activity_log
