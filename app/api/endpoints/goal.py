from fastapi import APIRouter, Depends, Body
from typing import Optional
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.goal import UserGoal
from app.services import goal_service

router = APIRouter()

@router.get("/", response_model=UserGoal)
async def get_goals(current_user: UserResponse = Depends(get_current_user)):
    """Get the current user's goals."""
    return await goal_service.get_user_goal(str(current_user.id))

@router.put("/", response_model=UserGoal)
async def update_goals(
    target_water: Optional[float] = Body(None),
    target_calories: Optional[float] = Body(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update current user's goals."""
    return await goal_service.update_user_goal(
        str(current_user.id), 
        target_water=target_water, 
        target_calories=target_calories
    )
