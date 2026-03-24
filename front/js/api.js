/**
 * Fakarni AI - API Integration Hub
 * بيربط واجهة المستخدم بالذكاء الاصطناعي والباك إند
 */

const API_BASE = "http://localhost:8000/api";

// --- دالة مساعدة لجلب التوكن (عشان السيرفر يعرفك) ---
function getAuthHeaders() {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    return {
        "Content-Type": "application/json",
        "Authorization": token ? `Bearer ${token}` : ""
    };
}

// 1. مراقبة التركيز (Vision / Presence Detection)
// بتبعت صورة من الكاميرا عشان الذكاء الاصطناعي يشوفك مركز ولا سايب اللاب توب
async function checkUserFocus(base64Image) {
    try {
        const response = await fetch(`${API_BASE}/vision/focus-check`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({ image_b64: base64Image })
        });
        return await response.json();
    } catch (error) {
        console.error("مش قادر أبعت الصورة للذكاء الاصطناعي 🙈", error);
    }
}

// 2. جلب شجرة الأحلام والمهام (Graph/Tree Data)
// بتجيب الهيكل الهرمي بتاع المستخدم (Dream ⬇ Goal ⬇ Tasks)
async function fetchLifeTree() {
    try {
        const response = await fetch(`${API_BASE}/graph/life-tree`, {
            method: "GET",
            headers: getAuthHeaders()
        });
        return await response.json();
    } catch (error) {
        console.error("في مشكلة في تحميل أحلامك وتاسكاتك 🕸️", error);
    }
}

// 3. الاتصال المباشر مع "فكرني" (WebSocket Chat)
// اتصال مفتوح للدردشة الحية مع الصديق الذكي بدون تقطيع
function connectFakarniChat() {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    // بنبعت التوكن في الرابط عشان الـ WebSocket مبيقبلش Headers بسهولة
    const ws = new WebSocket(`ws://localhost:8000/api/chat/ws/friend?token=${token}`);
    
    ws.onopen = () => {
        console.log("فكرني متصل وجاهز للدردشة 🤖💬");
    };

    ws.onmessage = (event) => {
        console.log("فكرني بيقولك:", event.data);
        // هنا بتنادي على الدالة اللي بتعرض الرسالة في الشات عندك
        if (typeof displayMessage === "function") {
            displayMessage(event.data, "ai");
        }
    };

    ws.onclose = () => {
        console.log("فكرني قفل الخط، حاول تتصل تاني 📴");
    };

    ws.onerror = (error) => {
        console.error("في مشكلة في الاتصال بفكرني ⚠️", error);
    };

    return ws;
}

// ============================================
// دوال إضافية أساسية لمشروع فكرني (CRUD)
// ============================================

// 4. إضافة مهمة جديدة من الدردشة
async function addNewTask(title, goalId, deadline) {
    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                title: title,
                goal_id: goalId,
                deadline: deadline,
                status: "To Do"
            })
        });
        return await response.json();
    } catch (error) {
        console.error("مقدرتش أضيف التاسك 📝", error);
    }
}