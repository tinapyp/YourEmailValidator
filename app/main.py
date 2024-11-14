from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .core.middleware import authenticate_user_middleware, log_api_requests
from .database import Base, engine
from .web.routes import router as web_router
from .api.routes import router as api_router
from .auth.routes import router as auth_router

# Import all models to ensure they're registered with SQLAlchemy
from .auth.models import User, UserStatus
from .api.models import APIKey, APIUsage

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(authenticate_user_middleware)
app.middleware("http")(log_api_requests)

# Include routers
app.include_router(web_router)
app.include_router(api_router)
app.include_router(auth_router)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # This will ensure all models are properly configured
    Base.metadata.create_all(bind=engine)
