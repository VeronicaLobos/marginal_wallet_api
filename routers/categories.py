from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from auth.auth import get_current_active_user
from config.database import SessionDep
from dependencies import check_category_belongs_to_user

from schema.category import CategoryCreate, CategoryPublic, Category, CategoryUpdate
from schema.transaction import MovementPublic, Movement, MovementCreate
from schema.user import User

# APIRouter instance for category operations
router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.post("/", response_model=CategoryPublic,
             status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
    ):
    """
    Endpoint to create a new category.

    This endpoint expects a POST request with an instance
    of CategoryCreate, which includes the category type (enum)
    and counterparty (to/from whom).
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


@router.get("/", response_model=List[CategoryPublic],
                            status_code=status.HTTP_200_OK)
async def get_categories(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
    skip: int = Query(0, ge=0,
            description="Number of items to skip (offset)"),
    limit: int = Query(100, ge=1, le=200,
            description="Max number of items to return (page size)")
):
    """
    Endpoint to retrieve all categories for the current user.

    This endpoint returns a list of CategoryPublic instances,
    which include the category type, counterparty, and user ID.
    """
    categories_statement = (select(Category)
                            .where(Category.user_id == current_user.id)
                            .order_by(Category.category_type,
                                      Category.counterparty)
                            .offset(skip)
                            .limit(limit))
    categories = db.exec(categories_statement).all()

    return categories


@router.get("/{category_id}", response_model=CategoryPublic,
                                    status_code=status.HTTP_200_OK)
async def get_category(
    category: Annotated[Category, Depends(check_category_belongs_to_user)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep
):
    """
    Endpoint to retrieve a specific category by its ID.

    This endpoint returns a CategoryPublic instance,
    which includes the category type, counterparty, and user ID.
    If the category does not belong to the current user,
    it raises a 404 error.
    """
    return category


@router.patch("/{category_id}", response_model=CategoryPublic,
                                    status_code=status.HTTP_200_OK)
async def update_category(
    category: Annotated[Category, Depends(check_category_belongs_to_user)],
    update: CategoryUpdate,
    db: SessionDep):
    """
    Endpoint to partially update an existing category.
    """
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400,
            detail="Category update failed: duplicate "
                   "entry or invalid data.")
    except Exception as e:
        db.rollback()
        print(f"Error updating category: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while updating the category.")


@router.delete("/{category_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category: Annotated[Category, Depends(check_category_belongs_to_user)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep):
    """
    Endpoint to delete a category.

    Only categories that belong to the current user
    and have no associated movements can be deleted.
    """
    if category.movements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with associated movements."
        )
    try:
        db.delete(category)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400,
            detail="Category deletion failed: Integrity error, "
                   "possibly due to foreign key constraints.")
    except Exception as e:
        db.rollback()
        print(f"Error deleting category: {e}")
        raise HTTPException(status_code=500,
            detail="An error occurred while deleting the category.")


### Endpoint to retrieve all movements for a specific category

@router.get("/{category_id}/movements",
            response_model=List[MovementPublic],
            status_code=status.HTTP_200_OK)
async def get_category_movements(
    category: Annotated[Category, Depends(check_category_belongs_to_user)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
    skip: int = Query(0, ge=0,
            description="Number of items to skip (offset)"),
    limit: int = Query(100, ge=1, le=200,
            description="Max number of items to return (page size)")
):
    """
    Endpoint to retrieve all movements for a specific category
    type ("Minijob", "Freelance", "Commission", or "Expenses").

    This endpoint returns a list of MovementPublic instances,
    which include the movement date, value, currency, and payment method.
    """
    movements_statement = (select(Movement)
                           .where(Movement.category_id == category.id)
                           .where(Movement.user_id == current_user.id)
                           .order_by(Movement.movement_date.desc())
                           .offset(skip)
                           .limit(limit))
    movements = db.exec(movements_statement).all()

    return movements


@router.post("/{category_id}/movements",
             response_model=MovementPublic,
             status_code=status.HTTP_201_CREATED)
async def create_category_movement(
        category: Annotated[Category, Depends(check_category_belongs_to_user)],
        movement: MovementCreate,
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: SessionDep
):
    """
    Endpoint to create a new movement (a transaction).

    This endpoint expects a POST request with an instance
    of MovementCreate, which includes the date, payment method,
    value, and currency of the movement.
    The category_id is sent as a path parameter to associate
    the movement with a specific category.
    """
    # Creates a new movement instance, by unpacking the data from
    # the request body into a dictionary and adding the user id
    # and category id to it.
    new_movement = Movement(
        **movement.model_dump(),
        user_id=current_user.id,
        category_id=category.id
    )
    try:
        db.add(new_movement)
        db.commit()
        db.refresh(new_movement)
        return new_movement

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movement creation failed: duplicate entry or invalid data."
        )
    except Exception as e:
        db.rollback()
        print(f"Error creating movement: {e}") # for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the movement."
        )
