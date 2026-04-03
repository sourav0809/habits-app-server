from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.db.mongodb import db_client
from app.models.food import UserFood, FoodConsumption
from app.services.activity_service import get_or_create_activity

async def create_user_food(user_id: str, name: str, calories_per_gram: float, default_quantity: float = 100.0) -> UserFood:
    """Create a predefined food item in the user's catalog."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    new_food = {
        "userId": obj_id,
        "name": name,
        "caloriesPerGram": calories_per_gram,
        "defaultQuantity": default_quantity,
        "isDeleted": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    result = await db_client.db.user_foods.insert_one(new_food)
    created_food = await db_client.db.user_foods.find_one({"_id": result.inserted_id})
    return UserFood(**created_food)

async def get_user_foods(user_id: str) -> List[UserFood]:
    """Retrieve all predefined food items for a user."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    cursor = db_client.db.user_foods.find({"userId": obj_id, "isDeleted": False})
    foods = await cursor.to_list(length=100)
    return [UserFood(**f) for f in foods]

async def log_food_consumption(user_id: str, food_id: str, quantity: float, log_time: Optional[datetime] = None) -> FoodConsumption:
    """Log food consumption and update daily summary."""
    try:
        obj_id = ObjectId(user_id)
        f_id = ObjectId(food_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if log_time is None:
        log_time = datetime.now()

    # Get food details to calculate total calories
    food_item = await db_client.db.user_foods.find_one({"_id": f_id, "isDeleted": False})
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
        
    total_calories = quantity * food_item["caloriesPerGram"]
    
    activity = await get_or_create_activity(obj_id, log_time.date())

    new_log = {
        "userId": obj_id,
        "userActivityId": ObjectId(activity.id),
        "userFoodId": f_id,
        "dateAndTime": log_time,
        "quantity": quantity,
        "totalCalories": total_calories,
        "isDeleted": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    result = await db_client.db.food_consumptions.insert_one(new_log)
    
    # Update total in activity
    await db_client.db.activities.update_one(
        {"_id": ObjectId(activity.id)},
        {
            "$inc": {"totalCalories": total_calories},
            "$set": {"updatedAt": datetime.now()}
        }
    )
    
    created_log = await db_client.db.food_consumptions.find_one({"_id": result.inserted_id})
    return FoodConsumption(**created_log)

async def get_food_consumptions(user_id: str, start_date: datetime, end_date: datetime) -> List[dict]:
    """Retrieve food logs between dates with food details."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    pipeline = [
        {
            "$match": {
                "userId": obj_id,
                "dateAndTime": {"$gte": start_date, "$lte": end_date},
                "isDeleted": False
            }
        },
        {
            "$lookup": {
                "from": "user_foods",
                "localField": "userFoodId",
                "foreignField": "_id",
                "as": "foodInfo"
            }
        },
        {
            "$unwind": "$foodInfo"
        },
        {"$sort": {"dateAndTime": -1}}
    ]
    
    cursor = db_client.db.food_consumptions.aggregate(pipeline)
    logs = await cursor.to_list(length=100)
    
    # Map MongoDB _id to id for consistency
    for log in logs:
        log["id"] = str(log["_id"])
        if "foodInfo" in log:
            log["foodInfo"]["id"] = str(log["foodInfo"]["_id"])
            
    return logs
