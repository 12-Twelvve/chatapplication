"""
User service for user management operations.
"""
from typing import Optional, List
from sqlmodel import Session, select, update # Import update for direct updates
from fastapi import HTTPException, status
from app.models.user import User # This is your SQLModel User class
from app.utils.security import get_password_hash
from app.utils.enums import UserRole # Ensure UserRole is imported

class UserService:
    """
    Service class for user operations.
    """

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        """
        return db.exec(select(User).where(User.id == user_id)).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.
        """
        return db.exec(select(User).where(User.username == username)).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        """
        return db.exec(select(User).where(User.email == email)).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        """
        return db.exec(select(User).offset(skip).limit(limit)).all()

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str, # Password now passed directly
        role: UserRole = UserRole.USER # Default role
    ) -> User:
        """
        Create a new user

        Args:
            db: Database session
            email: User's email
            username: User's username
            password: User's plain-text password (will be hashed)
            role: User's role (defaults to UserRole.USER)

        Returns:
            Created user

        Raises:
            HTTPException: If user already exists
        """
        # Check if user already exists
        if UserService.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        if UserService.get_user_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user instance
        hashed_password = get_password_hash(password) # Use the directly passed password
        db_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: User) -> Optional[User]:
        """
        Update user information 

        Args:
            db: Database session
            user_id: ID of the user to update
            user_data: User object containing fields to update.
                       Only fields that are set (not None and not default) will be updated.

        Returns:
            Updated user, or None if user not found.
        """
        # Fetch the existing user
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        # Update the fields in the SQLModel instance
        for key, value in update_data.items():
            setattr(db_user, key, value) # This will update the SQLModel instance

        db.add(db_user) # Add the modified object back to the session
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete a user
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
