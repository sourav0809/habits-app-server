from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from typing import Annotated

from app.core.config import settings
from app.models.user import UserResponse
from app.services.user_service import get_user_by_id

# We use an empty tokenUrl because we are handling the payload as JSON not Form Data typically,
# but using OAuth2PasswordBearer for swagger UI compatibility is also a common pattern.
# For custom frontend usage, sending 'Authorization: Bearer <token>' works fine.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # get user from db/service
    try:
        user = await get_user_by_id(user_id)
    except HTTPException:
        raise HTTPException(status_code=401, detail="User not found")
        
    return user
