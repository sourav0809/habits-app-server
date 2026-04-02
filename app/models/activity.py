from datetime import datetime
from pydantic import Field
from app.models.common import MongoBaseModel, TimestampModel, DeletableModel, PyObjectId

class UserActivity(MongoBaseModel, TimestampModel, DeletableModel):
    userId: PyObjectId
    date: datetime = Field(..., description="Represents a single day")
    totalCalories: float = Field(default=0.0)
    totalWaterMl: float = Field(default=0.0)
