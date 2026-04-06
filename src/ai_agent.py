import json
import os
from google import genai
from google.genai import types
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import PyPDF2
from typing import Optional

# استدعاء ملفات المشروع
from database import get_db
import models

import pathlib
from dotenv import load_dotenv

router = APIRouter()

<<<<<<< HEAD
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
=======
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class Message(BaseModel):
    message: str
    user_id: Optional[int] = 1
>>>>>>> cc918e1760a69951c9074c6e522655b7664294ea
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
<<<<<<< HEAD
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
=======
        system_instruction = """أنت 'فكرني AI'، مساعد شخصي ذكي لإدارة المهام والإنتاجية.
مهمتك: فهم رسالة المستخدم وتحديد نيته.
هل يطلب المستخدم خطة عمل أو إنشاء تقسيم لشيء محدد؟ إذا نعم، قم بوضع "action": "create_tasks" وإملاء المهام.
هل يطلب المستخدم مجرد دردشة، سؤال عادي، أو نصيحة؟ إذا نعم، قم بوضع "action": "chat" واترك المهام فارغة.

قواعد صارمة جداً:
1. الرد بصيغة JSON حصرياً للمفتاح.
2. الـ JSON يجب أن يحتوي على هذه المفاتيح: "action"، "reply"، و "tasks".
3. مفتاح "action" يجب أن يكون إما "chat" أو "create_tasks".
4. مفتاح "reply" يحتوي على تشجيع أو إجابة موجزة باللهجة المصرية.
5. مفتاح "tasks" مصفوفة (Array) تحتوي على المهام (من 2 إلى 5 مهام)، وفقط إذا كان action هو create_tasks. كل مهمة لها "title" و "duration_minutes".

مثال للإجابات:
>>>>>>> cc918e1760a69951c9074c6e522655b7664294ea
{
  "action": "create_tasks",
  "reply": "يا بطل، قسمتلك موضوعك لخطوات صغيرة عشان نخلص بسرعة، توكلنا على الله!",
  "tasks": [
    {"title": "كتابة المقدمة", "duration_minutes": 15}
  ]
}
"""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.3
        )

<<<<<<< HEAD
        raw_content = response.choices[0].message.content
        print("🤖 Raw Groq Response:", raw_content)

        # تنظيف الرد من علامات الماركدون لو الذكاء الاصطناعي بعتها
        cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()
        parsed_content = json.loads(cleaned_content)
=======
        prompt = f"[معلومات من الملف إن وجدت]:\n{msg.file_context}\n\n" if msg.file_context else ""
        prompt += f"رسالة المستخدم: {msg.message}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        
        parsed_content = json.loads(response.text)
>>>>>>> cc918e1760a69951c9074c6e522655b7664294ea

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
                    description=f"المدة المقترحة: {duration} دقيقة (مضافة بواسطة فكرني الذكي 🤖)",
                    status="to_do",
                    priority=3
                )
                db.add(new_task)
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
<<<<<<< HEAD
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "أنت 'فكرني AI'، مساعد ذكي لتبسيط الأمور. قم بتحليل وتقسيم المهمة المعطاة لك إلى 3-5 خطوات عملية دقيقة. أعد الرد كنص مقسم ومختصر باللهجة المصرية التشجيعية الجذابة (بدون JSON)."},
                {"role": "user", "content": f"السياق: {req.context}\nالمهمة المطلوب تقسيمها: {req.task}"}
            ],
=======
        system_instruction = "أنت 'فكرني AI'، مساعد ذكي لتبسيط الأمور. قم بتحليل وتقسيم المهمة المعطاة لك إلى 3-5 خطوات عملية دقيقة. أعد الرد كنص مقسم ومختصر باللهجة المصرية التشجيعية الجذابة (بدون JSON)."
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
>>>>>>> cc918e1760a69951c9074c6e522655b7664294ea
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
            
<<<<<<< HEAD
        content = content[:15000] # Safe limit for prompt window length
            
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": '''أنت معلم ذكي. مهمتك هي إنشاء اختبار (Quiz) مكون من 3 إلى 5 أسئلة متعددة الاختيارات بناءً على النص المُرفق حصرياً.
=======
        content = content[:30000]
        
        system_instruction = '''أنت معلم ذكي. مهمتك هي إنشاء اختبار (Quiz) مكون من 3 إلى 5 أسئلة متعددة الاختيارات بناءً على النص المُرفق حصرياً.
>>>>>>> cc918e1760a69951c9074c6e522655b7664294ea
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