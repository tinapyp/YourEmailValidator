from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserRegister(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime
    usage_count: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
