from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True, index=True)
    channel = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    conversations = relationship("Conversation", back_populates="session")
    report = relationship("Report", back_populates="session", uselist=False)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    speaker = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="conversations")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(String, index=True, unique=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), unique=True)
    intent = Column(String, index=True)
    summary = Column(String)
    recommended_action = Column(String)
    confidence_score = Column(Float)
    requires_human_review = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="report")
