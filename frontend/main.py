import os
import requests
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any

app = FastAPI(title="Reminder Frontend")
templates = Jinja2Templates(directory="frontend/templates")

# Адрес бэкенда берем из переменной окружения.
# Docker Compose подставит сюда http://backend:8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")

# --- Хелперы (вспомогательные функции) ---

def make_backend_request(method: str, endpoint: str, params: Optional[Dict] = None, json: Optional[Dict] = None) -> Any:
    """Универсальная функция для отправки запросов к бэкенду."""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = requests.request(method, url, params=params, json=json, timeout=5)
        response.raise_for_status()  # Вызовет ошибку, если статус не 2xx
        if response.status_code == 204:  # No Content
            return None
        return response.json()
    except requests.RequestException as e:
        # В логах будет видно полное сообщение
        print(f"Backend request failed: {e}")
        # Вернем словарь с ошибкой, чтобы обработать на уровне выше
        return {"error": f"Сервис данных временно недоступен. Попробуйте позже."}

def parse_reminders(reminders_json: Any) -> List[Dict]:
    """Конвертирует строки с датами из JSON в объекты datetime."""
    if not isinstance(reminders_json, list):
        return []  # Возвращаем пустой список, если бэкенд вернул ошибку или не список

    parsed_reminders = []
    for r in reminders_json:
        try:
            # Превращаем строки 'start_time' и 'end_time' в объекты datetime
            r['start_time'] = datetime.fromisoformat(r['start_time'])
            r['end_time'] = datetime.fromisoformat(r['end_time'])
            # 'created_at' и 'updated_at' тоже строки
            if 'created_at' in r:
                r['created_at'] = datetime.fromisoformat(r['created_at'])
            if 'updated_at' in r:
                r['updated_at'] = datetime.fromisoformat(r['updated_at'])
            parsed_reminders.append(r)
        except (ValueError, TypeError, KeyError) as e:
            # Пропускаем напоминание, если дата в неверном формате
            print(f"Could not parse reminder date, skipping. Reminder: {r}, Error: {e}")
            continue
    return parsed_reminders


# --- Основной эндпоинт для отображения главной страницы ---
@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    action: Optional[str] = Query(None)
):
    now = datetime.now()
    context = {"request": request, "now": now}

    # Получаем данные от бэкенда
    active_now_data = make_backend_request("get", "/api/reminders/", params={"active_now": True})
    active_tomorrow_data = make_backend_request("get", "/api/reminders/", params={"active_tomorrow": True})

    # Проверяем на ошибки и парсим даты
    if "error" in active_now_data or "error" in active_tomorrow_data:
        context["error"] = active_now_data.get("error") or active_tomorrow_data.get("error")
    else:
        context["active_now_reminders"] = parse_reminders(active_now_data)
        context["active_tomorrow_reminders"] = parse_reminders(active_tomorrow_data)
        context["tomorrow_date"] = (now + timedelta(days=1)).date()

    # Обработка фильтра и кнопки "Показать все"
    if action == "show_all":
        filtered_data = make_backend_request("get", "/api/reminders/", params={"show_all": True})
        if "error" not in filtered_data:
            context["filtered_reminders"] = parse_reminders(filtered_data)
    elif action == "filter" and filter_start_date and filter_end_date:
        params = {"filter_start_date": filter_start_date.isoformat(), "filter_end_date": filter_end_date.isoformat()}
        filtered_data = make_backend_request("get", "/api/reminders/", params=params)
        if "error" not in filtered_data:
            context["filtered_reminders"] = parse_reminders(filtered_data)
    
    return templates.TemplateResponse("index.html", context)


# --- CREATE ---
@app.post("/reminders/", response_class=RedirectResponse)
async def handle_create_reminder(
    text: str = Form(...),
    start_time_str: str = Form(...),
    end_time_str: str = Form(...)
):
    payload = {"text": text, "start_time": start_time_str, "end_time": end_time_str}
    make_backend_request("post", "/api/reminders/", json=payload)
    return RedirectResponse(url="/", status_code=303)


# --- UPDATE (Шаг 1: Показать страницу редактирования) ---
@app.get("/reminders/{reminder_id}/edit", response_class=HTMLResponse)
async def show_edit_form(reminder_id: int, request: Request):
    reminder_data = make_backend_request("get", f"/api/reminders/{reminder_id}")
    
    if not reminder_data or "error" in reminder_data:
        raise HTTPException(status_code=404, detail="Reminder not found or backend is down")

    # Преобразуем строки времени в формат, понятный для <input type="datetime-local">
    try:
        for key in ['start_time', 'end_time']:
            if key in reminder_data and reminder_data[key]:
                reminder_data[key] = datetime.fromisoformat(reminder_data[key]).strftime('%Y-%m-%dT%H:%M')
    except (ValueError, TypeError):
        raise HTTPException(status_code=500, detail="Could not parse date from backend")

    return templates.TemplateResponse("edit_reminder.html", {"request": request, "reminder": reminder_data})


# --- UPDATE (Шаг 2: Обработать POST-запрос с изменениями) ---
@app.post("/reminders/{reminder_id}/edit", response_class=RedirectResponse)
async def handle_edit_form(
    reminder_id: int,
    text: str = Form(...),
    start_time_str: str = Form(...),
    end_time_str: str = Form(...)
):
    payload = {"text": text, "start_time": start_time_str, "end_time": end_time_str}
    make_backend_request("put", f"/api/reminders/{reminder_id}", json=payload)
    return RedirectResponse(url="/", status_code=303)


# --- DELETE ---
@app.post("/reminders/{reminder_id}/delete", response_class=RedirectResponse)
async def handle_delete_reminder(reminder_id: int):
    make_backend_request("delete", f"/api/reminders/{reminder_id}")
    return RedirectResponse(url="/", status_code=303)
