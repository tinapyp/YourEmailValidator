from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt
from ..config import settings


def create_jwt_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None,
    secret_key: str = settings.SECRET_KEY,
    algorithm: str = settings.ALGORITHM,
) -> str:
    """
    Create a JWT token with given data and expiration
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def validate_jwt_token(
    token: str,
    secret_key: str = settings.SECRET_KEY,
    algorithm: str = settings.ALGORITHM,
) -> Dict:
    """
    Validate a JWT token and return its payload
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])
