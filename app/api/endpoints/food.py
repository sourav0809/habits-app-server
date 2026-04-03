from fastapi import APIRouter, Depends, Query, Body
from typing import List
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.food import UserFood, FoodConsumption
from app.services import food_service
from app.validation.food import CreateFoodRequest, LogFoodRequest, UpdateFoodLogRequest

router = APIRouter()

@router.get("/catalog", response_model=List[UserFood])
async def get_food_catalog(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve the user's predefined food items."""
    return await food_service.get_user_foods(str(current_user.id))

@router.post("/catalog", response_model=UserFood)
async def create_food_item(
    request: CreateFoodRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a new food item to the user's predefined catalog."""
    return await food_service.create_user_food(str(current_user.id), request)

@router.get("/logs", response_model=List[FoodConsumption])
async def get_food_logs(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve food consumption logs between two dates."""
    return await food_service.get_food_consumptions(str(current_user.id), start_date, end_date)

@router.post("/logs", response_model=FoodConsumption)
async def log_food_consumption(
    request: LogFoodRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Log food intake from the catalog."""
    return await food_service.log_food_consumption(str(current_user.id), request)

@router.patch("/logs/{log_id}", response_model=FoodConsumption)
async def update_food_log(
    log_id: str,
    request: UpdateFoodLogRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a food entry."""
    return await food_service.update_food_log(str(current_user.id), log_id, request)

@router.delete("/logs/{log_id}")
async def delete_food_log(
    log_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a food entry."""
    await food_service.delete_food_log(str(current_user.id), log_id)
    return {"detail": "Log deleted successfully"}
