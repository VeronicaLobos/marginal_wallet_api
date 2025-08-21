import calendar
import os
from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
import json
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, extract

from auth.rate_limit import limiter
from auth.auth import (get_current_active_user,
                       get_password_hash, verify_password, authenticate_user, create_access_token)
from config.database import SessionDep
from schema.activity_log import ActivityLog

from schema.auth import Token
from schema.enums import CategoryType

from schema.user import (UserPublic, User, UserCreate,
                         UserDeleteConfirmation, UserNameEmailUpdate,
                         UserPasswordUpdate, UserDashboard,
                         MinijobsBalanceSummary,
                         CategoryTypeBalanceSummary)
from schema.category import Category
from schema.movement import Movement, MovementPublic

from google.generativeai import GenerativeModel

load_dotenv()

# APIRouter instance for user operations
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=UserPublic,
             status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    request: Request,
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
@limiter.limit("10/minute")
async def update_password(
        request: Request,
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
@limiter.limit("10/minute")
async def delete_user(
    request: Request,
    # Changed to accept password via a custom header
    password_confirmation: Annotated[str, Header(
        alias="X-Confirm-Password",
        description="User's current password for deletion confirmation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to delete the authenticated user.

    This endpoint expects the user's password in the 'X-Confirm-Password' header
    for confirmation. It verifies the password and deletes the user and all
    associated data from the database.

    Any associated movements, categories, planned expenses and
    activity logs that belong to the user will also be deleted.
    """
    if not verify_password(password_confirmation, # Use the password from the header
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


@router.get("/me/insights", status_code=status.HTTP_200_OK)
async def read_insights(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: SessionDep
        ):
    """
    Endpoint to retrieve the user's insights.

    By fetching all the user Movements, this endpoint
    can provide insights such as spending patterns,
    income sources, and financial trends for the last
    three months.
    """
    # Ensures the API key is set in the environment
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google API key not set in environment variables."
            )
    except Exception as e:
        print(f"Error configuring Google Generative AI: {e}")

    # Fetches all movements for the user from the last three months
    last_three_months = datetime.now() - timedelta(days=90)
    movements_statement = ((select(Movement)
                .where(Movement.user_id == current_user.id)
                .where(Movement.movement_date >= last_three_months)
                .order_by(Movement.movement_date)))
    movements = db.exec(movements_statement).all()

    if not movements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movements found for the last three months."
        )

    # Prepares the movements data for the prompt
    # which will include the category type, counterparty,
    # all the movement details except the user_id and movement_id,
    # the date formatted as YYYY-MM-DD,
    # and activity_log if there is one associated with the movement
    movements_data_for_prompt = []

    for movement in movements:
        category_statement = db.get(Category, movement.category_id)
        activity_log_statement = db.get(ActivityLog, movement.id)

        movement_data = {
            "date": movement.movement_date.strftime("%Y-%m-%d"),
            "value": movement.value,
            "currency": movement.currency,
            "payment_method": movement.payment_method,
            "category": category_statement.category_type,
            "stakeholder": category_statement.counterparty,
            "activity_log": activity_log_statement.description
                            if activity_log_statement else None
        }

        movements_data_for_prompt.append(movement_data)

    # Converts the list of dictionaries to a JSON string for stable parsing
    json_data = json.dumps(movements_data_for_prompt, indent=2)

    # Create the prompt for the Google Generative AI
    prompt = f"""
        You are a financial analyst providing a summary of a user's
        recent financial movements.

            **Your final output MUST be a text-based financial summary.
            DO NOT provide any code or a Python function in your response.**
            Act as a financial analyst and provide the summary as prose.

            Analyze the following financial data for the last three months.
            The data is a list of dictionaries, where each dictionary
            represents a financial movement with its date, value, counterparty,
            and category. Some movements may also have an 'activity_log' with
            notes and a timestamp, providing additional context.

            **Instructions:**
            1.  Provide a general overview of the user's financial activity for
            the last three months, incorporating details from the activity logs
            where relevant.
            2.  Calculate and summarize the total income (positive values) and
            total expenses (negative values) for each unique stakeholder.
            3.  The final output should be a clear, concise, and easy-to-read
            summary. Format the summary using bullet points or a numbered list.

            **Financial Data:**
            {json_data}
        """

    # Call the Google Generative AI API to get insights
    try:
        model = GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        # Check if the response contains text and return it
        if response.text:
            return {"insights": response.text}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate insights from the AI."
            )

    except Exception as e:
        print(f"Error during insights generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating insights."
        )
