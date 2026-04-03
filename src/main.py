import os
import pathlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# استدعاء إعدادات الداتا بيز والموديلز
from database import Base, engine
import models  # 👈 السطر ده سحري ومهم جداً عشان السيرفر يقرا الجداول ويكريتها

# استدعاء ملفات الراوترز (الـ APIs)
import auth
import learning
import tasks
from ai_agent import router as ai_router
from config import settings
from sqlalchemy.orm import Session
from database import get_db
import learning
from pydantic import BaseModel
from fastapi import Depends, HTTPException

class ProfileUpdate(BaseModel):
    full_name: str
    job_title: str
    bio: str

# 👇 تحميل ملف .env عشان مفاتيح الـ API
env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 👇 ترقية الجداول وتعديلها تلقائياً بدون خسارة الداتا القديمة
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0"))
        conn.commit()
except Exception:
    pass

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0"))
        conn.commit()
except Exception:
    pass

# 👇 إنشاء الجداول في قاعدة البيانات أوتوماتيك أول ما السيرفر يقوم
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fakarni AI Backend", version="1.0.0", description="Backend API for Fakarni learning platform")

# إعداد مسار الفرونت إند
frontend_dir = Path(__file__).resolve().parent.parent / "front"

# إعداد الـ CORS عشان الفرونت إند يقدر يكلم الباك إند بدون مشاكل (Security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل كل الـ Routers (عشان الـ Endpoints تشتغل)
app.include_router(auth.router)
app.include_router(learning.router)
app.include_router(tasks.router)
app.include_router(ai_router)
@app.get("/api/user/me")
async def get_my_profile(current_user: models.User = Depends(learning.get_current_user), db: Session = Depends(get_db)):
    return {
        "full_name": current_user.full_name or "يا هندسة",
        "job_title": current_user.job_title or "مطور برمجيات",
        "bio": current_user.bio or "لا يوجد نبذة",
        "email": current_user.email
    }

@app.post("/api/user/update")
async def update_profile(data: ProfileUpdate, current_user: models.User = Depends(learning.get_current_user), db: Session = Depends(get_db)):
    try:
        current_user.full_name = data.full_name
        current_user.job_title = data.job_title
        current_user.bio = data.bio
        
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return {"status": "success", "message": "تم التحديث بنجاح"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# مسارات فحص صحة السيرفر (Health Checks)
@app.get("/api/health")
async def health_api():
    return {"status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# =======================================================
# ربط ملفات الفرونت إند (Static Files) - لازم تكون في الآخر
# =======================================================

app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")
app.mount("/img", StaticFiles(directory=str(frontend_dir / "img")), name="img")

# ربط ملفات الـ HTML في المسار الرئيسي (ده اللي بيعرض الموقع نفسه)
app.mount("/", StaticFiles(directory=str(frontend_dir / "html"), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)