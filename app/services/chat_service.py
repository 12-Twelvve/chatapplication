from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Session, select
from app.models.message import Message

class ChatService:
    """
    Service class for chat operations.
    """

    @staticmethod
    def get_messages_by_room_id(db: Session, room_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Get messages by room ID with pagination.
        """
        return db.exec(
            select(Message).where(Message.room_id == room_id).offset(skip).limit(limit)
        ).all()

    @staticmethod
    def create_message(
        db: Session,
        room_id: str,
        user_id: int,
        content: str
    ) -> Message:
        """
        Create a new message in a chat room.

        Args:
            db: Database session
            room_id: ID of the chat room
            user_id: ID of the user sending the message
            content: Content of the message

        Returns:
            The created Message object.
        """
        message = Message(
            room_id=room_id,
            user_id=user_id,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_recent_messages(
        db: Session,
        room_id: str,
        cursor_timestamp: Optional[datetime] = None, # For cursor-based pagination
        limit: int = 20
    ) -> List[Message]:
        """
        Fetches recent messages from a specific room, using cursor-based pagination.
        Messages are ordered by timestamp descending.
        """
        query = select(Message).where(Message.room_id == room_id)

        if cursor_timestamp:
            # For "older" messages (pagination backwards in time)
            query = query.where(Message.timestamp < cursor_timestamp)
        
        query = query.order_by(Message.timestamp.desc()).limit(limit)
        
        return db.exec(query).all()

    @staticmethod
    def get_message_by_id(db: Session, message_id: int) -> Optional[Message]:
        """Fetches a message by its ID."""
        return db.exec(select(Message).where(Message.id == message_id)).first()
        
        