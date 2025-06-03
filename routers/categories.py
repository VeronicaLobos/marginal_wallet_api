from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from auth.auth import get_current_active_user
from config.database import SessionDep
from schema.category import CategoryCreate, CategoryPublic, Category
from schema.user import User

# APIRouter instance for category operations
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=List[CategoryPublic])
def get_categories(current_user: Annotated[User, Depends(get_current_active_user)],
                   db: SessionDep):
    """
    Endpoint to retrieve all categories for the current user.

    This endpoint returns a list of CategoryPublic instances,
    which include the category type, counterparty, and user ID.
    """
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories


@router.post("/add/", response_model=CategoryPublic,
             status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate,
                    current_user: Annotated[User, Depends(get_current_active_user)],
                    db: SessionDep
                    ):
    """
    Endpoint to create a new category.

    This endpoint expects a POST request with an instance
    of CategoryCreate,
    which includes the category type and counterparty.
    """
    db_category = Category(**category.model_dump(),
                           user_id=current_user.id)
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError: {e}") # for debugging
        raise HTTPException(status_code=400,
            detail="Category creation failed: duplicate "
                   "entry or invalid data.")
    except Exception as e:
        db.rollback()
        print(f"Error creating category: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while creating the category.")
