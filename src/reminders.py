from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from models import User, Reminder
from schemas import ReminderCreate, ReminderResponse, ReminderUpdate
from database import get_db
from utils import verify_token
from fastapi import Header

router = APIRouter(prefix="/api/reminders", tags=["reminders"])

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/", response_model=List[ReminderResponse])
async def list_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminders = db.query(Reminder).filter(Reminder.user_id == current_user.id).all()
    return reminders

@router.get("/due", response_model=List[ReminderResponse])
async def get_due_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    # Find active reminders where remind_at or snoozed_until is strictly before or at now + 1 min
    # This gives a small buffer for the frontend polling
    buffer_time = now + timedelta(minutes=1)
    
    due_reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
    ).all()
    
    # Filter in python for complex time checks to avoid DB differences or timezone issues easily
    results = []
    for r in due_reminders:
        target_time = r.snoozed_until if r.snoozed_until else r.remind_at
        if target_time <= buffer_time:
            results.append(r)
            
    return results

@router.post("/", response_model=ReminderResponse)
async def create_reminder(reminder_data: ReminderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_reminder = Reminder(
        user_id=current_user.id,
        task_id=reminder_data.task_id,
        title=reminder_data.title,
        remind_at=reminder_data.remind_at,
        repeat=reminder_data.repeat
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    return new_reminder

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: int, reminder_data: ReminderUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    if reminder_data.title is not None:
        reminder.title = reminder_data.title
    if reminder_data.remind_at is not None:
        reminder.remind_at = reminder_data.remind_at
    if reminder_data.repeat is not None:
        reminder.repeat = reminder_data.repeat
    if reminder_data.is_active is not None:
        reminder.is_active = reminder_data.is_active
    if reminder_data.snoozed_until is not None:
        reminder.snoozed_until = reminder_data.snoozed_until
        
    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"detail": "Reminder deleted"}
