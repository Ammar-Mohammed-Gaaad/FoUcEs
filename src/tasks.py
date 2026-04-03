from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import User, Task, Goal
from schemas import TaskCreate, TaskResponse, TaskUpdate
from database import get_db
from utils import verify_token
from fastapi import Header

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

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

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        goal_id=task_data.goal_id,
        priority=task_data.priority,
        deadline=task_data.deadline
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.deadline is not None:
        task.deadline = task_data.deadline
    if task_data.status is not None:
        # نظام الجوائز (Gamification)
        if task_data.status == "done" and task.status != "done":
            if current_user.xp is None:
                current_user.xp = 0
            current_user.xp += 50
        task.status = task_data.status
        
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

# إصلاح مسار التعديل السريع PATCH
@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(task_id: int, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.status is not None:
        if task_data.status == "done" and task.status != "done":
            if current_user.xp is None:
                current_user.xp = 0
            current_user.xp += 50
        task.status = task_data.status
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    db.commit()
    db.refresh(task)
    return task

# مسار الدمج Merge المطور
@router.post("/merge")
async def merge_tasks(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task_ids = data.get("task_ids", [])
    tasks = db.query(Task).filter(Task.id.in_(task_ids), Task.user_id == current_user.id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="المهام غير موجودة")

    new_title = data.get("new_title") or (" + ".join([t.title for t in tasks]))

    merged = Task(
        user_id=current_user.id,
        title=new_title[:200],
        description="مدمجة من: " + " + ".join([t.title for t in tasks]),
        status="to_do",
        priority=tasks[0].priority or 3
    )
    db.add(merged)
    for t in tasks:
        db.delete(t)
    db.commit()
    db.refresh(merged)
    return {"status": "success", "new_task_id": merged.id}

# مسار الفصل Fork
@router.post("/{task_id}/fork")
async def fork_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    original = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Task not found")
    forked = Task(
        user_id=current_user.id,
        title=f"(Fork) {original.title}",
        description=original.description,
        priority=original.priority,
        status="to_do"
    )
    db.add(forked)
    db.commit()
    db.refresh(forked)
    return {"message": "Task forked successfully", "new_task_id": forked.id}
