"""
Authentication routes for the API.

This module handles user authentication and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError

from backend.api.auth import create_access_token, get_current_user
from backend.models.user import User
from backend.schemas.token import Token, TokenData
from backend.services.user_service import authenticate_user

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and create access token.
    
    Args:
        form_data: OAuth2 password request form with username and password.
        
    Returns:
        Token: Access token and token type.
        
    Raises:
        HTTPException: If authentication fails.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get authenticated user information.
    
    Args:
        current_user: Currently authenticated user from token validation.
        
    Returns:
        User: Current user information.
    """
    return current_user 