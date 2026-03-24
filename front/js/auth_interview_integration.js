/**
 * Fakarni AI - Onboarding & Interview Integration
 * * الملف ده مسؤول عن توجيه المستخدم بعد ما يعمل Login/Signup
 * عشان يتأكد إن المستخدم عمل "جلسة التعارف" مع فكرني (Learning Interview) 
 * قبل ما يدخله على لوحة التحكم الأساسية.
 */

// ===== STEP 1: Update Login Response Handler =====
// الدالة دي بتشتغل أول ما المستخدم يعمل تسجيل دخول بنجاح

async function handleLoginSuccess(data) {
    // بناخد التوكن (عشان فكرني يعرف مين اللي بيكلمه)
    localStorage.setItem("token", data.access_token);
    const token = data.access_token || localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (token) {
        // بنحفظ اسم المستخدم عشان فكرني يناديه بيه
        if (data.full_name || data.name) {
            localStorage.setItem('user_name', data.full_name || data.name || "يا حبيب");
        }
        
        // بنسأل السيرفر: هل المستخدم ده قعد مع فكرني قبل كده وحدد أحلامه وطريقة مذاكرته؟
        try {
            const statusResponse = await fetch('/api/learning/profile-status', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (statusResponse.ok) {
                const status = await statusResponse.json();
                
                // لو لسه معملش جلسة التعارف، نوديه ليها
                if (status.redirect_to_interview) {
                    console.log("فكرني لسه ميعرفكش كويس، يلا بينا على جلسة التعارف! 🤝");
                    window.location.href = '/learning-interview';
                } else {
                    // لو عارفه ومظبط دنيته، يدخل على الهوم يكمل شغله
                    console.log("أهلاً بيك في الأكاديمية يا بطل، يلا نشوف ورانا إيه! 🚀");
                    window.location.href = '/home';
                }
            } else {
                // لو حصلت مشكلة في التشيك، نوديه الهوم كحل بديل
                window.location.href = '/home';
            }
        } catch (error) {
            console.warn('فكرني مش قادر يتأكد إنت عملت الإنترفيو ولا لأ:', error);
            // حل بديل للطوارئ
            window.location.href = '/home';
        }
    }
}

// ===== STEP 2: Update your signup/login form =====
// (أمثلة برمجية لكيفية استخدام الدالة دي في ملف app.js - تم تطبيقها بالفعل في التحديثات السابقة)
/*
async function handleLoginForm(e) {
    // ... logic ...
    if (response.ok) {
        const data = await response.json();
        // بننادي الدالة السحرية بتاعتنا
        handleLoginSuccess(data);
    }
}
*/

// ===== STEP 3: Modify Backend Auth Controller (auth.py) =====
// ده تذكير ليك عشان تظبط الباك إند (FastAPI) يبعت حالة الإنترفيو مع الـ Login

/*
# في ملف auth.py في الباك إند:
from services.learning_profile_service import LearningProfileService

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    # 1. المصادقة
    db_user = UserService.authenticate_user(db, user.email, user.password)
    
    # 2. إنشاء التوكن
    token = create_access_token(data={"sub": str(db_user.id)})
    
    # 3. التأكد من وجود بروفايل فكرني (الأحلام والأهداف)
    profile_exists = LearningProfileService.check_profile_exists(db, db_user.id)
    
    return {
        "message": "Login successful", 
        "full_name": db_user.full_name,
        "access_token": token,
        "interview_completed": profile_exists,
        "redirect": "/learning-interview" if not profile_exists else "/home"
    }
*/

// ===== STEP 4: Handle Token from Cookies/Storage =====
// (دالة مساعدة لإرسال التوكن مع كل الطلبات - تم دمجها في api.js)

// ===== STEP 5: Protect Routes =====
// عشان لو مستخدم حب يتذاكى ويدخل الهوم من غير ما يعمل لوجين

/*
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    
    if (!token && !window.location.pathname.startsWith('/')) {
        // لو معندوش توكن ومش في صفحة اللوجين، اطرده بره
        console.log("إنت رايح فين من غير تسجيل دخول؟ ارجع يا حبيب! 🛑");
        window.location.href = '/';
        return;
    }
});
*/

// ===== COMPLETE FLOW DIAGRAM (Fakarni Version) =====
/*
تسجيل الدخول/إنشاء حساب
      ↓
الباك إند بيتأكد من البيانات وبيطلع Token
      ↓
السيرفر بيشوف: هل المستخدم ده عمل بروفايل فكرني (الأحلام والـ Pacing)؟
      ↓
الفرونت إند (الملف ده) بيستقبل الرد
      ↓
لو لسه معملوش ⬅️ تحويل لصفحة /learning-interview (جلسة التعارف)
لو عمله ومظبطه ⬅️ تحويل لصفحة /home (الـ Dashboard بتاعت فكرني)
*/

// ===== ERROR HANDLING =====
// التعامل مع مشاكل التوكن والصلاحيات

async function handleAuthError(error) {
    if (error.status === 401) {
        // التوكن خلص أو اتضرب
        console.log("التوكن بتاعك خلص أو مش مظبوط، هتحتاج تسجل دخول تاني 🔄");
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        window.location.href = '/';
    } else if (error.status === 403) {
        // ملوش صلاحية
        if (typeof showPopup === "function") {
            showPopup("ممنوع الدخول ⛔", "فكرني بيقولك الصفحة دي مش بتاعتك!");
        } else {
            alert("فكرني بيقولك: ممنوع الدخول يا حبيب!");
        }
    } else {
        console.error('مشكلة في المصادقة:', error);
    }
}

export {
    handleLoginSuccess,
    handleAuthError
    // LearningInterviewManager (يتم استيراده من ملفه الخاص)
};