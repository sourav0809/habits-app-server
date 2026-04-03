from fastapi import APIRouter, Depends, Body, Query
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.water import WaterConsumption
from app.services import water_service

router = APIRouter()

@router.get("/logs", response_model=List[WaterConsumption])
async def get_water_logs(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve water logs between two dates."""
    return await water_service.get_water_logs(str(current_user.id), start_date, end_date)

@router.post("/logs", response_model=WaterConsumption)
async def log_water(
    amount_ml: float = Body(..., embed=True),
    intake_time: Optional[datetime] = Body(None, embed=True),
    current_user: UserResponse = Depends(get_current_user)
):
    """Log water intake."""
    return await water_service.log_water(str(current_user.id), amount_ml, intake_time)
