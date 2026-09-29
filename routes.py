from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import ADMIN_PASSWORD
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip
from .gemini_generator import generate_workout_plan
from .models import User, WorkoutPlan
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_user(db, user_id):
    return db.scalar(select(User).where(User.user_id == user_id))

def latest_plan(db, user):
    return db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == user.id).order_by(WorkoutPlan.id.desc()))

def save_user(db, data):
    user = get_user(db, data.user_id)
    if user is None:
        user = User(**data.model_dump())
        db.add(user)
        db.flush()
    else:
        for key, value in data.model_dump().items():
            setattr(user, key, value)
    return user

def save_plan(db, user, plan, nutrition):
    record = WorkoutPlan(user_id=user.id, original_plan=plan, nutrition_tip=nutrition)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(request: Request, username: str = Form(...), user_id: str = Form(...),
                     age: int = Form(...), weight: float = Form(...), goal: str = Form(...),
                     intensity: str = Form(...), db: Session = Depends(get_db)):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
        plan_obj, plan_text = generate_workout_plan(data)
        nutrition = generate_nutrition_tip(data.goal, data.intensity)
        user = save_user(db, data)
        record = save_plan(db, user, plan_text, nutrition)
        return templates.TemplateResponse("result.html", {"request": request, "user": user, "plan": record, "error": None})
    except Exception as exc:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(exc)})

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...), db: Session = Depends(get_db)):
    try:
        req = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(db, req.user_id)
        if not user:
            raise ValueError("User not found.")
        record = latest_plan(db, user)
        if not record:
            raise ValueError("No workout plan found.")
        data = UserInput(username=user.username, user_id=user.user_id, age=user.age, weight=user.weight, goal=user.goal, intensity=user.intensity)
        record.updated_plan = update_workout_plan(data, record.original_plan, req.feedback)
        record.feedback = req.feedback
        record.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(record)
        return templates.TemplateResponse("result.html", {"request": request, "user": user, "plan": record, "error": None})
    except Exception as exc:
        return templates.TemplateResponse("index.html", {"request": request, "error": str(exc)})

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, password: str = ""):
    if password != ADMIN_PASSWORD:
        return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})
    from .database import SessionLocal
    db = SessionLocal()
    try:
        users = db.scalars(select(User).order_by(User.created_at.desc())).all()
        rows = [{"user": u, "plan": latest_plan(db, u)} for u in users]
        return templates.TemplateResponse("all_users.html", {"request": request, "rows": rows, "password": password})
    finally:
        db.close()

@router.post("/admin/delete-user")
def delete_user(user_id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if password != ADMIN_PASSWORD:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url=f"/view-all-users?password={password}", status_code=303)

@router.post("/api/generate-workout")
def api_generate(data: UserInput, db: Session = Depends(get_db)):
    plan_obj, plan_text = generate_workout_plan(data)
    nutrition = generate_nutrition_tip(data.goal, data.intensity)
    user = save_user(db, data)
    record = save_plan(db, user, plan_text, nutrition)
    return {"user": data.model_dump(), "plan": plan_obj.model_dump(), "nutrition_tip": nutrition, "record_id": record.id}

@router.post("/api/submit-feedback")
def api_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    user = get_user(db, data.user_id)
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    record = latest_plan(db, user)
    if not record:
        return JSONResponse({"error": "No workout plan found"}, status_code=404)
    user_data = UserInput(username=user.username, user_id=user.user_id, age=user.age, weight=user.weight, goal=user.goal, intensity=user.intensity)
    record.updated_plan = update_workout_plan(user_data, record.original_plan, data.feedback)
    record.feedback = data.feedback
    record.updated_at = datetime.utcnow()
    db.commit()
    return {"updated_plan": record.updated_plan}

@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [{"user_id": u.user_id, "username": u.username, "age": u.age, "weight": u.weight, "goal": u.goal, "intensity": u.intensity, "latest_plan_id": latest_plan(db, u).id if latest_plan(db, u) else None} for u in users]
