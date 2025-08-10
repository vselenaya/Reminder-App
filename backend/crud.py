from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from . import models

def get_reminder(db: Session, reminder_id: int):
    return db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()

def get_reminders(db: Session, skip: int = 0, limit: int = 100):
    # Сортируем по времени окончания! (хотим дедлайн как можно раньше увидеть)
    return db.query(models.Reminder).order_by(models.Reminder.end_time).offset(skip).limit(limit).all()

def create_reminder(db: Session, reminder: models.ReminderCreate):
    db_reminder = models.Reminder(
        text=reminder.text,
        start_time=reminder.start_time,
        end_time=reminder.end_time
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def update_reminder(db: Session, reminder_id: int, reminder_update: models.ReminderUpdate):
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder:
        db_reminder.text = reminder_update.text
        db_reminder.start_time = reminder_update.start_time
        db_reminder.end_time = reminder_update.end_time
        db.commit()
        db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: int):
    db_reminder = get_reminder(db, reminder_id)
    if db_reminder:
        db.delete(db_reminder)
        db.commit()
    return db_reminder

def get_active_reminders(db: Session, now: datetime):
    return db.query(models.Reminder).filter(
        models.Reminder.start_time <= now,
        models.Reminder.end_time >= now
    ).order_by(models.Reminder.end_time).all()

def get_reminders_for_date_range(db: Session, start_date: datetime, end_date: datetime):
    return db.query(models.Reminder).filter(
        models.Reminder.start_time < end_date,
        models.Reminder.end_time > start_date
    ).order_by(models.Reminder.end_time).all()

