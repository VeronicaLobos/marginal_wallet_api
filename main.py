import os
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from auth.auth import (authenticate_user,
                       create_access_token, get_current_active_user,
                       get_password_hash, verify_password)
from config.database import create_db_and_tables, SessionDep

from schema.auth import Token
from schema.user import (UserPublic, User, UserCreate,
                         UserDeleteConfirmation)
## need the following after dropping and recreating the database
from schema.category import CategoryCreate, CategoryPublic, Category
from schema.transaction import MovementCreate, MovementPublic
from schema.planned_expense import PlannedExpense
from schema.activity_log import ActivityLog

load_dotenv()

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def home():
    """
    This is the root endpoint of the FastAPI app.
    It returns a simple message.
    """
    return {"greeting": "Welcome to the Marginal Wallet API!",
            "version": "1.0",
            "description": "Marginal Wallet is a web application"
                       " that allows user to keep track of their"
                       " marginal income and expenses."}

@app.post("/users/registration/", response_model=UserPublic)
def register(user: UserCreate, db: SessionDep):
    """
    User registration endpoint.

    Password is hashed before creating a user instance.

    A POST request with an instance of UserRegistration
    is expected.
    The response will be an instance of UserResponse
    (which excludes the password for security reasons).
    """
    hashed_pass = get_password_hash(user.password)
    updated_user = user.model_copy(update={"password": hashed_pass})
    db_user = User.model_validate(updated_user)
    print("---------")
    print(db_user)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        print(e)
        # Handle duplicate entries
        db.rollback()
        raise HTTPException(status_code=400,
                            detail="Username or email already exists")
    except Exception as e:
        # Handle any other exceptions and print the error for debugging
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500,
                            detail="An error occurred while creating the user")

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep) -> Token:
    """
    Login endpoint to authenticate a user and return an access token.
    This endpoint expects a POST request with form data containing
    the username and password of the user to authenticate
    """
    # Call the authenticate_user function to verify credentials
    user = authenticate_user(form_data.username, form_data.password,
                             session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    secret_key = os.environ.get("SECRET_KEY")
    algorithm = os.environ.get("ALGORITHM")
    if not secret_key or not algorithm:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: "
                   "Missing secrets for token generation."
        )

    # Create an access token with an expiration time and
    # the user's email as subject
    access_token_expires = timedelta(minutes=int(os.environ
                        .get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.email}]


@app.delete("/users/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    delete_confirmation: UserDeleteConfirmation,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to delete the authenticated user.

    It removes the user and all their associated data (categories, transactions,
    planned expenses, and activity logs) from the database due to cascading deletes.
    The user must provide their password for confirmation in the request body.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    # call verify_password from auth/auth.py
    if not verify_password(delete_confirmation.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Incorrect password, cannot delete user account.")

    try:
        db.delete(current_user)
        db.commit()
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

#### Category Endpoints ####

from schema.category import CategoryCreate, CategoryPublic
@app.post("/categories/", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate,
                    current_user: Annotated[User, Depends(get_current_active_user)],
                    db: SessionDep
                    ):
    """
    Endpoint to create a new category.

    This endpoint expects a POST request with an instance of CategoryCreate,
    which includes the category type and counterparty.
    Requires current_user since the category is associated with a user.
    Requires a valid session to interact with the database.

    Returns the created category as an instance of CategoryPublic.
    """
    # Ensure the category is associated with the current user
    db_category = Category(**category.model_dump(), user_id=current_user.id)
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError: {e}") # for debugging
        raise HTTPException(status_code=400,
            detail="Category creation failed: duplicate entry or invalid data.")
    except Exception as e:
        db.rollback()
        print(f"Error creating category: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while creating the category.")
