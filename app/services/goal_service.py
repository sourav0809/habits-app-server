from fastapi import HTTPException
from bson import ObjectId
from app.db.mongodb import db_client
from app.models.goal import UserGoal
from app.models.common import PyObjectId
from datetime import datetime

async def get_user_goal(user_id: str) -> UserGoal:
    """Retrieve or create default goals for a user."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    goal_doc = await db_client.db.goals.find_one({"userId": obj_id, "isDeleted": False})
    
    if not goal_doc:
        # Create default goal
        new_goal = {
            "userId": obj_id,
            "targetWaterMl": 2000.0,
            "targetCalories": 2000.0,
            "isDeleted": False,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        result = await db_client.db.goals.insert_one(new_goal)
        goal_doc = await db_client.db.goals.find_one({"_id": result.inserted_id})

    return UserGoal(**goal_doc)

async def update_user_goal(user_id: str, target_water: float = None, target_calories: float = None) -> UserGoal:
    """Update user goals."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    update_data = {"updatedAt": datetime.now()}
    if target_water is not None:
        update_data["targetWaterMl"] = target_water
    if target_calories is not None:
        update_data["targetCalories"] = target_calories

    result = await db_client.db.goals.find_one_and_update(
        {"userId": obj_id, "isDeleted": False},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        # If not found, create one with defaults and the updates
        new_goal = {
            "userId": obj_id,
            "targetWaterMl": target_water if target_water is not None else 2000.0,
            "targetCalories": target_calories if target_calories is not None else 2000.0,
            "isDeleted": False,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        res = await db_client.db.goals.insert_one(new_goal)
        result = await db_client.db.goals.find_one({"_id": res.inserted_id})

    return UserGoal(**result)
