from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from auth.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from config.database import create_db_and_tables, SessionDep
from schema.auth import Token
from schema.user import UserPublic, User, UserCreate

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
    #BUG FIX: session was not being passed to the authenticate_user function
    user = authenticate_user(form_data.username, form_data.password, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30) #TODO: load this from .env file
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.email}]
