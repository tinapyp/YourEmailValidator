from fastapi import Request
from ..database import get_db
from ..dependencies import get_current_user_optional


async def authenticate_user_middleware(request: Request, call_next):
    """
    Middleware to authenticate user and add to request state
    """
    try:
        db = next(get_db())
        request.state.user = await get_current_user_optional(request, db)
    except Exception:
        request.state.user = None

    response = await call_next(request)
    return response
