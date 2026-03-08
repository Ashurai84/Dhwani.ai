import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# MongoDB ke liye (baad mein use karenge)
# from motor.motor_asyncio import AsyncIOMotorClient
# MONGODB_URI = os.environ.get("MONGODB_URI", "")

# SQLite (abhi presentation ke liye)
SQLALCHEMY_DATABASE_URL = "sqlite:///./banking.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

