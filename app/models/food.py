from datetime import datetime
from pydantic import Field
from app.models.common import MongoBaseModel, TimestampModel, DeletableModel, PyObjectId

class UserFood(MongoBaseModel, TimestampModel, DeletableModel):
    userId: PyObjectId
    name: str = Field(...)
    caloriesPerGram: float = Field(...)
    defaultQuantity: float = Field(...)

class FoodConsumption(MongoBaseModel, TimestampModel, DeletableModel):
    userId: PyObjectId
    userActivityId: PyObjectId
    userFoodId: PyObjectId
    dateAndTime: datetime = Field(...)
    quantity: float = Field(...)
    totalCalories: float = Field(..., description="quantity * caloriesPerGram")
