from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from app.models.user import User
from app.models.room import Room

class Message(SQLModel, table=True):
    """Message model for storing chat messages."""
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: str = Field(index=True, nullable=False)
    user_id: int = Field(index=True, nullable=False, foreign_key="users.id")
    content: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    room: Room = Relationship(back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id},room_id={self.room_id}, user_id={self.user_id}, content='{self.content[:20]}...')>"