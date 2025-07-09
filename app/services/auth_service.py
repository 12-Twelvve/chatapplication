"""
Authentication service for login and token validation.
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user_service import UserService
from app.utils.security import verify_password, create_access_token
from app.config import settings

class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
        
        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create access token for authenticated user.
        
        Args:
            user: Authenticated user
        
        Returns:
            JWT access token
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        return access_token