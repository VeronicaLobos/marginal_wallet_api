
## 0. Imports section
"""
The following imports are used in the code:

    - `enum`: Provides support for enumerations, which are a
set of symbolic names bound to unique, constant values.
    - `os`: Provides a way of using operating system-dependent
functionality like reading environment variables.
    - `contextlib`: Provides utilities for working with context managers.
- -- `asynccontextmanager`: A decorator for defining asynchronous
context managers.
    - `datetime`: Supplies classes for manipulating dates and times.
- -- `timedelta`: Represents a duration, the difference between
two dates or times.
- -- `timezone`: A class for dealing with time zones.
    - `dotenv`: Reads key-value pairs from a `.env` file and adds
them to the environment variables.
- -- `load_dotenv`: A function that loads environment variables
from a `.env` file.
    - `fastapi`: A modern, fast (high-performance), web framework for
building APIs with Python 3.6+ based on standard Python type hints.
- -- `Depends`: A dependency injection system for FastAPI.
- -- `HTTPException`: An exception class for HTTP errors.
- -- `Security`: A class for handling security-related
dependencies in FastAPI, to use in OPenAPI docs.
    - `fastapi.security`: A module that provides security
utilities for FastAPI.
- -- `HTTPBearer`: A class that provides a way to handle
HTTP Bearer authentication.
- -- `HTTPAuthorizationCredentials`: A class that represents
the credentials for HTTP authorization.
- -- `OAuth2PasswordBearer`: A class that provides a way to handle
OAuth2 password flow, a standard for user authentication.
    - `jose`: A library for creating and verifying JSON Web Tokens (JWT).
- -- `JWTError`: An exception class for JWT errors. Handles errors
such as invalid tokens, expired tokens, etc.
- -- `jwt`: A library for encoding and decoding JSON Web Tokens (JWT).
    - `passlib`: A password hashing library that provides a way to
hash and verify passwords.
- -- `bcrypt`: A password hashing function that is designed to
be slow to prevent brute-force attacks.
    - `pydantic`: A data validation and settings management library
based on Python type annotations.
- -- `BaseModel`: A base class for creating Pydantic models, which
are used for data validation and serialization.
    - `SQLModel`: A library for SQL databases in Python, which provides
a way to define models and interact with the database.
- -- `Field`: A class for defining fields in SQLModel models.
- -- `Relationship`: A class for defining relationships between
SQLModel models.
- -- `Session`: A class for managing database sessions in SQLModel.
It is used with a context manager to handle transactions.
- -- `create_engine`: A function for creating a database engine,
which is used to connect to the database.
- -- `inspect`: A function for inspecting the database schema,
which is used to check if the tables exist at startup.
- -- `select`: A function for creating SQL SELECT statements.
    - `typing`: A standard library module that provides support for
type hints and annotations.
- -- `Annotated`: A type hint that allows you to add metadata
to a type, such as specifying dependencies in FastAPI.
For now, it's being used to avoid code duplication.
- -- `List`: A generic type for lists, used for type hinting.
- -- `Optional`: A type hint that indicates a value can be of a
specified type or None.
"""

import enum
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import (OAuth2PasswordBearer,
            HTTPBearer, HTTPAuthorizationCredentials)
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import (Field, Relationship, Session,
            SQLModel, create_engine, inspect, select)
from typing import Annotated, List, Optional

load_dotenv()

## 1. Database models section

# 1.1 Define the categorical variables (enums)
class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    bank_transfer = "Bank Transfer"

class CurrencyType(str, enum.Enum):
    euro = "EURO"
    usd = "USD"

class FrequencyType(str, enum.Enum):
    weekly = "Weekly"
    monthly = "Monthly"
    quarterly = "Quarterly"
    biannually = "Biannually"
    yearly = "Yearly"
    one_time = "One Time"

# 1.2 Define the SQLModel classes (models)
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password: str

    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_type: CategoryType = Field(nullable=False)
    counterparty: str = Field(nullable=False)

    user: "User" = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    date: str = Field(nullable=False)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    payment_method: PaymentMethodType = Field(nullable=False)

    user: "User" = Relationship(back_populates="transactions")
    category: "Category" = Relationship(back_populates="transactions")
    activity_log: Optional["ActivityLog"] = Relationship(back_populates="transaction")

class PlannedExpense(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    date: Optional[datetime] = Field(nullable=True)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)

    user: "User" = Relationship(back_populates="planned_expenses")

class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)
    description: str = Field(nullable=False)

    transaction: "Transaction" = Relationship(back_populates="activity_log")


## 2. Database setup section

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    """
    Create the database and tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)
    print("Database tables created (or checked)")

def get_session():
    """
    Dependency to get a database session.
    This function is used to create a new session for each request.
    """
    with Session(engine) as session:
        yield session


## 3. API section

# 3.0 FastAPI app setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event for the FastAPI app.
    It checks if the database and tables exist at startup,
    and creates them if they do not.
    """
    if not inspect(engine).has_table("user"):
        # If the table does not exist, create all tables
        print("Creating database tables...")
        create_db_and_tables()
    print("FastAPI started!")
    yield
    print("FastAPI stopped!")

security_schemes = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

app = FastAPI(lifespan=lifespan, security_schemes=security_schemes)

db_dependency = Annotated[Session, Depends(get_session)]

# 3.1 Define the root endpoint

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

# 3.2 User registration endpoint

class UserRegistration(BaseModel):
    """
    Input, data sent by the client to register a new user.
    """
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    """
    Output, data sent back to the client after user registration.
    Safely excludes the password field.
    """
    id: int
    name: str
    email: str

@app.post("/users/registration/", response_model=UserResponse)
def register(user: UserRegistration, db: db_dependency):
    """
    User registration endpoint.

    Password is hashed before creating a user instance.

    A POST request with an instance of UserRegistration
    is expected.
    The response will be an instance of UserResponse
    (which excludes the password for security reasons).
    """
    hashed_pass = bcrypt.hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_pass)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponse(id=new_user.id,
                            name=new_user.name, email=new_user.email)
    except IntegrityError:
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

# 3.3 User authentication endpoint

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINS = 30

"""
- oauth2_scheme: This correctly points Swagger UI to the login 
endpoint for documenting the OAuth2 password flow, allowing 
users to get a token via username/password in the docs.
- bearer_scheme: This is the actual dependency used to extract 
the Bearer token from incoming requests for protected routes.
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")
bearer_scheme = HTTPBearer()

def generate_access_token(payload: dict) -> str:
    """
    Function to create a JWT token for user authentication.

    Receives a dictionary payload as input, which contains
    the user's email as the subject and the expiration time:
    {"sub": user email, "exp": expiration time (in minutes)}

    - The payload is copied to avoid modifying the original one.
    - The expiration time is set to the current time plus
    the specified number of minutes.
    - The payload is updated with the expiration timestamp.
    - The payload is encoded using the secret key and algorithm.

    The returned JWT token is a string.
    """
    payload_to_encode = payload.copy()
    expire = (datetime.now(timezone.utc) +
              timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS))
    payload_to_encode.update({"exp": expire})
    encoded_jwt_token = jwt.encode(payload_to_encode,
                       SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt_token

def get_current_user(db: db_dependency,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    """
    Dependency to get the current authenticated user from a JWT token.

    Receives the token from the Authorization header and
    the database session (to query the user with the info in the payload).

    - Creates a response exception for invalid credentials.
    - Decodes the JWT token using the secret key and algorithm.
    - Extracts the subject from the token payload (user email).
    - If the email is None, raises the credentials exception.
    - If the token is invalid, raises the credentials exception.
    - Makes a dictionary with the email (a standardized way to pass
    data around in case we want to add more fields in the future).
    - Queries the database for the user with the email.
    - If the user is None, raises the credentials exception.

    Returns the authenticated User object, containing all the fields
    (including the hashed password).

    Raises a HTTPException (401) if the token is invalid, expired,
    or the user doesn't exist, or if the email or user is None.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = {"email": email}
    except JWTError:
        raise credentials_exception

    user = (db.exec(select(User).where(User.email == token_data["email"]))
            .first())
    if user is None:
        raise credentials_exception
    return user

class UserLogin(BaseModel):
    """
    Data sent by the client to log in a user.
    It contains the email and unhashed password.
    """
    email: str
    password: str

class Token(BaseModel):
    """
    Data sent back to the client after user login.
    It contains the access token and its type.
    """
    access_token: str
    token_type: str

@app.post("/users/login/", response_model=Token)
def authenticate_user(user: UserLogin, db: db_dependency):
    """
    User login endpoint.

    A POST request with an instance of UserLogin is expected.

    - Retrieves the user from the database using the email.
    - If the user does not exist or the email or password is
      incorrect, raises a HTTPException (401) with an error message.
    - If the user exists, creates a JWT token with the user's
      email as the subject.
    - The token is generated using the generate_access_token function.
    - An instance of Token is created with the access token and
      its type (bearer).

    The response will be the instance of Token.
    """
    db_user = db.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = generate_access_token(payload={"sub": db_user.email})
    token = Token(access_token=access_token, token_type="bearer")
    return token

# 3.4 User profile endpoint
@app.get(
    "/users/me/",
    response_model=UserResponse,
    dependencies=[Depends(bearer_scheme), Depends(get_current_user)],
)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    User profile endpoint.

    A GET request is expected with the Authorization header
    containing the JWT token.

    The response will be an instance of UserResponse
    (which excludes the password for security reasons).
    """
    return UserResponse(id=current_user.id,
                        name=current_user.name, email=current_user.email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002)
