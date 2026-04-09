from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, LearningProfile, FocusSession
from schemas import LearningProfileResponse, LearningProfileCreate, LearningProfileUpdate, UserUpdate
from database import get_db
from utils import verify_token
from fastapi import Header
from pydantic import BaseModel
from datetime import datetime, timedelta

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
    
    # Ensure goals is never None
    if profile.goals is None:
        profile.goals = ""
    
    return profile

@router.put("/my-profile", response_model=LearningProfileResponse)
async def update_profile(profile_data: LearningProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.learning_style = profile_data.learning_style
    profile.learning_pace = profile_data.learning_pace
    profile.goals = profile_data.goals or ""  # Ensure empty string if None
    profile.motivation_type = profile_data.motivation_type
    profile.completed_interview = True
    db.commit()
    db.refresh(profile)
    
    # Ensure goals is never None in response
    if profile.goals is None:
        profile.goals = ""
    
    return profile

@router.patch("/my-profile", response_model=LearningProfileResponse)
async def partial_update_profile(profile_data: LearningProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update learning profile with optional fields"""
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update only provided fields
    if profile_data.learning_style is not None:
        profile.learning_style = profile_data.learning_style
    if profile_data.learning_pace is not None:
        profile.learning_pace = profile_data.learning_pace
    if profile_data.goals is not None:
        profile.goals = profile_data.goals or ""
    if profile_data.motivation_type is not None:
        profile.motivation_type = profile_data.motivation_type
    
    db.commit()
    db.refresh(profile)
    
    # Ensure goals is never None in response
    if profile.goals is None:
        profile.goals = ""
    
    return profile

@router.patch("/user-profile", response_model=LearningProfileResponse)
async def update_user_profile(user_data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user full_name and email"""
    # Update User model
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(User.email == user_data.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = user_data.email
    
    # Also get and update learning profile to return it
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile.goals is None:
        profile.goals = ""
    
    db.commit()
    db.refresh(current_user)
    db.refresh(profile)
    
    return profile

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

# ================= نظام جلسات التركيز (Focus Sessions) =================
class FocusSessionCreate(BaseModel):
    duration_minutes: int

@router.post("/focus-session")
async def log_focus_session(data: FocusSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """تسجيل جلسة تركيز جديدة ومنح XP"""
    session = FocusSession(
        user_id=current_user.id,
        duration_minutes=data.duration_minutes,
        focus_score=min(100, data.duration_minutes * 2)  # نقاط التركيز
    )
    db.add(session)
    
    # منح XP (1 XP لكل دقيقة تركيز)
    if current_user.xp is None:
        current_user.xp = 0
    current_user.xp += data.duration_minutes
    
    db.commit()
    return {
        "message": "تم تسجيل الجلسة بنجاح! 🎯",
        "duration": data.duration_minutes,
        "xp_earned": data.duration_minutes,
        "total_xp": current_user.xp
    }

@router.get("/focus-stats")
async def get_focus_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """إحصائيات التركيز لآخر 7 أيام"""
    today = datetime.utcnow().date()
    days_labels = []
    days_data = []
    day_names_ar = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        total = db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0)).filter(
            FocusSession.user_id == current_user.id,
            FocusSession.created_at >= day_start,
            FocusSession.created_at <= day_end
        ).scalar()
        
        days_labels.append(day_names_ar[day.weekday()])
        days_data.append(int(total or 0))
    
    # إجمالي ساعات التركيز
    total_minutes = db.query(func.coalesce(func.sum(FocusSession.duration_minutes), 0)).filter(
        FocusSession.user_id == current_user.id
    ).scalar()
    
    return {
        "labels": days_labels,
        "data": days_data,
        "total_hours": round(int(total_minutes or 0) / 60, 1),
        "total_sessions": db.query(FocusSession).filter(FocusSession.user_id == current_user.id).count()
    }

@router.get("/user-xp")
async def get_user_xp(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """عرض النقاط والمستوى"""
    xp = current_user.xp or 0
    level = xp // 500 + 1
    xp_in_level = xp % 500
    
    # حساب الشارات
    badges = []
    if xp >= 100:
        badges.append({"icon": "🌟", "title": "بداية قوية"})
    if xp >= 500:
        badges.append({"icon": "🔥", "title": "مثابر"})
    if xp >= 1000:
        badges.append({"icon": "🏆", "title": "بطل التركيز"})
    if xp >= 2500:
        badges.append({"icon": "💎", "title": "ماسي"})
    
    return {
        "xp": xp,
        "level": level,
        "xp_in_level": xp_in_level,
        "xp_to_next": 500,
        "badges": badges,
        "streak": current_user.streak or 0
    }

class FocusTimeData(BaseModel):
    minutes: int = 5

@router.post("/add-focus-time")
async def add_focus_time(data: FocusTimeData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Heartbeat: يستقبل دقائق التركيز ويضيفها لـ XP المستخدم"""
    if current_user.xp is None:
        current_user.xp = 0
    current_user.xp += data.minutes * 2  # دقيقة = 2 XP
    db.commit()
    return {"status": "success", "added_xp": data.minutes * 2, "total_xp": current_user.xp}
