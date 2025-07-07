from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)