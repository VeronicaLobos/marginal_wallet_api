"""
This module contains helper functions to check ownership of
categories and movements for the current user.

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

## Importing necessary schemas
from schema.category import Category
from schema.enums import CategoryType
from schema.user import User
from schema.transaction import Movement


def check_category_belongs_to_user(
    category_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
) -> Category:
    """
    Helper function to check if a category belongs to the current user.

    This function retrieves a category by its ID and checks if it
    belongs to the current user. If not, it raises an HTTPException.
    """
    categories_statement = (select(Category)
                            .where(Category.id == category_id)
                            .where(Category.user_id == current_user.id))
    category = db.exec(categories_statement).first()

    if not category:
        raise HTTPException(status_code=404,
                            detail="Category not found or does not belong to the user.")

    return category


def check_movement_belongs_to_user(
    movement_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
) -> Movement:
    """
    Helper function to check if a movement belongs to the current user.

    This function retrieves a movement by its ID and checks if it
    belongs to the current user. If not, it raises an HTTPException.
    """
    statement = (select(Movement)
                 .where(Movement.id == movement_id,
                        Movement.user_id == current_user.id))
    movement = db.exec(statement).first()

    if not movement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Movement not found or does not belong to the user.")

    return movement
