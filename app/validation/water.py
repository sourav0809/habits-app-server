from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LogWaterRequest(BaseModel):
    amount_ml: float = Field(..., gt=0)
    intake_time: Optional[datetime] = Field(default=None)

class UpdateWaterLogRequest(BaseModel):
    amount_ml: float = Field(..., gt=0)
    intake_time: Optional[datetime] = Field(default=None)
