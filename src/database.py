from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# بنستدعي الإعدادات بتاعتك (اللي فيها مسار قاعدة البيانات)
from config import settings

# 1. إنشاء محرك الاتصال (Engine)
# السطر ده ذكي جداً: بيشيك لو الداتا بيز SQLite بيضيف check_same_thread=False عشان FastAPI شغال بـ Threads كتير
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 2. إعداد الجلسة (Session) اللي هنتعامل بيها مع الداتا بيز في كل Request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. الكلاس الأساسي اللي كل الجداول في models.py بتورث منه
Base = declarative_base()

# 4. دالة get_db (Dependency)
# الدالة دي وظيفتها تفتح اتصال بالداتا بيز أول ما يجي Request، وتقفله بأمان أول ما الـ Request يخلص
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()