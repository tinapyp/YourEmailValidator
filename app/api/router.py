from fastapi import APIRouter
from .endpoints import auth, api_keys

api_router = APIRouter()

# Include all API routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(api_keys.router, prefix="/api", tags=["api-keys"])
