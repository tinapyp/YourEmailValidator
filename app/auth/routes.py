from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.config import settings
from . import models, schemas, utils
from .dependencies import get_current_user, get_current_user_optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "pages/login.html", {"request": request, "current_user": None}
    )


@router.post("/login", name="login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not utils.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "error": "Invalid username or password",
                "current_user": None,
            },
            status_code=400,
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
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
        secure=False,
    )

    return response


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user_optional(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "pages/register.html", {"request": request, "current_user": None}
    )


@router.post("/register", name="register_post")
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username exists
        if (
            db.query(models.User)
            .filter(models.User.username == user_data.username)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email exists
        if db.query(models.User).filter(models.User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = utils.get_password_hash(user_data.password)
        user = models.User(
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
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred during registration"
        )


@router.post("/logout", name="logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=False,
        httponly=True,
    )
    return response
