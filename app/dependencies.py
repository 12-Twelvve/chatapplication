from fastapi import HTTPException, Depends, WebSocket, WebSocketException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models.user import User
from app.utils.enums import UserRole
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user from the JWT token.
    
    Args:
        token: JWT token from the request header
    
    Returns:
        User object if token is valid    
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return User(username=username, role=UserRole(payload.get("role")))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def require_role(required_role: UserRole):
    """
    Create a dependency that requires specific roles.
    
    Args:
        allowed_roles: List of allowed user roles
    
    Returns:
        Dependency function that checks user role
    """
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return role_checker



# NEW: WebSocket JWT Authentication Dependency
async def get_websocket_user(
    websocket: WebSocket,
    token: str = Query(...) # Token expected as a query parameter ?token=abc
) -> User:
    """
    Authenticates a WebSocket connection using a JWT token from query parameters.
    This function mirrors the logic of get_current_user for WebSocket context.
    """
    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate WebSocket credentials."
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role_str: str = payload.get("role")

        if username is None or user_role_str is None:
            raise credentials_exception
        
        # Construct User object from payload, similar to get_current_user
        return User(username=username, role=UserRole(user_role_str), email="placeholder@example.com", hashed_password="not_needed_for_auth_check")
    except JWTError:
        raise credentials_exception
    except ValueError: # Catch if UserRole string is invalid
        raise credentials_exception
    except Exception as e:
        # Catch any other unexpected errors during token processing
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=f"Authentication error: {e}")

