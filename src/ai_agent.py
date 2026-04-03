import json
import os
from groq import Groq
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import PyPDF2

# استدعاء ملفات المشروع
from database import get_db
import models

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

class Message(BaseModel):
    message: str
    user_id: int = 1  # افتراضي
    file_context: str = None

class BreakdownRequest(BaseModel):
    task: str
    context: str = "User requested AI breakdown from home dashboard"
    user_id: int = 1

@router.post("/api/ai/chat")
async def chat(msg: Message, db: Session = Depends(get_db)):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """أنت 'فكرني AI'، مساعد شخصي ذكي لإدارة المهام والإنتاجية.
مهمتك: فهم رسالة المستخدم وتحديد نيته.
هل يطلب المستخدم خطة عمل أو إنشاء تقسيم لشيء محدد؟ إذا نعم، قم بوضع "action": "create_tasks" وإملاء المهام.
هل يطلب المستخدم مجرد دردشة، سؤال عادي، أو نصيحة؟ إذا نعم، قم بوضع "action": "chat" واترك المهام فارغة.

قواعد صارمة جداً:
1. الرد بصيغة JSON حصرياً.
2. الـ JSON يجب أن يحتوي على هذه المفاتيح: "action"، "reply"، و "tasks".
3. مفتاح "action" يجب أن يكون إما "chat" أو "create_tasks".
4. مفتاح "reply" يحتوي على تشجيع أو إجابة موجزة باللهجة المصرية.
5. مفتاح "tasks" مصفوفة (Array) تحتوي على المهام (من 2 إلى 5 مهام)، وفقط إذا كان action هو create_tasks. كل مهمة لها "title" و "duration_minutes".

مثال إذا كان طلب مهام:
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
        parsed_content = json.loads(raw_content)

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