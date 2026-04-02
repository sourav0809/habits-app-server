from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from app.models.common import MongoBaseModel, TimestampModel, DeletableModel

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class UserBase(DeletableModel, TimestampModel):
    name: str = Field(..., min_length=1, description="User's name (trimmed)")
    email: EmailStr = Field(..., description="User's unique email")
    status: UserStatus = Field(default=UserStatus.ACTIVE)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase, MongoBaseModel):
    password: str

class UserResponse(UserBase, MongoBaseModel):
    pass
