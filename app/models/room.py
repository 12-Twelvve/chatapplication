from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class Room(SQLModel, table=True):
    """Room model for chat rooms."""
    
    __tablename__ = "rooms"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    messages: List["Message"] = Relationship(back_populates="room")
    
    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', created_at={self.created_at.isoformat()})>"
    
