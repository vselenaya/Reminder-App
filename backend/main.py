from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date

# Важно, чтобы импорты были с точкой, так как это пакет
from . import crud, models
# Импортируем нашу новую функцию
from .database import get_db, init_db

# --- ВЫЗЫВАЕМ ФУНКЦИЮ ПРИ СТАРТЕ ---
# Сервер сначала создаст таблицы, а потом будет готов к работе.
init_db()

app = FastAPI(title="Reminder Backend API")

# --- CRUD API ---
@app.post("/api/reminders/", response_model=models.ReminderInDB, status_code=status.HTTP_201_CREATED)
def api_create_reminder(reminder: models.ReminderCreate, db: Session = Depends(get_db)):
    if reminder.start_time >= reminder.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time.")
    return crud.create_reminder(db=db, reminder=reminder)

@app.get("/api/reminders/{reminder_id}", response_model=models.ReminderInDB)
def api_read_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = crud.get_reminder(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@app.put("/api/reminders/{reminder_id}", response_model=models.ReminderInDB)
def api_update_reminder(reminder_id: int, reminder: models.ReminderUpdate, db: Session = Depends(get_db)):
    if reminder.start_time >= reminder.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time.")
    updated_reminder = crud.update_reminder(db=db, reminder_id=reminder_id, reminder_update=reminder)
    if updated_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated_reminder

@app.delete("/api/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = crud.delete_reminder(db=db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return

# --- API для получения списков ---
@app.get("/api/reminders/", response_model=List[models.ReminderInDB])
def api_get_reminders(
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    show_all: bool = False,
    active_now: bool = False,
    active_tomorrow: bool = False,
    db: Session = Depends(get_db)
):
    now = datetime.now()
    if active_now:
        return crud.get_active_reminders(db, now=now)
    
    if active_tomorrow:
        tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        return crud.get_reminders_for_date_range(db, start_date=tomorrow_start, end_date=tomorrow_end)
        
    if filter_start_date and filter_end_date:
        range_start = datetime.combine(filter_start_date, datetime.min.time())
        range_end = datetime.combine(filter_end_date + timedelta(days=1), datetime.min.time())
        return crud.get_reminders_for_date_range(db, start_date=range_start, end_date=range_end)

    if show_all:
        return crud.get_reminders(db, limit=1000)

    return crud.get_reminders(db, limit=100) # По умолчанию вернем 100 последних
