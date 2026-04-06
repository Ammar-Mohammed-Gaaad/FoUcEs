import json
import os
import pathlib
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import PyPDF2

# استدعاء ملفات المشروع
from database import get_db
import models

# تحميل .env قبل os.getenv — ده كان السبب الحقيقي إن المفتاح بيرجع فاضي
_env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

router = APIRouter()

class Message(BaseModel):
    message: str
    user_id: Optional[int] = 1
    file_context: Optional[str] = None

class BreakdownRequest(BaseModel):
    task: str
    context: str = "User requested AI breakdown from home dashboard"
    user_id: int = 1

def get_gemini_client():
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

@router.post("/api/ai/chat")
async def chat(msg: Message, db: Session = Depends(get_db)):
    client = get_gemini_client()
    if not client:
        return {"action": "chat", "reply": "مفتاح Gemini API غير موجود في ملف .env ❌ (قم بإنشاء حساب في Google AI Studio واكتب المفتاح)", "tasks": []}
    
    try:
        system_instruction = (
            'أنت فكرني AI، مساعد شخصي ذكي لإدارة المهام والإنتاجية.\n'
            'مهمتك: فهم رسالة المستخدم وتحديد نيته.\n'
            'هل يطلب المستخدم خطة عمل أو إنشاء تقسيم لشيء محدد؟ إذا نعم، قم بوضع action=create_tasks وإملاء المهام.\n'
            'هل يطلب المستخدم مجرد دردشة أو سؤال عادي؟ إذا نعم، قم بوضع action=chat واترك المهام فارغة.\n\n'
            'قواعد صارمة:\n'
            '1. الرد بصيغة JSON حصرياً.\n'
            '2. الـ JSON يحتوي على: action, reply, tasks.\n'
            '3. action = "chat" أو "create_tasks".\n'
            '4. reply = رد مشجع باللهجة المصرية.\n'
            '5. tasks = مصفوفة من 2-5 مهام (فقط لو action هو create_tasks).\n'
            '6. كل مهمة في tasks لها:\n'
            '   - title: اسم المهمة\n'
            '   - duration_minutes: المدة بالدقائق (رقم)\n'
            '   - task_type: "task" للرئيسية أو "subtask" للفرعية\n'
            '   - parent_index: رقم index المهمة الأب (من 0)، أو null لو مستقلة\n\n'
            'مثال تقسيم: المهمة 0 رئيسية (parent_index: null, task_type: "task")، '
            'المهام 1 و2 أبناء لها (parent_index: 0, task_type: "subtask").'
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.3
        )

        prompt = f"[معلومات من الملف إن وجدت]:\n{msg.file_context}\n\n" if msg.file_context else ""
        prompt += f"رسالة المستخدم: {msg.message}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        
        parsed_content = json.loads(response.text)

        saved_tasks_count = 0
        action = parsed_content.get("action", "chat")

        if action == "create_tasks" and "tasks" in parsed_content and isinstance(parsed_content["tasks"], list):
            # خزن الـ IDs الحقيقية عشان نربط الأبناء بالآباء أوتوماتيك
            saved_ids = {}  # index -> real DB id

            for idx, task_data in enumerate(parsed_content["tasks"]):
                duration = task_data.get('duration_minutes', 30)
                try:
                    duration = int(duration)
                except:
                    duration = 30

                # حدد الأب لو في parent_index
                parent_index = task_data.get('parent_index')
                real_parent_id = None
                if parent_index is not None:
                    real_parent_id = saved_ids.get(parent_index)

                task_type = task_data.get('task_type', 'subtask' if real_parent_id else 'task')

                new_task = models.Task(
                    user_id=msg.user_id,
                    title=task_data.get("title", "مهمة جديدة"),
                    description=f"المدة المقترحة: {duration} دقيقة",
                    status="to_do",
                    priority=3,
                    parent_id=real_parent_id,
                    task_type=task_type,
                )
                db.add(new_task)
                db.flush()  # نحصل على الـ ID قبل الـ commit
                saved_ids[idx] = new_task.id
                saved_tasks_count += 1
            
            db.commit()
            parsed_content["database_status"] = f"تم حفظ {saved_tasks_count} مهام بنجاح!"
        else:
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
    client = get_gemini_client()
    if not client:
        return {"breakdown": "مفتاح Gemini API غير موجود ❌"}
        
    try:
        system_instruction = "أنت 'فكرني AI'، مساعد ذكي لتبسيط الأمور. قم بتحليل وتقسيم المهمة المعطاة لك إلى 3-5 خطوات عملية دقيقة. أعد الرد كنص مقسم ومختصر باللهجة المصرية التشجيعية الجذابة (بدون JSON)."
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4
        )
        
        prompt = f"السياق: {req.context}\nالمهمة المطلوب تقسيمها: {req.task}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        return {"breakdown": response.text}
    except Exception as e:
        print("🔥 ERROR in ai_breakdown:", str(e))
        return {"breakdown": "حصل خطأ أثناء الاتصال بالذكاء الاصطناعي ❌"}

@router.post("/api/ai/generate-quiz")
async def generate_quiz(file: UploadFile = File(...)):
    client = get_gemini_client()
    if not client:
        return {"questions": []}
        
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
            
        content = content[:30000]
        
        system_instruction = '''أنت معلم ذكي. مهمتك هي إنشاء اختبار (Quiz) مكون من 3 إلى 5 أسئلة متعددة الاختيارات بناءً على النص المُرفق حصرياً.
الرد يجب أن يكون صيغة JSON فقط، بدون أي نصوص، على الشكل التالي:
{
  "questions": [
    {
      "question": "نص السؤال العبقري؟",
      "options": ["خيار 1", "خيار 2", "خيار 3", "خيار 4"],
      "answer": "خيار 1"
    }
  ]
}'''
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.3
        )
        
        prompt = f"المحتوى المرجعي:\n{content}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        return json.loads(response.text)
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
            
        content = content[:30000]
        return {"context": content}
    except Exception as e:
        print("🔥 ERROR in extract_text:", str(e))
        return {"context": ""}