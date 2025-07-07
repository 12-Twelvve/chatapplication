from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlmodel import Session, select
from jose import jwt
from datetime import datetime, timedelta
from models import User, Role, UserRead
from database import get_session
from dependencies import get_current_user, require_role

SECRET_KEY ="thisisscretkeyforjwt"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(user: User) -> str:
    expiration = datetime.now(datetime.timezone.utc) + timedelta(hours=1)
    to_encode = {"sub": user.username,"role": user.role, "exp": expiration}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup", response_model=UserRead)
def signup(user: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == username)).first()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_token(db_user)
    return {"access_token": token, "token_type": "bearer", "user": db_user}
 
 
@router.get("/admin-only")
def admin_route(user: User = Depends(require_role(Role.ADMIN))):
    return {"message": "Welcome to the admin route!"}
