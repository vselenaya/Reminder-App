from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.sql import func as sqlfunc # Renamed to avoid Pydantic conflict
from pydantic import BaseModel
from datetime import datetime

from .database import Base

# SQLAlchemy model
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=sqlfunc.now()) # Use renamed func
    updated_at = Column(DateTime, server_default=sqlfunc.now(), onupdate=sqlfunc.now()) # Use renamed func

# Pydantic models for request/response validation
class ReminderBase(BaseModel):
    text: str
    start_time: datetime
    end_time: datetime

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(ReminderBase):
    pass

class ReminderInDB(ReminderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For SQLAlchemy ORM mode (Pydantic V2)
        # orm_mode = True # For Pydantic V1
