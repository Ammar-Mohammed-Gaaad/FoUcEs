/**
 * Fakarni - Profile Page JavaScript
 * ملف إدارة صفحة الملف الشخصي
 * يستخدم البيانات المحفوظة في localStorage
 */

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('📥 تحميل صفحة الملف الشخصي...');
    
    // تحقق من التوكن
    const token = localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) {
        console.warn('❌ لا توجد جلسة مستخدم');
        window.location.href = "/login.html";
        return;
    }
    
    // حمل البيانات من localStorage
    loadProfileFromLocalStorage();
});

// ===== LOAD PROFILE FROM LOCALSTORAGE =====
/**
 * جلب بيانات المستخدم من localStorage
 */
function loadProfileFromLocalStorage() {
    try {
        console.log('📥 جاري تحميل البيانات من localStorage...');
        
        // الحصول على البيانات من localStorage
        const name = localStorage.getItem('user_name') || 'يا صاحبي';
        const email = localStorage.getItem('user_email') || 'لم يتم تعيين بريد إلكتروني';
        const userId = localStorage.getItem('user_id') || 'N/A';
        
        console.log('✅ تم جلب البيانات:', { name, email, userId });
        
        // تحديث الواجهة
        updateProfileUI({
            name: name,
            full_name: name,
            email: email,
            user_id: userId,
            task_count: 0,
            completed_tasks: 0,
            goal_count: 0,
            completed_interview: false
        });
        
    } catch (error) {
        console.error('❌ خطأ في تحميل البيانات:', error);
        showError('خطأ في التحميل', error.message);
    }
}

// ===== UPDATE UI WITH DATA =====
/**
 * تحديث عناصر الصفحة بـ بيانات المستخدم
 */
function updateProfileUI(data) {
    try {
        // البيانات الأساسية
        const name = data.name || data.full_name || 'يا صاحبي';
        const email = data.email || 'لم يتم تعيين بريد إلكتروني';
        
        // تحديث الاسم والبريد
        document.getElementById("username").innerText = name;
        document.getElementById("email").innerText = email;
        
        // تحديث الإحصائيات
        document.getElementById("taskCount").innerText = data.task_count || 0;
        document.getElementById("completedTasks").innerText = data.completed_tasks || 0;
        document.getElementById("goalCount").innerText = data.goal_count || 0;
        
        // حالة الإنترفيو
        if (data.completed_interview) {
            document.getElementById("interviewStatus").innerHTML = '✅ مكتملة';
        } else {
            document.getElementById("interviewStatus").innerHTML = '⏳ قيد الإنجاز';
        }
        
        // تاريخ الانضمام
        if (data.created_at) {
            try {
                const date = new Date(data.created_at);
                document.getElementById("joinDate").innerText = date.toLocaleDateString('ar-EG');
            } catch (e) {
                document.getElementById("joinDate").innerText = '-';
            }
        } else {
            document.getElementById("joinDate").innerText = new Date().toLocaleDateString('ar-EG');
        }
        
        // تحديث الـ Avatar بـ الحرف الأول من الاسم
        const firstLetter = name.charAt(0).toUpperCase();
        document.getElementById("profileAvatar").innerText = firstLetter;
        
        console.log('✅ تم تحديث الواجهة بنجاح');
        
    } catch (error) {
        console.error('❌ خطأ في تحديث الواجهة:', error);
    }
}

// ===== UPDATE PROFILE (SAVE CHANGES) =====
/**
 * حفظ التعديلات على البروفايل
 * ملاحظة: في الوقت الحالي يحفظ في localStorage فقط
 * في المستقبل سيتم ربطها بـ API
 */
async function updateProfile() {
    try {
        // جلب القيم من خانات الإدخال
        const newName = document.getElementById("newName").value.trim();
        const newEmail = document.getElementById("newEmail").value.trim();
        
        // التحقق من أن المستخدم أدخل شيء على الأقل
        if (!newName && !newEmail) {
            showError('تنبيه', 'أدخل على الأقل اسماً أو بريداً إلكترونياً');
            return;
        }
        
        // التحقق من صحة البريد الإلكتروني
        if (newEmail && !validateEmail(newEmail)) {
            showError('بريد غير صحيح', 'الرجاء إدخال بريد إلكتروني صحيح');
            return;
        }

        // تحديث حالة الزر
        const saveBtn = document.getElementById("saveBtn");
        const originalText = saveBtn.innerText;
        saveBtn.disabled = true;
        saveBtn.innerText = '⏳ جاري الحفظ...';

        console.log('💾 جاري حفظ التعديلات...');
        
        // حفظ في localStorage (حتى الآن)
        if (newName) {
            localStorage.setItem('user_name', newName);
        }
        if (newEmail) {
            localStorage.setItem('user_email', newEmail);
        }

        // محاكاة تأخير الـ API
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('✅ تم حفظ البيانات بنجاح');
        
        // إظهار رسالة النجاح
        showSuccess('نجاح!', 'تم تحديث بيانات حسابك بنجاح');
        
        // إعادة تحميل البيانات
        loadProfileFromLocalStorage();
        
        // مسح خانات الإدخال
        document.getElementById("newName").value = '';
        document.getElementById("newEmail").value = '';

    } catch (error) {
        console.error('❌ خطأ في التحديث:', error);
        showError('خطأ في التحديث', error.message);
    } finally {
        // إعادة الزر لحالته الطبيعية
        const saveBtn = document.getElementById("saveBtn");
        saveBtn.disabled = false;
        saveBtn.innerText = '💾 حفظ التعديلات';
    }
}

// ===== RESET FORM =====
/**
 * مسح خانات الإدخال
 */
function resetForm() {
    document.getElementById("newName").value = '';
    document.getElementById("newEmail").value = '';
    console.log('🔄 تم مسح النموذج');
}

// ===== LOGOUT =====
/**
 * تسجيل الخروج من الحساب
 */
function logout() {
    if (confirm('هل أنت متأكد من رغبتك في تسجيل الخروج؟')) {
        try {
            // حذف البيانات من المتصفح
            localStorage.removeItem('token');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_name');
            localStorage.removeItem('user_email');
            localStorage.removeItem('user_id');
            
            console.log('👋 تم تسجيل الخروج بنجاح');
            
            // تحويل للصفحة الرئيسية
            window.location.href = '/';
        } catch (error) {
            console.error('❌ خطأ في تسجيل الخروج:', error);
            showError('خطأ', 'حدث خطأ أثناء تسجيل الخروج');
        }
    }
}

// ===== GO BACK =====
/**
 * العودة للصفحة السابقة
 */
function goBack() {
    window.history.back();
}

// ===== EMAIL VALIDATION =====
/**
 * التحقق من صحة البريد الإلكتروني
 */
function validateEmail(email) {
    const emailRegex = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return emailRegex.test(String(email).toLowerCase());
}

// ===== SHOW ALERTS =====
/**
 * إظهار رسالة نجاح
 */
function showSuccess(title, message) {
    const alert = document.getElementById('successAlert');
    const messageEl = document.getElementById('successMessage');
    messageEl.innerText = `${title}: ${message}`;
    alert.style.display = 'flex';
    
    // إخفاء الرسالة بعد 5 ثوان
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

/**
 * إظهار رسالة خطأ
 */
function showError(title, message) {
    const alert = document.getElementById('errorAlert');
    const messageEl = document.getElementById('errorMessage');
    messageEl.innerText = `${title}: ${message}`;
    alert.style.display = 'flex';
    
    // إخفاء الرسالة بعد 5 ثوان
    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

// ===== CONSOLE LOG =====
console.log('✅ تم تحميل ملف profile.js');
console.log('📝 الملاحظات:');
console.log('  - البيانات تُحمل من localStorage في الوقت الحالي');
console.log('  - عند إنشاء API للبروفايل، غيّر loadProfileFromLocalStorage() لاستخدام API');
console.log('الدوال المتاحة:');
console.log('  - loadProfileFromLocalStorage() - جلب البيانات');
console.log('  - updateProfile() - حفظ التعديلات');
console.log('  - resetForm() - مسح الخانات');
console.log('  - logout() - تسجيل الخروج');
console.log('  - goBack() - العودة للخلف');