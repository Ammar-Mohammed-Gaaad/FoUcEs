from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
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

# ── جلب كل المهام ──────────────────────────────────────────────────────────
@router.get("/", response_model=List[TaskResponse])
async def list_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

# ── إنشاء مهمة جديدة (مع دعم parent_id و task_type) ─────────────────────
@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # تحقق من وجود الأب لو تم إرسال parent_id
    if task_data.parent_id:
        parent = db.query(Task).filter(
            Task.id == task_data.parent_id,
            Task.user_id == current_user.id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent task not found")

    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        goal_id=task_data.goal_id,
        priority=task_data.priority,
        deadline=task_data.deadline,
        parent_id=task_data.parent_id,
        task_type=task_data.task_type or "task",
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# ── إضافة مهمة فرعية (ابن) تحت مهمة أب ──────────────────────────────────
@router.post("/{parent_id}/subtask", response_model=TaskResponse)
async def create_subtask(
    parent_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    parent = db.query(Task).filter(Task.id == parent_id, Task.user_id == current_user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent task not found")

    subtask = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        goal_id=task_data.goal_id or parent.goal_id,
        priority=task_data.priority,
        deadline=task_data.deadline,
        parent_id=parent_id,
        task_type="subtask",
        status="to_do",
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask

# ── جلب المهمة + أبناؤها ─────────────────────────────────────────────────
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/{task_id}/children", response_model=List[TaskResponse])
async def get_children(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """جলب كل المهام الفرعية (الأبناء) لمهمة معينة"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    children = db.query(Task).filter(Task.parent_id == task_id, Task.user_id == current_user.id).all()
    return children

# ── تعديل مهمة ───────────────────────────────────────────────────────────
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
    if task_data.parent_id is not None:
        task.parent_id = task_data.parent_id
    if task_data.task_type is not None:
        task.task_type = task_data.task_type
    if task_data.status is not None:
        if task_data.status == "done" and task.status != "done":
            if current_user.xp is None:
                current_user.xp = 0
            current_user.xp += 50
        task.status = task_data.status
        
    db.commit()
    db.refresh(task)
    return task

# ── تعديل جزئي PATCH ─────────────────────────────────────────────────────
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
    # parent_id: نقبل null صريح للفصل (detach) — مختلف عن "غير مرسل"
    if "parent_id" in task_data.model_fields_set:
        task.parent_id = task_data.parent_id  # ممكن يكون None (فصل) أو رقم (ربط)
        if task_data.parent_id is None:
            task.task_type = "task"  # لما بنفصل نرجعها مهمة أساسية
    if task_data.task_type is not None:
        task.task_type = task_data.task_type
    db.commit()
    db.refresh(task)
    return task

# ── حذف مهمة ─────────────────────────────────────────────────────────────
@router.delete("/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # الأبناء يصبحوا مستقلين بدل ما يتحذفوا
    db.query(Task).filter(Task.parent_id == task_id).update(
        {"parent_id": None, "task_type": "task"}
    )
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

# ── فصل مهمة (Detach) — تحويل الابن لمهمة مستقلة ────────────────────────
@router.post("/{task_id}/detach", response_model=TaskResponse)
async def detach_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """فصل مهمة فرعية وتحويلها لمهمة مستقلة"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.parent_id is None:
        raise HTTPException(status_code=400, detail="Task is already independent")

    task.parent_id = None
    task.task_type = "task"
    db.commit()
    db.refresh(task)
    return task

# ── فورك (Fork) — نسخ مهمة كأخ (Sibling) تحت نفس الأب ────────────────
@router.post("/{task_id}/fork", response_model=TaskResponse)
async def fork_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """نسخ مهمة بنفس parent_id عشان تظهر كفرع أخوي في الجراف"""
    original = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Task not found")

    forked = Task(
        user_id=current_user.id,
        title=f"(Fork) {original.title}",
        description=original.description,
        goal_id=original.goal_id,
        priority=original.priority,
        deadline=original.deadline,
        parent_id=original.parent_id,  # نفس أبو الأصل → يظهر كأخ في الشجرة
        task_type=original.task_type,
        status="to_do",
    )
    db.add(forked)
    db.commit()
    db.refresh(forked)
    return forked

# ── دمج (Merge) — دمج مهمتين أو أكثر في مهمة واحدة ─────────────────────
@router.post("/merge")
async def merge_tasks(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    دمج قائمة مهام في مهمة واحدة جديدة وحذف القديمة.
    Body: { "task_ids": [1, 2, 3], "new_title": "اسم اختياري" }
    """
    task_ids = data.get("task_ids", [])
    if len(task_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tasks required to merge")

    tasks = db.query(Task).filter(Task.id.in_(task_ids), Task.user_id == current_user.id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Tasks not found")

    new_title = data.get("new_title") or (" + ".join([t.title for t in tasks]))
    merged_desc = "Merged from:\n" + "\n".join([f"- {t.title}: {t.description or ''}" for t in tasks])

    merged = Task(
        user_id=current_user.id,
        title=new_title[:200],
        description=merged_desc[:1000],
        goal_id=tasks[0].goal_id,
        priority=tasks[0].priority or 3,
        parent_id=None,
        task_type="task",
        status="to_do",
    )
    db.add(merged)

    # أبناء المهام المدموجة ينتقلوا للمهمة الجديدة
    for t in tasks:
        db.query(Task).filter(Task.parent_id == t.id).update({"parent_id": merged.id})
        db.delete(t)

    db.commit()
    db.refresh(merged)
    return {"status": "success", "new_task_id": merged.id, "title": merged.title}
