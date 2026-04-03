from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from app.db.mongodb import db_client
from app.models.food import UserFood, FoodConsumption
from app.services.activity_service import get_or_create_activity
from app.validation.food import CreateFoodRequest, LogFoodRequest, UpdateFoodLogRequest

async def create_user_food(user_id: str, request: CreateFoodRequest) -> UserFood:
    """Create a predefined food item in the user's catalog."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    new_food = {
        "userId": obj_id,
        "name": request.name,
        "caloriesPerGram": request.calories_per_gram,
        "defaultQuantity": request.default_quantity,
        "isDeleted": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    
    result = await db_client.db.user_foods.insert_one(new_food)
    new_food["_id"] = result.inserted_id
    return UserFood(**new_food)

async def get_user_foods(user_id: str) -> List[UserFood]:
    """Retrieve all predefined food items for a user."""
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    cursor = db_client.db.user_foods.find({"userId": obj_id, "isDeleted": False})
    foods = await cursor.to_list(length=100)
    return [UserFood(**f) for f in foods]

async def log_food_consumption(user_id: str, request: LogFoodRequest) -> FoodConsumption:
    """Log food consumption and update daily summary."""
    try:
        obj_id = ObjectId(user_id)
        f_id = ObjectId(request.food_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    log_time = request.log_time or datetime.now()

    # Get food details to calculate total calories
    food_item = await db_client.db.user_foods.find_one({"_id": f_id, "isDeleted": False})
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")
        
    total_calories = request.quantity * food_item["caloriesPerGram"]
    
    activity = await get_or_create_activity(obj_id, log_time.date())

    new_log = {
        "userId": obj_id,
        "userActivityId": ObjectId(activity.id),
        "userFoodId": f_id,
        "dateAndTime": log_time,
        "quantity": request.quantity,
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
    
    new_log["_id"] = result.inserted_id
    return FoodConsumption(**new_log)

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
    
    for log in logs:
        log["id"] = str(log["_id"])
        if "foodInfo" in log:
            log["foodInfo"]["id"] = str(log["foodInfo"]["_id"])
            
    return logs

async def update_food_log(user_id: str, log_id: str, request: UpdateFoodLogRequest) -> FoodConsumption:
    """Update an existing food log and adjust daily summary."""
    try:
        u_id = ObjectId(user_id)
        l_id = ObjectId(log_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    old_log = await db_client.db.food_consumptions.find_one({"_id": l_id, "userId": u_id, "isDeleted": False})
    if not old_log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    food_item = await db_client.db.user_foods.find_one({"_id": ObjectId(old_log["userFoodId"])})
    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    new_total_calories = request.quantity * food_item["caloriesPerGram"]
    calorie_diff = new_total_calories - old_log["totalCalories"]

    update_data = {
        "quantity": request.quantity,
        "totalCalories": new_total_calories,
        "updatedAt": datetime.now()
    }
    if request.log_time:
        update_data["dateAndTime"] = request.log_time

    await db_client.db.food_consumptions.update_one({"_id": l_id}, {"$set": update_data})

    await db_client.db.activities.update_one(
        {"_id": ObjectId(old_log["userActivityId"])},
        {
            "$inc": {"totalCalories": calorie_diff},
            "$set": {"updatedAt": datetime.now()}
        }
    )

    updated_log = await db_client.db.food_consumptions.find_one({"_id": l_id})
    return FoodConsumption(**updated_log)

async def delete_food_log(user_id: str, log_id: str) -> bool:
    """Soft delete a food log and adjust daily summary."""
    try:
        u_id = ObjectId(user_id)
        l_id = ObjectId(log_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    log = await db_client.db.food_consumptions.find_one({"_id": l_id, "userId": u_id, "isDeleted": False})
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    await db_client.db.food_consumptions.update_one(
        {"_id": l_id},
        {"$set": {"isDeleted": True, "updatedAt": datetime.now()}}
    )

    await db_client.db.activities.update_one(
        {"_id": ObjectId(log["userActivityId"])},
        {
            "$inc": {"totalCalories": -log["totalCalories"]},
            "$set": {"updatedAt": datetime.now()}
        }
    )

    return True
