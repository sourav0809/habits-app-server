from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserResponse
from app.services import auth_service
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(login_data: UserLogin):
    return await auth_service.authenticate_user(login_data)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
