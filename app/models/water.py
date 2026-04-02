from datetime import datetime
from pydantic import Field
from app.models.common import MongoBaseModel, TimestampModel, DeletableModel, PyObjectId

class WaterConsumption(MongoBaseModel, TimestampModel, DeletableModel):
    userId: PyObjectId
    userActivityId: PyObjectId
    amountMl: float = Field(...)
    dateAndTime: datetime = Field(...)
