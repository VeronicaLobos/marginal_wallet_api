from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session

from auth.auth import get_current_active_user
from config.database import SessionDep
from dependencies import check_planned_expense_belongs_to_user

from schema.user import User
from schema.planned_expense import (
    PlannedExpense,
    PlannedExpenseCreate,
    PlannedExpenseUpdate,
    PlannedExpensePublic,
)

# APIRouter instance for planned expenses operations
router = APIRouter(prefix="/planned_expenses", tags=["planned_expenses"])


@router.post(
    "/", response_model=PlannedExpensePublic, status_code=status.HTTP_201_CREATED
)
async def create_planned_expense(
    planned_expense: PlannedExpenseCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
):
    """
    Creates a new planned expense for the authenticated user.
    """
    db_planned_expense = PlannedExpense.model_validate(
        planned_expense, update={"user_id": current_user.id}
    )

    try:
        db.add(db_planned_expense)
        db.commit()
        db.refresh(db_planned_expense)
        return db_planned_expense
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity Error creating planned expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating planned expense due to data " "integrity issue.",
        )
    except Exception as e:
        db.rollback()
        print(f"Error creating planned expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating "
            "the planned expense.",
        )


@router.get(
    "/list", response_model=List[PlannedExpensePublic], status_code=status.HTTP_200_OK
)
async def list_planned_expenses(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        100, ge=1, le=200, description="Max number of items to return (page size)"
    ),
):
    """
    Retrieves all planned expenses for the authenticated user with pagination.
    """
    statement = (
        select(PlannedExpense)
        .where(PlannedExpense.user_id == current_user.id)
        .order_by(PlannedExpense.aprox_date)
        .offset(skip)
        .limit(limit)
    )
    planned_expenses = db.exec(statement).all()
    return planned_expenses


@router.get(
    "/{planned_expense_id}",
    response_model=PlannedExpensePublic,
    status_code=status.HTTP_200_OK,
)
async def get_planned_expense_by_id(
    planned_expense: Annotated[
        PlannedExpense, Depends(check_planned_expense_belongs_to_user)
    ],
):
    """
    Retrieves a single planned expense by its ID, ensuring ownership.
    """
    return planned_expense


@router.patch(
    "/{planned_expense_id}",
    response_model=PlannedExpensePublic,
    status_code=status.HTTP_200_OK,
)
async def update_planned_expense(
    planned_expense: Annotated[
        PlannedExpense, Depends(check_planned_expense_belongs_to_user)
    ],
    update_data: PlannedExpenseUpdate,
    db: SessionDep,
):
    """
    Partially update an existing planned expense, ensuring ownership.
    """
    updated_fields = update_data.model_dump(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(planned_expense, key, value)

    try:
        db.add(planned_expense)
        db.commit()
        db.refresh(planned_expense)
        return planned_expense
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity Error updating planned expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating planned expense due to data " "integrity issue.",
        )
    except Exception as e:
        db.rollback()
        print(f"Error updating planned expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating "
            "the planned expense.",
        )


@router.delete("/{planned_expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planned_expense(
    planned_expense: Annotated[
        PlannedExpense, Depends(check_planned_expense_belongs_to_user)
    ],
    db: SessionDep,
):
    """
    Deletes a planned expense by its ID, ensuring ownership.
    """
    db.delete(planned_expense)
    db.commit()
