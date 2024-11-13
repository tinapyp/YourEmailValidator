from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import timedelta
from fastapi.responses import JSONResponse

from database import engine, get_db
from models import Base, User, APIKey
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


# Routes
@app.get("/", response_class=HTMLResponse, name="home")
async def home(
    request: Request, current_user: Optional[User] = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        "pages/home.html", {"request": request, "current_user": current_user}
    )


@app.get("/login", response_class=HTMLResponse, name="login")
async def login_page(
    request: Request, current_user: Optional[User] = Depends(get_current_user_optional)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
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

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        expires=1800,
    )
    return response


@app.post("/logout", name="logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
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
async def register_page(
    request: Request, current_user: Optional[User] = Depends(get_current_user_optional)
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
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


@app.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "current_user": current_user, "api_keys": api_keys},
    )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
