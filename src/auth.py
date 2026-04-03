from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from models import User, LearningProfile
from schemas import UserCreate, UserResponse, TokenResponse
from database import get_db
from utils import hash_password, verify_password, create_access_token, validate_email, validate_password
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"Signup attempt for email: {user_data.email}")  # Debug log
        
        if not validate_email(user_data.email):
            raise HTTPException(status_code=400, detail="البريد الإلكتروني غير صحيح")
        
        print(f"Password received: '{user_data.password}' (length: {len(user_data.password)})")  # Debug log
        
        is_valid, msg = validate_password(user_data.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=msg)
        
        # Check if user exists
        user = db.query(User).filter(User.email == user_data.email).first()
        if user:
            raise HTTPException(status_code=400, detail="المستخدم موجود بالفعل")
        
        # Hash password
        hashed_pwd = hash_password(user_data.password)
        print(f"Password hashed successfully")  # Debug log
        
        # Create user
        new_user = User(email=user_data.email, full_name=user_data.full_name, hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created with ID: {new_user.id}")  # Debug log
        
        # Create learning profile
        learning_profile = LearningProfile(user_id=new_user.id)
        db.add(learning_profile)
        db.commit()
        print(f"Learning profile created")  # Debug log
        
        # Create token
        access_token = create_access_token(data={"sub": str(new_user.id)})
        print(f"Token created successfully")  # Debug log
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=new_user.id,
            name=new_user.full_name,
            email=new_user.email
        )
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Signup error: {str(e)}\n{error_msg}\n")
            
        print(f"Signup error: {str(e)}")  # Debug log
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء الحساب: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="بيانات الدخول غير صحيحة")
    
    # تأمين جلب البيانات حتى لو الأعمدة جديدة وفاضية (تعديل الـ payload للـ id لضمان توافق باقي النظام)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.full_name,
        "email": user.email,
        "user": {
            "email": user.email,
            "full_name": user.full_name or "يا هندسة",
            "job_title": getattr(user, 'job_title', "مطور") or "مطور",
            "bio": getattr(user, 'bio', "") or ""
        }
    }
