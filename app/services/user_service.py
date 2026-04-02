from fastapi import HTTPException
from bson import ObjectId
from app.db.mongodb import get_database
from app.models.user import UserResponse

async def get_user_by_id(user_id: str) -> UserResponse:
    db = get_database()
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    user_doc = await db.users.find_one({"_id": obj_id, "isDeleted": False})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(**user_doc)
