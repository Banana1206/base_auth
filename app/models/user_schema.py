from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import Union


class UserBaseSchema(BaseModel):
    name: str
    email: str
    photo: str
    role: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        from_attributes = True


class CreateUserSchema(UserBaseSchema):
    password: str
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
