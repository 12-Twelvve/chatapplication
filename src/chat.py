from fastapi import WebSocket, WebSocketDisconnect, Depends
from jose import JWTError, jwt
from typing import List, Dict
from models import User, Role
from dependencies import get_current_user
from database import get_session
from sqlmodel import Session, select

SECRET_KEY ="thisisscretkeyforjwt"
ALGORITHM = "HS256"

connections = {}

