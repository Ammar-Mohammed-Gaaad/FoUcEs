from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, LearningProfile
from schemas import LearningProfileResponse, LearningProfileCreate
from database import get_db
from utils import verify_token
from fastapi import Header

router = APIRouter(prefix="/api/learning", tags=["learning"])

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

@router.get("/profile-status")
async def profile_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile or not profile.completed_interview:
        return {"redirect_to_interview": True, "completed": False}
    return {"redirect_to_interview": False, "completed": True}

@router.get("/my-profile", response_model=LearningProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/my-profile", response_model=LearningProfileResponse)
async def update_profile(profile_data: LearningProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(LearningProfile).filter(LearningProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.learning_style = profile_data.learning_style
    profile.learning_pace = profile_data.learning_pace
    profile.goals = profile_data.goals
    profile.motivation_type = profile_data.motivation_type
    profile.completed_interview = True
    db.commit()
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
