from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from .models.models import User
from .services.auth import get_current_user


async def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    try:
        token = request.cookies.get("access_token")
        if token:
            user = await get_current_user(token, db)
            return user
    except:
        pass
    return None
