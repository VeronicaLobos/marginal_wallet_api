from typing import List, Optional
from datetime import datetime
import enum
from fastapi import FastAPI, Depends
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

#### This section is for the database design and connection

# Define the database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/marginal-wallet"

# Create the database engine
engine = create_engine(DATABASE_URL)

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
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False)
    password: str

    categories: List["Category"] = Relationship(back_populates="user")
    transactions: List["Transaction"] = Relationship(back_populates="user")
    planned_expenses: List["PlannedExpense"] = Relationship(back_populates="user")

class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_type: CategoryType = Field(nullable=False)
    Counterparty: str = Field(nullable=False)

    user: "User" = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")

class Transaction(SQLModel, table=True):
    id: int = Field(primary_key=True)
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
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: Optional[datetime] = Field(nullable=True)
    value: float = Field(nullable=False)
    currency: CurrencyType = Field(nullable=False)
    frequency: FrequencyType = Field(nullable=False)

    user: "User" = Relationship(back_populates="planned_expenses")

class Activity_log(SQLModel, table=True):
    id: int = Field(primary_key=True)
    transaction_id: int = Field(foreign_key="transaction.id", unique=True)
    description: str = Field(nullable=False)

    transaction: "Transaction" = Relationship(back_populates="activity_log")


def create_db_and_tables():
    """
    Create the database and tables if they do not exist.
    """
    SQLModel.metadata.create_all(engine)
    print("Database tables created (or checked)")


def get_session():
    """
    Dependency to get a database session.
    """
    with Session(engine) as session:
        yield session


## FastAPI app setup

app = FastAPI()

# Add a startup event to create the database and tables (using lambda)
#app.add_event_handler("startup", lambda: create_db_and_tables())
app.add_event_handler("startup", lambda: print("FastAPI started!"))


# Define the root endpoint
@app.get("/")
def home():
    """
    This is the root endpoint of the FastAPI app.
    It returns a simple message.
    TODO: Add a summary of what the app is intended for.
    """
    return {"message": "Welcome to the Marginal Wallet API!"}


# Example route with session dependency
@app.get("/users/me")
async def read_current_user(session: Session = Depends(get_session)):
    # For now, let's just return a placeholder
    return {"user_id": "current_user_id", "session_active": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002)
