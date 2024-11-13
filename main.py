from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from sqlalchemy.orm import relationship
import json

from database import engine, get_db
from models import APIUsage, Base, User, APIKey
from auth import (
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
    verify_api_key,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from fastapi import Form

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


# User dependency
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


# Middleware to add user to request state
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    try:
        db = next(get_db())
        request.state.user = await get_current_user_optional(request, db)
    except Exception:
        request.state.user = None
    response = await call_next(request)
    return response


with open("faq.json", "r") as f:
    FAQ_ITEMS = json.load(f)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "hero_title": "Validate emails with confidence ✨",
            "hero_description": "Simple, reliable email validation API for developers.",
            "faq_items": FAQ_ITEMS,
            "current_year": datetime.now().year,
            "current_user": current_user,
        },
    )


@app.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "pages/login.html", {"request": request, "current_user": None}
    )


@app.post("/token")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "error": "Invalid username or password",
                "current_user": None,
            },
            status_code=400,
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
        path="/",
        samesite="lax",
    )

    return response


@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=False,
        httponly=True,
    )

    return response


@app.post("/login", name="login_post")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@app.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "pages/register.html", {"request": request, "current_user": None}
    )


@app.post("/register", name="register_post")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already registered")

        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Registration successful"},
        )

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Log the error here in production
        raise HTTPException(
            status_code=500, detail="An error occurred during registration"
        )


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime
    usage_count: int


def get_usage_stats(user_id: int, db: Session, days: int = 30):
    """Get API usage statistics for the last n days."""
    today = datetime.now().date()
    start_date = today - timedelta(days=days)

    # Get daily usage counts
    daily_usage = (
        db.query(
            func.date(APIUsage.timestamp).label("date"),
            func.count(APIUsage.id).label("count"),
        )
        .filter(APIUsage.user_id == user_id, APIUsage.timestamp >= start_date)
        .group_by(func.date(APIUsage.timestamp))
        .all()
    )

    # Create a dict with all dates
    usage_dict = {(start_date + timedelta(days=i)): 0 for i in range(days + 1)}

    # Fill in actual usage
    for date, count in daily_usage:
        usage_dict[date] = count

    # Calculate success rate
    total_calls = db.query(APIUsage).filter(APIUsage.user_id == user_id).count()

    successful_calls = (
        db.query(APIUsage)
        .filter(APIUsage.user_id == user_id, APIUsage.is_success == True)
        .count()
    )

    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

    return {
        "dates": list(usage_dict.keys()),
        "calls": list(usage_dict.values()),
        "total_calls": total_calls,
        "success_rate": success_rate,
    }


@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    # Get user's API keys
    api_keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.is_active == True)
        .all()
    )

    # Mock usage stats for now
    usage_stats = {"total_calls": 0, "success_rate": 0, "dates": [], "calls": []}

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "api_keys": api_keys,
            "usage_stats": usage_stats,
        },
    )


@app.post("/api/keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    new_key = APIKey(
        key=APIKey.generate_key(), name=key_data.name, user_id=current_user.id
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return APIKeyResponse(
        id=new_key.id,
        name=new_key.name,
        key=new_key.key,
        created_at=new_key.created_at,
        usage_count=new_key.usage_count,
    )


@app.delete("/api/keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    db.commit()

    return {"message": "API key deleted successfully"}


@app.middleware("http")
async def authenticate_user_middleware(request: Request, call_next):
    try:
        db = next(get_db())
        request.state.user = await get_current_user_optional(request, db)
    except Exception:
        request.state.user = None

    response = await call_next(request)
    return response


@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        start_time = datetime.now()
        api_key = request.headers.get("X-API-Key")

        response = await call_next(request)

        if api_key:
            db = next(get_db())
            key_record = (
                db.query(APIKey)
                .filter(APIKey.key == api_key, APIKey.is_active == True)
                .first()
            )

            if key_record:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000

                usage_log = APIUsage(
                    user_id=key_record.user_id,
                    api_key_id=key_record.id,
                    endpoint=request.url.path,
                    is_success=response.status_code < 400,
                    response_time=response_time,
                )

                key_record.usage_count += 1
                db.add(usage_log)
                db.commit()

        return response
    return await call_next(request)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
