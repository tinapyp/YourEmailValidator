from random import random
import string
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_random_password(length: int = 12) -> str:
    """
    Generate a random password with a mix of letters, digits, and symbols.
    """
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(random.choice(characters) for _ in range(length))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
