from typing import Annotated, List
from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session

from auth.auth import get_current_active_user
from config.database import SessionDep
from dependencies import check_activity_log_belongs_to_user

from schema.activity_log import ActivityLog, ActivityLogPublic, ActivityLogUpdate
from schema.movement import Movement
from schema.user import User

# APIRouter instance for activity log operations
router = APIRouter(prefix="/activity_logs", tags=["activity_logs"])


@router.get(
    "/list", response_model=List[ActivityLogPublic], status_code=status.HTTP_200_OK
)
async def list_activity_logs(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: SessionDep,
    skip: int = Query(0, ge=0, description="Number of items to skip (offset)"),
    limit: int = Query(
        100, ge=1, le=200, description="Max number of items to return (page size)"
    ),
):
    """
    Retrieve all activity logs for the authenticated user's
    movements with pagination.

    This endpoint returns a list of ActivityLogPublic instances,
    associated with the authenticated user's movements. When no
    results are found, it returns an empty list.
    """
    statement = (
        select(ActivityLog)
        .join(Movement)
        .where(Movement.user_id == current_user.id)
        .order_by(ActivityLog.id)
        .offset(skip)
        .limit(limit)
    )
    activity_logs = db.exec(statement).all()

    return activity_logs


@router.get(
    "/{activity_log_id}",
    response_model=ActivityLogPublic,
    status_code=status.HTTP_200_OK,
)
async def get_activity_log_by_id(
    activity_log: Annotated[ActivityLog, Depends(check_activity_log_belongs_to_user)],
):
    """
    Retrieve a single activity log by its ID,
    ensuring ownership via its associated movement.
    """
    return activity_log


@router.patch(
    "/{activity_log_id}",
    response_model=ActivityLogPublic,
    status_code=status.HTTP_200_OK,
)
async def update_activity_log(
    activity_log: Annotated[ActivityLog, Depends(check_activity_log_belongs_to_user)],
    update_data: ActivityLogUpdate,
    db: SessionDep,
):
    """
    Partially updates an existing activity log, ensuring ownership.
    """
    updated_fields = update_data.model_dump(exclude_unset=True)
    for key, value in updated_fields.items():
        setattr(activity_log, key, value)

    try:
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log
    except IntegrityError as e:
        db.rollback()
        print(f"Integrity Error updating activity log: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating activity log due to data integrity issue.",
        )
    except Exception as e:
        db.rollback()
        print(f"Error updating activity log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the activity log.",
        )


@router.delete("/{activity_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity_log(
    activity_log: Annotated[ActivityLog, Depends(check_activity_log_belongs_to_user)],
    db: SessionDep,
):
    """
    Delete an activity log by its ID, ensuring ownership.
    """
    db.delete(activity_log)
    db.commit()
