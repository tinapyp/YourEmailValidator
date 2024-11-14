from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api.router import api_router
from .web.routes import router as web_router
from .middleware.authentication import authenticate_user_middleware
from .middleware.api_logger import log_api_requests

# Create the FastAPI app
app = FastAPI(
    title="Email Validation API",
    description="A simple and reliable email validation API for developers",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(authenticate_user_middleware)
app.middleware("http")(log_api_requests)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(web_router)  # Web routes for HTML pages
app.include_router(api_router)  # API routes

# Create database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
