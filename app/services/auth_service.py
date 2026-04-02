from datetime import datetime
from fastapi import HTTPException
from app.db.mongodb import db_client
from app.models.user import UserCreate, UserLogin, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token

async def register_user(user_data: UserCreate) -> dict:
    
    # Check if email exists
    existing_user = await db_client.db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user_data.password)
    
    user_doc = {
        "name": user_data.name.strip(),
        "email": user_data.email.lower(),
        "password": hashed_password,
        "status": "ACTIVE",
        "isDeleted": False,
        "deletedAt": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db_client.db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Create default user goal
    goal_doc = {
        "userId": result.inserted_id,
        "targetWaterMl": 2000.0,
        "targetCalories": 2500.0,
        "isDeleted": False,
        "deletedAt": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    await db_client.db.user_goals.insert_one(goal_doc)
    
    # Generate token
    access_token = create_access_token(subject=str(result.inserted_id))
    
    user_response = UserResponse(**user_doc)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

async def authenticate_user(login_data: UserLogin) -> dict:
    
    user_doc = await db_client.db.users.find_one({"email": login_data.email.lower(), "isDeleted": False})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not verify_password(login_data.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if user_doc["status"] != "ACTIVE":
        raise HTTPException(status_code=403, detail="Inactive user")

    access_token = create_access_token(subject=str(user_doc["_id"]))
    user_response = UserResponse(**user_doc)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }
