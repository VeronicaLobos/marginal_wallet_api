from typing import List, Optional
from datetime import datetime
import enum
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

#### This section is for the database models

# Define the categorical variables (enums)
class CategoryType(str, enum.Enum):
    minijob = "Minijob"
    freelance = "Freelance"
    commission = "Commission"
    expenses = "Expenses"

class PaymentMethodType(str, enum.Enum):
    cash = "Cash"
    paypal = "Paypal"
    banktransfer = "Bank Transfer"

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

# Define the SQLModel classes (models)
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False)
    password: str

    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    category_type: CategoryType = Field(nullable=False)
    Counterparty: str = Field(nullable=False)

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
    activity_log: Optional["Activity_log"] = Relationship(back_populates="transaction")

class PlannedExpense(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    date: Optional[datetime] = Field(nullable=True)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)

    user: "User" = Relationship(back_populates="planned_expenses")

class Activity_log(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)
    description: str = Field(nullable=False)

    transaction: "Transaction" = Relationship(back_populates="activity_log")


#### This section is for the database setup

# TODO: Use environment variables for sensitive data
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/marginal-wallet"
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


## FastAPI app setup

@asynccontextmanager
async def lifespan():
    """
    Lifespan event for the FastAPI app.
    It creates the database and tables when the app starts.
    """
    create_db_and_tables()
    print("FastAPI started!")
    yield
    print("FastAPI stopped!")

app = FastAPI(lifespan=lifespan)


# Define the root endpoint
@app.get("/")
def home():
    """
    This is the root endpoint of the FastAPI app.
    It returns a simple message.
    TODO: Add a summary of what the app is intended for.
    """
    return {"message": "Welcome to the Marginal Wallet API!"}


## User registration

class UserRegistration(BaseModel):
    """
    Data sent by the client to register a new user.
    """
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    """
    Data sent back to the client after user registration.
    Safely excludes the password field.
    """
    id: int
    name: str
    email: str

@app.post("/users/", response_model=UserResponse)
def register(user: UserRegistration, session: Session = Depends(get_session)):
    """
    User registration endpoint.

    Password is hashed before creating a user instance.

    A POST request with an instance of UserRegistration is expected.
    The response will be an instance of UserResponse.
    """
    hashed_pass = bcrypt.hash(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_pass)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)
    except IntegrityError:
        # Handle duplicate entries
        session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    except Exception as e:
        # Handle any other exceptions
        session.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002)
