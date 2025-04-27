"""
Token schemas for authentication.
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Schema for the authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for data stored in the token."""
    email: Optional[str] = None 