import json
import os
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlmodel import select

from config.database import SessionDep
from schema.activity_log import ActivityLog
from schema.category import Category
from schema.movement import Movement
from schema.user import User

from google.generativeai import GenerativeModel
import google.generativeai as genai


# Configure the API key from environment variables once
try:
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")


def generate_financial_insights(current_user: User, db: SessionDep) -> str:
    """
    Generates financial insights for the user based on their movements
    from the last three months.

    Parameters:
        current_user: The authenticated user object.
        db: The database session.

    Returns a string containing the AI-generated financial summary.
    """
    # Fetch all movements for the user from the last three months
    last_three_months = datetime.now() - timedelta(days=90)
    movements_statement = (
        select(Movement)
        .where(Movement.user_id == current_user.id)
        .where(Movement.movement_date >= last_three_months)
        .order_by(Movement.movement_date)
    )
    movements = db.exec(movements_statement).all()

    if not movements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movements found for the last three months.",
        )

    # Prepare the movements data for the prompt
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
            "activity_log": (
                activity_log_statement.description if activity_log_statement else None
            ),
        }

        movements_data_for_prompt.append(movement_data)

    # Converts the list of dictionaries to a JSON string for stable parsing
    json_data = json.dumps(movements_data_for_prompt, indent=4)

    # Creates the prompt for the Google Generative AI
    prompt = f"""
        You are a financial analyst providing a summary of a user's
        recent financial movements as prose.

        Your final output must be a text-based financial summary.
        Do not provide any code or a Python function in your response.

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
            total expenses (negative values) for each unique category and
            counterparty.
        3.  The final output should be a clear, concise, and easy-to-read
            summary. Format the summary using bullet points or a numbered list.

        **Financial Data:**
        {json_data}
    """

    # Calls the Google Generative AI API to get insights
    try:
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Checks if the response contains text and return it
        if response.text:
            return response.text
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate insights from the AI.",
            )

    except Exception as e:
        print(f"Error during insights generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating insights.",
        )
