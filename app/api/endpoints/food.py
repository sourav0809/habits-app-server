from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.food import UserFood, FoodConsumption
from app.services import food_service

router = APIRouter()

@router.get("/catalog", response_model=List[UserFood])
async def get_food_catalog(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve the user's predefined food items."""
    return await food_service.get_user_foods(str(current_user.id))

@router.post("/catalog", response_model=UserFood)
async def create_food_item(
    name: str = Body(...),
    calories_per_gram: float = Body(...),
    default_quantity: float = Body(100.0),
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a new food item to the user's predefined catalog."""
    return await food_service.create_user_food(
        str(current_user.id), 
        name, 
        calories_per_gram, 
        default_quantity
    )

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
    food_id: str = Body(...),
    quantity: float = Body(...),
    log_time: Optional[datetime] = Body(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Log food intake from the catalog."""
    return await food_service.log_food_consumption(
        str(current_user.id), 
        food_id, 
        quantity, 
        log_time
    )
