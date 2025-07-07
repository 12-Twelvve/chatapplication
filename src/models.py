from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum

# This is an enumeration for user roles.
# It defines two roles: USER and ADMIN.
class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

# This is the User model that represents a user in the system.
# It includes fields for id, username, email, password, and role.
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    # email: str = Field(index=True, unique=True, max_length=100)
    password: str
    role: Role = Field(default=Role.USER)
    
class UserRead(SQLModel):
    id: int
    username: str
    role: Role