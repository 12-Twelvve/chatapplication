import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.dependencies import get_websocket_user
from app.services.chat_service import ChatService
from app.models.message import Message
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["chat"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        print(f"User connected to room {room_id}. Total connections in room: {len(self.active_connections[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id] # Clean up empty rooms
            print(f"User disconnected from room {room_id}. Remaining connections in room: {len(self.active_connections.get(room_id, []))}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


    async def broadcast(self, message: Dict[str, Any], room_id: str):
        """Broadcasts a message (as JSON string) to all clients in a specific room."""
        # Ensure the message is JSON serializable
        message_str = json.dumps(message, default=str) # default=str handles datetime serialization
        
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message_str)
                except RuntimeError as e:
                    print(f"Error sending to WebSocket in room {room_id}: {e}")
                    # Optionally handle disconnection here if error indicates broken pipe
                except Exception as e:
                    print(f"Unexpected error broadcasting: {e}")

manager = ConnectionManager()

# websocket endpoint for chat rooms
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    # Inject authenticated user from WebSocket token
    current_user: User = Depends(get_websocket_user),
    db: Session = Depends(get_session)
):
    """
    WebSocket endpoint for chat communication.
    Requires a JWT token as a query parameter (e.g., /ws/general?token=YOUR_JWT_TOKEN).
    """
    try:
        await manager.connect(websocket, room_id)
        

        recent_messages = ChatService.get_recent_messages(db, room_id=room_id, limit=50) # Fetch 50 recent messages
        
        # Messages oldest first
        for msg in reversed(recent_messages):
            # Send message data. Exclude sensitive using model_dump for easy JSON conversion
            await manager.send_personal_message(
                json.dumps({
                    "id": msg.id,
                    "room_id": msg.room_id,
                    "user_id": msg.user_id,
                    "username": current_user.username, 
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }),
                websocket
            )

        while True:
            try:
                data = await websocket.receive_text()
                
                new_message_db = ChatService.create_message(
                    db,
                    room_id=room_id,
                    user_id=current_user.id,
                    content=data
                )
                
                # message for broadcasting 
                broadcast_message = {
                    "id": new_message_db.id,
                    "room_id": new_message_db.room_id,
                    "user_id": new_message_db.user_id,
                    "username": current_user.username,
                    "content": new_message_db.content,
                    "timestamp": new_message_db.timestamp.isoformat()
                }
                
                # Broadcast to all connected clients in the same room
                await manager.broadcast(broadcast_message, room_id)

            except WebSocketDisconnect:
                print(f"User {current_user.username} disconnected from room {room_id}.")
                break # Exit the loop on disconnect
            except json.JSONDecodeError:
                print(f"Received invalid JSON from {current_user.username} in room {room_id}: {data}")
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
            except Exception as e:
                print(f"Error in WebSocket communication for user {current_user.username} in room {room_id}: {e}")
                await websocket.send_text(json.dumps({"error": f"Server error: {e}"}))
                break # Close connection on unexpected errors

    finally:
        # Disconnection logic even if loop breaks due to other reasons
        manager.disconnect(websocket, room_id)

# testing routes
@router.get("/test")
async def test_chat_router():
    return {"message": "Chat router is working!"}