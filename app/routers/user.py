"""
User routes for user management.
"""
from fastapi import APIRouter, Depends
from app.models.user import User 
from app.dependencies import get_current_user, require_role
from app.utils.enums import UserRole

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=User, response_model_exclude={'hashed_password'})
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.Accessible by authenticated users of any role.
    Args:
        current_user: Current authenticated user (SQLModel User instance)
    Returns:
        User profile information (hashed_password excluded from response)
    """

    return current_user

@router.get("/dashboard")
def user_dashboard(current_user: User = Depends(require_role(UserRole.USER))):
    """
    User dashboard endpoint. Accessible by users.
    Args:
        current_user: Current authenticated user (SQLModel User instance)
    Returns:
        Dashboard information
    """
    
    return {
        "message": "Welcome to user dashboard",
        "user": current_user.username,
        "role": current_user.role
    }

