from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, extract

from auth.auth import (get_current_active_user,
                       get_password_hash, verify_password)
from config.database import SessionDep
from schema.user import (UserPublic, User, UserCreate,
                         UserDeleteConfirmation)
from schema.category import CategoryPublic, Category
from schema.transaction import Movement, MovementPublic

# APIRouter instance for user operations
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/registration/", response_model=UserPublic)
async def register(user: UserCreate, db: SessionDep):
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


@router.get("/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Endpoint to retrieve the authenticated user's details.

    This endpoint returns the user's name, email, and ID.
    """
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to retrieve the user's categories and overall balance.

    This endpoint returns a list of the user's categories
    and their total calculated balance from all movements.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    categories = [CategoryPublic.model_validate(cat)
                    for cat in current_user.categories]

    balance = sum(movement.value for movement in current_user.movements)

    return {
        "categories": categories,
        "total_balance": balance
    }


@router.get("/me/minijobs_balance/", response_model=dict)
async def read_minijobs_balance(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep):
    """
    Endpoint to retrieve the user's balance for minijobs,
    for the current month and year.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    now = datetime.now()
    statement = (select(Movement).join(Category)
                .where(Movement.user_id == current_user.id)
                .where(Category.counterparty == "Minijob")
                .where(extract('month', Movement.date) == now.month)
                .where(extract('year', Movement.date) == now.year))
    minijobs_query = db.exec(statement).all()

    minijobs_movements = [MovementPublic.model_validate(mv) for mv in minijobs_query]

    minijobs_balance = sum(mv.value for mv in minijobs_movements)

    return {
        "minijobs_balance": minijobs_balance,
        "minijobs_movements": minijobs_movements
    }


@router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
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
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    if not verify_password(delete_confirmation.password,
                           current_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect password, "
                                   "cannot delete user account.")

    try:
        db.delete(current_user)
        db.commit()
        print(f"User {current_user.name} and associated "
              f"data deleted successfully.")
        return {"detail": f"User {current_user.name} and "
                           f"associated data deleted successfully."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,
            detail="User deletion failed: Integrity error, "
                   "possibly due to foreign key constraints.")
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500,
                        detail="An error occurred while deleting "
                               "the user and associated data.")
