import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone

# --- НАСТРОЙКА ---
from backend.main import app
from backend.database import Base, get_db
# Явный импорт модели, чтобы она точно зарегистрировалась в Base
from backend.models import Reminder

# Используем файловую БД, как в твоем рабочем варианте.
# Это исключает проблемы с in-memory базами.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Мы объединяем всё в одну фикстуру, которая и создает таблицы, и подменяет зависимость
@pytest.fixture()
def test_db():
    # Создаем все таблицы перед тестом
    Base.metadata.create_all(bind=engine)
    # yield - это момент, когда выполняется сам тест
    yield
    # Удаляем все таблицы после теста
    Base.metadata.drop_all(bind=engine)

# Переопределяем зависимость get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Создаем тестовый клиент
client = TestClient(app)

# --- ТЕСТЫ ДЛЯ BACKEND API ---
# Мы передаем фикстуру test_db в качестве аргумента в каждый тест
# Это гарантирует, что код фикстуры будет выполнен для каждого теста.

def test_create_reminder_api(test_db): # <--- Передаем фикстуру
    """Тест: Успешное создание напоминания через API."""
    start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    response = client.post(
        "/api/reminders/",
        json={"text": "Test API Reminder", "start_time": start_time.isoformat(), "end_time": end_time.isoformat()},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test API Reminder"
    assert "id" in data

def test_create_reminder_with_invalid_time(test_db): # <--- Передаем фикстуру
    """Тест: Ошибка при попытке создать напоминание, где время начала позже времени окончания."""
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)
    end_time = start_time - timedelta(hours=1) # Неверное время
    
    response = client.post(
        "/api/reminders/",
        json={"text": "Invalid Time", "start_time": start_time.isoformat(), "end_time": end_time.isoformat()},
    )
    assert response.status_code == 400

def test_read_reminders_api(test_db): # <--- Передаем фикстуру
    """Тест: Получение списка напоминаний."""
    client.post("/api/reminders/", json={"text": "Reminder 1", "start_time": "2025-01-01T10:00:00Z", "end_time": "2025-01-01T11:00:00Z"})
    
    response = client.get("/api/reminders/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["text"] == "Reminder 1"

def test_update_reminder_api(test_db): # <--- Передаем фикстуру
    """Тест: Обновление существующего напоминания."""
    response_create = client.post("/api/reminders/", json={"text": "Original Text", "start_time": "2025-01-01T10:00:00Z", "end_time": "2025-01-01T11:00:00Z"})
    reminder_id = response_create.json()["id"]

    response_update = client.put(
        f"/api/reminders/{reminder_id}",
        json={"text": "Updated Text", "start_time": "2025-01-01T10:00:00Z", "end_time": "2025-01-01T12:00:00Z"}
    )
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["text"] == "Updated Text"

def test_delete_reminder_api(test_db): # <--- Передаем фикстуру
    """Тест: Удаление существующего напоминания."""
    response_create = client.post("/api/reminders/", json={"text": "To Be Deleted", "start_time": "2025-01-01T10:00:00Z", "end_time": "2025-01-01T11:00:00Z"})
    reminder_id = response_create.json()["id"]

    response_delete = client.delete(f"/api/reminders/{reminder_id}")
    assert response_delete.status_code == 204

    response_get = client.get(f"/api/reminders/{reminder_id}")
    assert response_get.status_code == 404
