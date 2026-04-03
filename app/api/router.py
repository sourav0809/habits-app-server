from fastapi import APIRouter
from app.api.endpoints import auth, food, water, goal

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(food.router, prefix="/foods", tags=["food"])
api_router.include_router(water.router, prefix="/water", tags=["water"])
api_router.include_router(goal.router, prefix="/goals", tags=["goal"])
