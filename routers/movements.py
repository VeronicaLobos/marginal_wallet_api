"""
router for managing movements in the Marginal Wallet API.

This module provides endpoints to create, retrieve, and delete movements
related to financial transactions. Movements can be categorized as income
or expenses depending on the value being positive or negative, respectively.

Creating a movement requires a user id, a category id, a date, a payment
method, and a value.
"""

from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from auth.auth import get_current_active_user
from config.database import SessionDep

from schema.user import User
from schema.category import Category
from schema.transaction import MovementCreate, MovementPublic, Movement


# APIRouter instance for movement operations
router = APIRouter(
    prefix="/movements",
    tags=["movements"]
)

@router.post("/add/",
             response_model=MovementPublic,
             status_code=status.HTTP_201_CREATED)
async def create_movement(
        movement: MovementCreate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: SessionDep
):
    """
    Endpoint to create a new movement (a transaction).

    This endpoint expects a POST request with an instance
    of MovementCreate, which includes the category id,
    date, payment method, value, and currency of the movement.
    It associates the movement with the
    authenticated user and the specified category.
    """
    # Checks if the int provided in the request body is a valid category id
    statement = (select(Category)
                 .where(movement.category_id == Category.id,
                                    Category.user_id == current_user.id))
    category = db.exec(statement).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or does not belong to the user."
        )

    # Creates a new movement instance, by unpacking the data from
    # the request body into a dictionary and adding the user id
    db_movement = Movement(**movement.model_dump(), user_id=current_user.id)
    try:
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return db_movement
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movement creation failed: duplicate entry or invalid data."
        )
    except Exception as e:
        db.rollback()
        print(f"Error creating movement: {e}") # for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the movement."
        )

@router.get("/list/",
            response_model=list[MovementPublic],
            status_code=status.HTTP_200_OK)
async def list_movements(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: SessionDep
):
    """
    Endpoint to retrieve all movements for the authenticated user.

    This endpoint returns a list of all movements associated with the
    authenticated user, including their details such as category,
    date, payment method, value, and currency.
    It also includes the category type and counterparty.
    """
    statement = (select(Movement)
                 .where(Movement.user_id == current_user.id)
                 .order_by(Movement.date.desc()))
    movements = db.exec(statement).all()

    if not movements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movements found for the user."
        )

    return movements