"""
Router for managing movements in the Marginal Wallet API.

This module provides endpoints to retrieve, update
and delete movements (financial transactions).
Movements can be categorized as income or expenses depending
on the value being positive or negative, respectively.
"""

from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, extract

from auth.auth import get_current_active_user
from config.database import SessionDep
from dependencies import check_movement_belongs_to_user, check_category_belongs_to_user
from schema.activity_log import ActivityLogPublic, ActivityLogCreate, ActivityLog
from schema.category import Category

from schema.user import User
from schema.movement import MovementPublic, Movement, MovementUpdate

# APIRouter instance for movement operations
router = APIRouter(prefix="/movements", tags=["movements"])


@router.get(
    "/list", response_model=list[MovementPublic], status_code=status.HTTP_200_OK
)
async def list_movements(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
    sort_order: str = Query(
        "desc", description="Sort order for movement date (asc or desc)"
    ),
    time_filter: str = Query(
        "last_month",
        description="Filter movements by time (last_month, last_3_months, all)",
    ),
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        100, ge=1, le=200, description="Max number of items to return (page size)"
    ),
):
    """
    Endpoint to retrieve all movements for the authenticated user.

    This endpoint returns a list of paginated movements ordered by
    movement date in descending order, associated with the
    authenticated user.
    When no results are found, it returns an empty list.
    """
    statement = select(Movement).where(Movement.user_id == current_user.id)

    # Apply time filter
    now = datetime.now()
    if time_filter == "last_month":
        statement = statement.where(
            extract("month", Movement.movement_date) == now.month,
            extract("year", Movement.movement_date) == now.year,
        )
    elif time_filter == "last_3_months":
        three_months_ago = now - timedelta(days=90)
        statement = statement.where(Movement.movement_date >= three_months_ago)
    elif time_filter == "all":
        pass  # No time filter applied

    # Apply sort order
    if sort_order == "asc":
        statement = statement.order_by(Movement.movement_date.asc())
    else:  # Default to desc
        statement = statement.order_by(Movement.movement_date.desc())

    statement = statement.offset(skip).limit(limit)
    movements = db.exec(statement).all()

    return movements


@router.get(
    "/{movement_id}", response_model=MovementPublic, status_code=status.HTTP_200_OK
)
async def get_movement_by_id(
    movement: Annotated[Movement, Depends(check_movement_belongs_to_user)],
):
    """
    Endpoint to retrieve a single movement by its ID.

    This endpoint uses the `check_movement_belongs_to_user` dependency
    to ensure that the movement with the given `movement_id` exists
    and belongs to the currently authenticated user.

    If the movement is found and authorized, it returns the movement's
    details. Otherwise, it raises an HTTPException (e.g., 404 Not Found
    if the movement doesn't exist or 403 Forbidden if it doesn't belong
    to the user, handled by the dependency).
    """
    return movement


@router.patch(
    "/{movement_id}", response_model=MovementUpdate, status_code=status.HTTP_200_OK
)
async def update_movement(
    movement: Annotated[Movement, Depends(check_movement_belongs_to_user)],
    update: MovementUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
):
    """
    Endpoint to partially update an existing movement.

    The dependency `check_movement_belongs_to_user` ensures that the
    movement belongs to the current user, and fetches the movement
    or raises a 404 error if it does not exist.

    The request body can contain any subset of fields defined in
    MovementUpdate, allowing for flexible updates to the movement's
    details such as date, value, currency, and payment method.
    """
    update_data = update.model_dump(exclude_unset=True)

    if "category_id" in update_data and update_data["category_id"] is not None:
        new_category_id = update_data["category_id"]
        category_statement = select(Category).where(
            Category.id == new_category_id, Category.user_id == current_user.id
        )
        existing_category = db.exec(category_statement).first()

        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {new_category_id} not found or "
                f"does not belong to the current user.",
            )
    elif "category_id" in update_data and update_data["category_id"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category ID cannot be set to null/None for a movement"
            "as it is a required field.",
        )

    for key, value in update_data.items():
        setattr(movement, key, value)

    try:
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movement update failed: duplicate entry or invalid data.",
        )


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement(
    movement: Annotated[Movement, Depends(check_movement_belongs_to_user)],
    db: SessionDep,
):
    """
    Endpoint to delete a movement.

    This endpoint deletes a movement by its ID, ensuring that the
    movement belongs to the authenticated user. If the movement is
    successfully deleted, it returns a 204 No Content response.
    """
    db.delete(movement)
    db.commit()


@router.post(
    "/{movement_id}/activity_logs",
    response_model=ActivityLogPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity_log(
    activity_log_data: ActivityLogCreate,
    movement: Annotated[Movement, Depends(check_movement_belongs_to_user)],
    db: SessionDep,
):
    """
    Create a new activity log for a specific movement belonging to the user.
    Each movement can only have one activity log.
    """
    existing_log_statement = select(ActivityLog).where(
        ActivityLog.movement_id == movement.id
    )
    existing_log = db.exec(existing_log_statement).first()
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An activity log already exists for movement ID "
            f"{movement.id}. Each movement can only have one log.",
        )

    db_activity_log = ActivityLog.model_validate(
        activity_log_data, update={"movement_id": movement.id}
    )

    try:
        db.add(db_activity_log)
        db.commit()
        db.refresh(db_activity_log)
        return db_activity_log
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity Error creating activity log: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating activity log (e.g., movement ID already has a log).",  # <--- Changed detail
        )
    except Exception as e:
        db.rollback()
        print(f"Error creating activity log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the activity log.",
        )
