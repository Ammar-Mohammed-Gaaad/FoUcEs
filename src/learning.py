from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, LearningProfile
from schemas import LearningProfileResponse, LearningProfileCreate, LearningProfileUpdate, UserUpdate
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
