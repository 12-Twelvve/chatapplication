"""
Authentication routes for signup and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlmodel import Session 
from app.database import get_session 
from app.models.user import User 
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.utils.enums import UserRole 

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED, response_model_exclude={'hashed_password'})
def signup(
    email: str,
    username: str,
    password: str,
    role: UserRole = UserRole.USER,
    db: Session = Depends(get_session)
):
    """
    User registration endpoint.

    Creates a new user with hashed password and assigned role.

    Args:
        email: User's email address
        username: User's desired username
        password: User's chosen password
        role: User's role (defaults to 'user')
        db: Database session

    Returns:
        Created user information (hashed_password excluded from response)

    Raises:
        HTTPException: If user already exists
    """
    # Call UserService.create_user with individual arguments
    return UserService.create_user(db, email=email, username=username, password=password, role=role)

@router.post("/login") # Removed response_model=Token
def login(
    username: str = Form(...), # Accept username directly from form data
    password: str = Form(...), # Accept password directly from form data
    db: Session = Depends(get_session) # Use get_session
):
    """
    User login endpoint.

    Verifies credentials and returns JWT token with embedded role.

    Args:
        username: User's username
        password: User's password
        db: Database session

    Returns:
        JWT access token and token type in a dictionary.

    Raises:
        HTTPException: If credentials are invalid
    """
    user = AuthService.authenticate_user(
        db,
        username, # Use the directly provided username
        password  # Use the directly provided password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token_for_user(user)
    # Return a dictionary instead of a Token model
    return {"access_token": access_token, "token_type": "bearer"}
