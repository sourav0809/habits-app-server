from datetime import datetime, date
from bson import ObjectId
from app.db.mongodb import db_client
from app.models.activity import UserActivity

async def get_or_create_activity(user_id: ObjectId, activity_date: date) -> UserActivity:
    # Convert date to start of day datetime (assuming UTC/Server time for simplicity)
    start_of_day = datetime.combine(activity_date, datetime.min.time())
    
    activity = await db_client.db.activities.find_one({
        "userId": user_id, 
        "date": start_of_day, 
        "isDeleted": False
    })
    
    if not activity:
        new_activity = {
            "userId": user_id,
            "date": start_of_day,
            "totalCalories": 0.0,
            "totalWaterMl": 0.0,
            "isDeleted": False,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        result = await db_client.db.activities.insert_one(new_activity)
        activity = await db_client.db.activities.find_one({"_id": result.inserted_id})
        
    return UserActivity(**activity)
