from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Enum
from app.utils.enums import UserRole 


class User(SQLModel, table=True): # Inherit from SQLModel and set table=True
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.USER, sa_column=Enum(UserRole))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc)) 

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
