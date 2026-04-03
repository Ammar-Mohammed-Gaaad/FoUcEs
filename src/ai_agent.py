import json
import os
from groq import Groq
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import PyPDF2

# استدعاء ملفات المشروع
from database import get_db
import models

import pathlib
from dotenv import load_dotenv

router = APIRouter()

def get_groq_client():
    """دالة تقرأ ملف .env ديناميكياً مع كل طلب عشان لو غيرت المفتاح السيرفر يحس بيه بدون ريستارت"""
    env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("API Key is missing from .env file!")
    
    return Groq(api_key=api_key.strip())

class Message(BaseModel):
    message: str
    user_id: int = 1  # افتراضي
    file_context: Optional[str] = None

class BreakdownRequest(BaseModel):
    task: str
    context: str = "User requested AI breakdown from home dashboard"
    user_id: int = 1

@router.post("/api/ai/chat")
async def chat(msg: Message, db: Session = Depends(get_db)):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """أنت 'فكرني AI'، مساعدك الشخصي العبقري.
مهامك:
1. لو المستخدم طلب "تقسيم" أو "خطة" أو "إضافة مهام": ضع "action": "create_tasks" وكريه المهام في مصفوفة tasks.
2. لو طلب "دردشة" أو "سؤال" أو "مساعدة عامة": ضع "action": "chat" ورد عليه بلباقة.
3. لو طلب "تنظيم" أو "تحديث": رد عليه وشجعه.

قواعد الـ JSON:
- "action": "create_tasks" أو "chat".
- "reply": ردك باللهجة المصرية المشجعة.
- "tasks": مصفوفة المهام لو النية إضافة (كل مهمة لها title و duration_minutes). لو دردشة سيبها فاضية [].

مثال طلب مهام:
{
  "action": "create_tasks",
  "reply": "يا بطل، قسمتلك موضوعك لخطوات صغيرة عشان نخلص بسرعة، توكلنا على الله!",
  "tasks": [
    {"title": "كتابة المقدمة", "duration_minutes": 15}
  ]
}

مثال للدردشة العادية:
{
  "action": "chat",
  "reply": "صباح الفل يا صاحبي! أنا موجود لو محتاجني أساعدك في تقسيم أي هدف طويل.",
  "tasks": []
}
"""},
                {"role": "user", "content": f"رسالة المستخدم: {msg.message}\n\n[معلومات مرجعية يجب الاعتماد عليها إن وجدت: {msg.file_context}]" if msg.file_context else msg.message}
            ],
            temperature=0.5
        )

        raw_content = response.choices[0].message.content
        print("🤖 Raw Groq Response:", raw_content)

        # تنظيف الرد من علامات الماركدون لو الذكاء الاصطناعي بعتها
        cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()
        parsed_content = json.loads(cleaned_content)

        saved_tasks_count = 0
        action = parsed_content.get("action", "chat")

        if action == "create_tasks" and "tasks" in parsed_content and isinstance(parsed_content["tasks"], list):
            for task_data in parsed_content["tasks"]:
                duration = task_data.get('duration_minutes', 30)
                try:
                    duration = int(duration)
                except:
                    duration = 30
                    
                new_task = models.Task(
                    user_id=msg.user_id,
                    title=task_data.get("title", "مهمة جديدة"),
                    description=f"المدة المقترحة: {duration} دقيقة (مضافة بواسطة الذكاء الاصطناعي 🤖)",
                    status="to_do",
                    priority=3
                )
                db.add(new_task)
                saved_tasks_count += 1
            
            db.commit()
            parsed_content["database_status"] = f"تم حفظ {saved_tasks_count} مهام بنجاح!"
        else:
            # تنظيف المصفوفة إذا كان مجرد دردشة
            parsed_content["tasks"] = []
            parsed_content["database_status"] = None

        return parsed_content

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return {
            "action": "chat",
            "reply": "معلش يا بطل، حصل خطأ في السيستم ❌ حاول توضح طلبك أكتر.",
            "tasks": [],
            "database_status": None
        }

@router.post("/api/ai-breakdown")
async def ai_breakdown(req: BreakdownRequest, db: Session = Depends(get_db)):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت 'فكرني AI'، مساعد ذكي لتبسيط الأمور. قم بتحليل وتقسيم المهمة المعطاة لك إلى 3-5 خطوات عملية دقيقة. أعد الرد كنص مقسم ومختصر باللهجة المصرية التشجيعية الجذابة (بدون JSON)."},
                {"role": "user", "content": f"السياق: {req.context}\nالمهمة المطلوب تقسيمها: {req.task}"}
            ],
            temperature=0.4
        )
        return {"breakdown": response.choices[0].message.content}
    except Exception as e:
        print("🔥 ERROR in ai_breakdown:", str(e))
        return {"breakdown": "حصل خطأ أثناء الاتصال بالذكاء الاصطناعي ❌"}

@router.post("/api/ai/generate-quiz")
async def generate_quiz(file: UploadFile = File(...)):
    try:
        content = ""
        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file.file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        else:
            raw_content = await file.read()
            content = raw_content.decode("utf-8")
            
        content = content[:15000] # Safe limit for prompt window length
            
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": '''أنت معلم ذكي. مهمتك هي إنشاء اختبار (Quiz) مكون من 3 إلى 5 أسئلة متعددة الاختيارات بناءً على النص المُرفق حصرياً.
الرد يجب أن يكون صيغة JSON فقط، بدون أي نصوص، على الشكل التالي:
{
  "questions": [
    {
      "question": "نص السؤال العبقري؟",
      "options": ["خيار 1", "خيار 2", "خيار 3", "خيار 4"],
      "answer": "خيار 1"
    }
  ]
}'''},
                {"role": "user", "content": f"المحتوى المرجعي:\n{content}"}
            ],
            temperature=0.3
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("🔥 ERROR in generate_quiz:", str(e))
        return {"questions": []}

@router.post("/api/ai/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        content = ""
        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file.file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
        else:
            raw_content = await file.read()
            content = raw_content.decode("utf-8")
            
        content = content[:15000] # Safe limit
        return {"context": content}
    except Exception as e:
        print("🔥 ERROR in extract_text:", str(e))
        return {"context": ""}