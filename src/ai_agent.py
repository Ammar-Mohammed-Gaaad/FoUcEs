from groq import Groq
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# 👇 حط مفتاح Groq هنا مباشرة
client = Groq(api_key="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")

class Message(BaseModel):
    message: str

@router.post("/ai/chat")
async def chat(msg: Message):
    try:
        response = client.chat.completions.create(
    model="llama-3.1-8b-instant",  # 👈 الفاصلة هنا
    messages=[
        {"role": "system", "content": "أنت فكرني AI مساعد ذكي باللهجة المصرية"},
        {"role": "user", "content": msg.message}
    ]
    )
        return {
            "reply": response.choices[0].message.content
        }

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return {"reply": "حصل خطأ ❌"}