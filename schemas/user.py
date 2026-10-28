"""User Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload required to create a new user."""

    name: str = Field(..., min_length=1, max_length=200, description="Full name of the user.")
    email: EmailStr = Field(..., description="Unique e-mail address.")
    password: str = Field(..., min_length=8, description="Plain-text password (hashed before storage).")


class UserUpdate(BaseModel):
    """Fields that can be changed on a user profile."""

    name: str = Field(..., min_length=1, max_length=200, description="Updated full name of the user.")


class UserResponse(BaseModel):
    """User data returned by the API.

    The password hash is intentionally excluded from this schema.
    """

    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
