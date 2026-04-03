from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime
from app.api.deps import get_current_user
from app.models.user import UserResponse
from app.models.water import WaterConsumption
from app.services import water_service
from app.validation.water import LogWaterRequest, UpdateWaterLogRequest

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
    request: LogWaterRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Log water intake."""
    return await water_service.log_water(str(current_user.id), request)

@router.patch("/logs/{log_id}", response_model=WaterConsumption)
async def update_water_log(
    log_id: str,
    request: UpdateWaterLogRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a water entry."""
    return await water_service.update_water_log(str(current_user.id), log_id, request)

@router.delete("/logs/{log_id}")
async def delete_water_log(
    log_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a water entry."""
    await water_service.delete_water_log(str(current_user.id), log_id)
    return {"detail": "Log deleted successfully"}
