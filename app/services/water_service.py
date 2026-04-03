from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.db.mongodb import db_client
from app.models.water import WaterConsumption
from app.services.activity_service import get_or_create_activity

async def log_water(user_id: str, amount_ml: float, intake_time: Optional[datetime] = None) -> WaterConsumption:
    """Log water intake and update activity summary."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    if intake_time is None:
        intake_time = datetime.now()
    
    activity = await get_or_create_activity(obj_id, intake_time.date())

    new_log = {
        "userId": obj_id,
        "userActivityId": ObjectId(activity.id),
        "amountMl": amount_ml,
        "dateAndTime": intake_time,
        "isDeleted": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    result = await db_client.db.water_consumptions.insert_one(new_log)
    
    # Update total in activity
    await db_client.db.activities.update_one(
        {"_id": ObjectId(activity.id)},
        {
            "$inc": {"totalWaterMl": amount_ml},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    created_log = await db_client.db.water_consumptions.find_one({"_id": result.inserted_id})
    return WaterConsumption(**created_log)

async def get_water_logs(user_id: str, start_date: datetime, end_date: datetime) -> List[WaterConsumption]:
    """Retrieve water logs between dates."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    cursor = db_client.db.water_consumptions.find({
        "userId": obj_id,
        "dateAndTime": {"$gte": start_date, "$lte": end_date},
        "isDeleted": False
    }).sort("dateAndTime", -1)
    
    logs = await cursor.to_list(length=100)
    for log in logs:
        log["id"] = str(log["_id"])
    return [WaterConsumption(**l) for l in logs]
async def update_water_log(user_id: str, log_id: str, amount_ml: float, intake_time: Optional[datetime] = None) -> WaterConsumption:
    """Update an existing water log and adjust daily summary."""
    try:
        u_id = ObjectId(user_id)
        l_id = ObjectId(log_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Find existing log
    old_log = await db_client.db.water_consumptions.find_one({"_id": l_id, "userId": u_id, "isDeleted": False})
    if not old_log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    amount_diff = amount_ml - old_log["amountMl"]

    # Update log
    update_data = {
        "amountMl": amount_ml,
        "updatedAt": datetime.now()
    }
    if intake_time:
        update_data["dateAndTime"] = intake_time

    await db_client.db.water_consumptions.update_one({"_id": l_id}, {"$set": update_data})

    # Update activity total
    await db_client.db.activities.update_one(
        {"_id": ObjectId(old_log["userActivityId"])},
        {
            "$inc": {"totalWaterMl": amount_diff},
            "$set": {"updatedAt": datetime.now()}
        }
    )

    updated_log = await db_client.db.water_consumptions.find_one({"_id": l_id})
    return WaterConsumption(**updated_log)

async def delete_water_log(user_id: str, log_id: str) -> bool:
    """Soft delete a water log and adjust daily summary."""
    try:
        u_id = ObjectId(user_id)
        l_id = ObjectId(log_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    log = await db_client.db.water_consumptions.find_one({"_id": l_id, "userId": u_id, "isDeleted": False})
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    # Mark as deleted
    await db_client.db.water_consumptions.update_one(
        {"_id": l_id},
        {"$set": {"isDeleted": True, "updatedAt": datetime.now()}}
    )

    # Subtract from activity
    await db_client.db.activities.update_one(
        {"_id": ObjectId(log["userActivityId"])},
        {
            "$inc": {"totalWaterMl": -log["amountMl"]},
            "$set": {"updatedAt": datetime.now()}
        }
    )

    return True
