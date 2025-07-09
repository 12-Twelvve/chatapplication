"""
Database connection and session management.
"""
from sqlmodel import Session, SQLModel, create_engine
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    """
    Database dependency to get DB session.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Create all database tables.
    """
    SQLModel.metadata.create_all(engine)
    
