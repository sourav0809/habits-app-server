from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateFoodRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    calories_per_gram: float = Field(..., gt=0)
    default_quantity: float = Field(default=100.0, gt=0)

class LogFoodRequest(BaseModel):
    food_id: str = Field(..., description="ID of the food item from catalog")
    quantity: float = Field(..., gt=0)
    log_time: Optional[datetime] = Field(default=None)

class UpdateFoodLogRequest(BaseModel):
    quantity: float = Field(..., gt=0)
    log_time: Optional[datetime] = Field(default=None)
