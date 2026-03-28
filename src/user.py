from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from learning import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/me")
async def get_my_profile(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """جلب بيانات المستخدم الحالي للبروفايل والهيدر"""
    return {
        "full_name": current_user.full_name,
        "job_title": current_user.job_title,
        "bio": current_user.bio,
        "email": current_user.email
    }

@router.post("/update")
async def update_my_profile(data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """تحديث بيانات المستخدم من صفحة البروفايل"""
    current_user.full_name = data.get("full_name", current_user.full_name)
    current_user.job_title = data.get("job_title", current_user.job_title)
    current_user.bio = data.get("bio", current_user.bio)
    
    db.commit()
    return {"status": "success", "message": "Profile updated"}
