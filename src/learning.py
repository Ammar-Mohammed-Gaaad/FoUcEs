from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, LearningProfile, Task, Goal
from schemas import LearningProfileResponse, LearningProfileCreate
from database import get_db
from utils import verify_token
from fastapi import Header

router = APIRouter(prefix="/api/learning", tags=["learning"])

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.get("/profile-status")
async def profile_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile or not profile.completed_interview:
        return {"redirect_to_interview": True, "completed": False}
    return {"redirect_to_interview": False, "completed": True}

@router.get("/my-profile")
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    task_count = db.query(Task).filter(Task.user_id == current_user.id).count()    
    completed_tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.status == "completed").count()    
    goal_count = db.query(Goal).filter(Goal.user_id == current_user.id).count()
    
    return {
        "name": current_user.full_name,
        "email": current_user.email,
        "task_count": task_count,
        "completed_tasks": completed_tasks,
        "goal_count": goal_count,
        "completed_interview": profile.completed_interview,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.put("/my-profile")
async def update_profile(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.full_name = data.get("name", current_user.full_name)
    current_user.email = data.get("email", current_user.email)
    db.commit()
    return {"status": "success", "message": "تم التحديث"}



@router.post("/save-style")
async def save_learning_style(learning_style: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    حفظ أسلوب التعلم بعد إنهاء الإنترفيو
    """
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # تحديث أسلوب التعلم وتحديد أن الإنترفيو مكتمل
    profile.learning_style = learning_style
    profile.completed_interview = True
    db.commit()
    
    return {
        "message": "تم حفظ أسلوب التعلم بنجاح",
        "learning_style": learning_style,
        "completed_interview": True
    }

@router.get("/learning-styles")
async def get_learning_styles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    return {
        "visual": 85,
        "auditory": 60,
        "reading_writing": 70,
        "kinesthetic": 75
    }
