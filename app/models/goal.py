from pydantic import Field
from app.models.common import MongoBaseModel, TimestampModel, DeletableModel, PyObjectId

class UserGoal(MongoBaseModel, TimestampModel, DeletableModel):
    userId: PyObjectId = Field(..., description="unique")
    targetWaterMl: float = Field(default=0.0)
    targetCalories: float = Field(default=0.0)
