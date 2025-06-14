import calendar
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, extract

from auth.auth import (get_current_active_user,
                       get_password_hash, verify_password)
from config.database import SessionDep
from schema.enums import CategoryType

from schema.user import (UserPublic, User, UserCreate,
                         UserDeleteConfirmation, UserNameEmailUpdate,
                         UserPasswordUpdate, UserDashboard,
                         MinijobsBalanceSummary,
                         CategoryTypeBalanceSummary)
from schema.category import Category
from schema.movement import Movement, MovementPublic

# APIRouter instance for user operations
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=UserPublic,
             status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: SessionDep):
    """
    User registration endpoint.

    This endpoint expects a POST request with an instance
    of UserCreate, which includes the user's name,
    email, and password. It hashes the password and
    creates a new user in the database.
    """
    hashed_pass = get_password_hash(user.password)
    updated_user = user.model_copy(update={"password": hashed_pass})
    db_user = User.model_validate(updated_user)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=400,
                detail="Username or email already exists")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500,
                detail="An error occurred while creating the user")


@router.get("/me", response_model=UserPublic,
            status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Endpoint to retrieve the authenticated user's details.

    This endpoint returns the user's name, email, and ID.
    """
    return current_user


@router.patch("/me/update_details",
                response_model=UserPublic,
            status_code=status.HTTP_200_OK)
async def update_name_email(
    user_update: UserNameEmailUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to update the authenticated user's details.

    This endpoint expects a PATCH request with an instance
    of UserNameEmailUpdate, which includes the user's
    name and/or email. It updates the user's details
    in the database if the provided values are not None.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
            detail="Username or email already in use by another user.")
    except Exception as e:
        db.rollback()
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while updating the user details.")


@router.patch("/me/update_password",
              status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
        password_update: UserPasswordUpdate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: SessionDep):
    """
    Endpoint to update the authenticated user's password.

    Checks if the current password is correct,
    and if the new password matches the confirmation.
    If both checks pass, it hashes the new password
    and updates the user's password in the database.
    """
    if not verify_password(password_update.current_password,
                           current_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect current password."
        )

    if password_update.new_password != password_update.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match."
        )

    hashed_new_pass = get_password_hash(password_update.new_password)
    current_user.password = hashed_new_pass
    try:
        db.add(current_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
            detail="Password update failed: Integrity error.")
    except Exception as e:
        db.rollback()
        print(f"Error updating password: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while updating the password.")


@router.delete("/me",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    delete_confirmation: UserDeleteConfirmation,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to delete the authenticated user.

    This endpoint expects a POST request with an instance
    of UserDeleteConfirmation, which includes the user's
    password for confirmation. It verifies the password
    and deletes the user and all associated data from the database.

    Any associated movements, categories, planned expenses and
    activity logs that belong to the user will also be deleted.
    """
    if not verify_password(delete_confirmation.password,
                           current_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect password, "
                                   "cannot delete user account.")

    try:
        db.delete(current_user)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {e}")  # for debugging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while deleting"
                                   " the user account.")


@router.get("/me/dashboard/", response_model=UserDashboard,
            status_code=status.HTTP_200_OK)
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Endpoint to retrieve the user's overall balance,
    number of movements, and number of categories.
    """
    total_balance = sum(movement.value for movement
                        in current_user.movements)
    num_categories = len(current_user.categories)
    num_movements = len(current_user.movements)

    return UserDashboard(
        balance=total_balance,
        num_categories=num_categories,
        num_movements=num_movements
    )


@router.get("/me/minijobs_balance/",
            response_model=MinijobsBalanceSummary,
            status_code=status.HTTP_200_OK)
async def read_minijobs_balance(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
    ):
    """
    Endpoint to retrieve the user's balance for minijobs,
    for the current month and year.
    """
    now = datetime.now()
    minijobs_statement = (
        select(Movement)
        .join(Category)
        .where(Category.category_type == "Minijob")
        .where(Movement.user_id == current_user.id)
        .where(extract('month', Movement.movement_date) == now.month)
        .where(extract('year', Movement.movement_date) == now.year)
    )
    minijobs_query = db.exec(minijobs_statement).all()

    minijobs_movements_current_month =\
        [MovementPublic.model_validate(mv) for mv in minijobs_query]

    minijobs_balance = sum(mv.value for mv in
                           minijobs_movements_current_month)

    return MinijobsBalanceSummary(
        minijobs_balance=minijobs_balance,
        max_earnings="556€",
        current_month=calendar.month_name[now.month],
        current_year=now.year
    )


@router.get("/me/{category_type}/balance/",
            response_model=CategoryTypeBalanceSummary,
            status_code=status.HTTP_200_OK)
async def read_category_balance(
    category_type: CategoryType,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep):
    """
    Endpoint to retrieve the user's overall balance for a specific
    category type for the current month and year.
    """
    now = datetime.now()
    category_statement = (select(Movement)
                          .join(Category)
                          .where(Category.category_type == category_type)
                          .where(Movement.user_id == current_user.id)
        .where(extract('month', Movement.movement_date) == now.month)
        .where(extract('year', Movement.movement_date) == now.year)
                          )
    category_query = db.exec(category_statement).all()

    category_movements = [MovementPublic.model_validate(movement)
                            for movement in category_query]
    category_balance = sum(mv.value for mv in category_movements)

    return CategoryTypeBalanceSummary(
        category_type=str(category_type),
        balance=category_balance,
        current_month=calendar.month_name[now.month],
        current_year=now.year
    )
