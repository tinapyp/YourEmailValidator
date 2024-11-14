from fastapi import APIRouter, Request, Depends, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..dependencies import get_current_user_optional
from ..models.models import User, APIKey
from ..services.auth import verify_password, create_access_token, get_password_hash
from ..config import settings
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Load FAQ items
with open("faq.json", "r") as f:
    FAQ_ITEMS = json.load(f)


@router.get("/", response_class=HTMLResponse)
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


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "pages/login.html", {"request": request, "current_user": None}
    )


@router.post("/login")
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

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
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


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(
        "pages/register.html", {"request": request, "current_user": None}
    )


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "error": "Username already registered",
                "current_user": None,
            },
            status_code=400,
        )

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "pages/register.html",
            {
                "request": request,
                "error": "Email already registered",
                "current_user": None,
            },
            status_code=400,
        )

    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically log in the user after registration
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
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


@router.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=False,
        httponly=True,
    )
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    if not current_user:
        return RedirectResponse(url="/login")

    api_keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.is_active == True)
        .all()
    )

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "api_keys": api_keys,
            "usage_stats": {
                "total_calls": 0,
                "success_rate": 0,
                "dates": [],
                "calls": [],
            },
        },
    )
