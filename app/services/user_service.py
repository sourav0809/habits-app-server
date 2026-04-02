from fastapi import HTTPException
from bson import ObjectId
from app.db.mongodb import db_client
from app.models.user import UserResponse

async def get_user_by_id(user_id: str) -> UserResponse:
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid User ID format")

    user_doc = await db_client.db.users.find_one({"_id": obj_id, "isDeleted": False})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(**user_doc)
