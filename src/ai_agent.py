import json
import os
from groq import Groq
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# استدعاء ملفات المشروع بتاعتك
from database import get_db
import models

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

class Message(BaseModel):
    message: str
    user_id: int = 1  # هنديله رقم 1 افتراضي عشان ميضربش إيرور وإحنا بنجرب

@router.post("/api/ai/chat")
async def chat(msg: Message, db: Session = Depends(get_db)):
    try:
        # 1. نبعت الطلب لـ Groq ونطلب منه JSON بشكل صارم جداً
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """أنت 'فكرني AI'، مساعد شخصي ذكي لإدارة المهام والإنتاجية.
مهمتك الوحيدة: تحويل أي رسالة يكتبها المستخدم (سواء كانت هدف كبير، مشروع، أو حتى مجرد فكرة عامة) إلى خطة عمل مقسمة لمهام صغيرة.

قواعد صارمة جداً:
1. ممنوع الرد بنص عادي نهائياً. يجب أن يكون الرد بصيغة JSON فقط.
2. الـ JSON يجب أن يحتوي حصرياً على مفتاحين: "reply" و "tasks".
3. مفتاح "reply" يحتوي على تشجيع قصير جداً باللهجة المصرية.
4. مفتاح "tasks" يحتوي على مصفوفة (Array) من المهام (من 2 إلى 5 مهام). كل مهمة لها "title" (عنوان واضح) و "duration_minutes" (رقم صحيح يعبر عن الدقائق).

مثال للرد الذي يجب أن تلتزم به إجبارياً:
{
  "reply": "يا بطل، قسمتلك موضوع الفرونت إند لخطوات صغيرة عشان تخلصهم بسرعة، توكلنا على الله!",
  "tasks": [
    {"title": "تجهيز هيكل الموقع الأساسي بـ HTML", "duration_minutes": 30},
    {"title": "تنسيق الألوان والخطوط بـ CSS", "duration_minutes": 45},
    {"title": "إضافة التفاعلات الأساسية بـ JavaScript", "duration_minutes": 60}
  ]
}
"""},
                {"role": "user", "content": msg.message}
            ],
            temperature=0.5 # قللنا الإبداع شوية عشان يلتزم بالتنسيق
        )

        # 2. نحول الرد لـ Dictionary
        raw_content = response.choices[0].message.content
        parsed_content = json.loads(raw_content)

        # 3. استخراج التاسكات وحفظها في قاعدة البيانات مع حماية من الأخطاء
        saved_tasks_count = 0
        if "tasks" in parsed_content and isinstance(parsed_content["tasks"], list):
            for task_data in parsed_content["tasks"]:
                
                # تأمين عشان لو الموديل بعت الدقايق بشكل غلط (نص بدل رقم)
                duration = task_data.get('duration_minutes', 30)
                try:
                    duration = int(duration)
                except:
                    duration = 30 # رقم افتراضي لو فشل التحويل
                    
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
        return parsed_content

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return {
            "reply": "معلش يا بطل، حصل خطأ في السيستم ❌ حاول توضح طلبك أكتر.",
            "tasks": []
        }