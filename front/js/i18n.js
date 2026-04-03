const translations = {
    ar: {
        // Shared / Navigation
        "btn_dark_mode": "🌙 الوضع المظلم",
        "btn_light_mode": "☀️ الوضع الفاتح",
        "btn_login": "دخول",
        "btn_signup": "حساب جديد",
        "btn_language": "🌍 English",
        "btn_ok": "تمام",
        
        // Homepage / Landing
        "hero_title": "فكرني — رفيقك الذكي لتخطيط حياتك 🚀",
        "hero_subtitle": "افتح قوة عاداتك اليومية، قسم أهدافك الكبيرة لخطوات صغيرة، راقب تركيزك، واوصل لإنتاجية بدون أي إجهاد أو توتر. فكرني مش مجرد تطبيق، ده صاحبك اللي هيشجعك!",
        "hero_start_btn": "يلا نبدأ الرحلة 🔥",
        "hero_account_btn": "عندي حساب بالفعل",
        "features_title": "إيه اللي فكرني هيقدمهولك؟ ✨",
        "feature1_title": "أهداف واضحة",
        "feature1_desc": "بينظم أهدافك المعقدة ويقسمها لمهام صغيرة وواضحة تقدر تنفذها بسهولة.",
        "feature2_title": "خطة ذكية ومفصلة",
        "feature2_desc": "بيحلل دماغك وبيقترح جدول عمل بناءً على أسلوب تعلمك ورتم إنجازك.",
        "feature3_title": "كاميرا التركيز",
        "feature3_desc": "الذكاء الاصطناعي بيراقب تركيزك وإنت شغال عشان يضمن إن مفيش حاجة تشتتك.",
        "feature4_title": "تقارير يومية تفرحك",
        "feature4_desc": "يعطيك رسوم بيانية وتتبع لأدائك عشان تشوف إنجازك بيكبر يوم ورا يوم.",
        "feature5_title": "مساعد الدردشة",
        "feature5_desc": "صديقك فكرني معاك طول الوقت، بيرد على استفساراتك وبيحفزك لما تكسل.",
        "feature6_title": "أمان وخصوصية تامة",
        "feature6_desc": "كل بياناتك، مهامك، وأحلامك محفوظة في خزنة آمنة ومشفرة بالكامل.",
        
        // Auth (Login / Signup)
        "auth_welcome_login": "فكرني معاك",
        "auth_welcome_signup": "حساب جديد",
        "auth_tab_login": "دخول",
        "auth_tab_signup": "تسجيل",
        "lbl_fullname": "الاسم الكامل",
        "lbl_email": "البريد الإلكتروني",
        "lbl_password": "كلمة المرور",
        "lbl_confirm_password": "تأكيد كلمة المرور",
        "btn_submit_login": "دخول",
        "btn_submit_signup": "إنشاء حساب",
        "lnk_forgot_password": "نسيت كلمة المرور؟",
        "lnk_no_account": "ليس لديك حساب؟",
        "lnk_has_account": "عندك حساب فعلاً؟",
        "click_here": "اضغط هنا",
        "login_here": "سجل دخول من هنا",
        "pwd_strength": "قوة كلمة المرور: ",
        "pwd_weak": "ضعيفة 🔴",
        "pwd_medium": "متوسطة 🟠",
        "pwd_strong": "قوية 🟢",
        "signup_subtitle": "سجل دلوقتي وابدأ رحلتك مع فكرني 🚀",
        
        // Learning Interview
        "intv_title": "جلسة التعارف 🤝",
        "intv_desc": "مرحباً! أنا فكرني. دعني أتعرف على أسلوبك في التعلم والعمل عشان أساعدك بشكل أفضل.",
        "intv_q1_title": "ما أسلوبك في التعلم المفضل؟",
        "intv_q1_desc": "اختر الأقرب لطريقة استيعابك",
        "intv_q1_opt1": "👁️ بصري (صور ورسوم بيانية)",
        "intv_q1_opt2": "👂 سمعي (اشرح وأسمع)",
        "intv_q1_opt3": "📖 قراءة وكتابة",
        "intv_q1_opt4": "✋ حركي (بمارس وأطبق)",
        "intv_q2_title": "ما رتمك المفضل في التعلم؟",
        "intv_q2_desc": "كم من الوقت تحتاج لاستيعاب الأشياء الجديدة",
        "intv_q2_label_fast": "سريع جداً",
        "intv_q2_label_slow": "بطيء جداً",
        "intv_q2_value_mod": "معتدل",
        "intv_q3_title": "ما أهدافك الرئيسية؟",
        "intv_q3_desc": "أخبرني عن أحلامك واهتماماتك",
        "intv_q4_title": "ما الذي يحفزك؟",
        "intv_q4_desc": "كيف أساعدك تظل متحفزاً",
        "intv_q4_opt1": "🏆 الإنجازات والتقدم",
        "intv_q4_opt2": "👥 التنافس والمقارنة مع الآخرين",
        "intv_q4_opt3": "🎯 الحرية والاستقلالية",
        "intv_q4_opt4": "🎓 الإتقان والتخصص",
        "intv_complete_h2": "عاش يا بطل! 🎉",
        "intv_complete_p": "تعرفت عليك دلوقتي وهعدل كل حاجة عشانك. ندخل على لوحة التحكم والنبدأ نشتغل؟",
        "btn_prev": "السابق",
        "btn_next": "التالي",
        "btn_finish": "إنهاء",
        "btn_go_home": "الذهاب للوحة التحكم",
        
        // Dashboard Sidebar
        "nav_main": "الرئيسية",
        "nav_dashboard": "لوحة القيادة",
        "nav_tasks": "إدارة المهام",
        "nav_ai": "الذكاء الاصطناعي",
        "nav_focus": "غرفة التركيز (الكاميرا)",
        "nav_assistant": "المساعد الذكي",
        "nav_settings": "الإعدادات",
        "nav_profile": "الملف الشخصي",
        "btn_language_icon": "English",
        
        // Profile Page
        "prof_task_count": "📊 عدد المهام",
        "prof_completed": "✅ المهام المكتملة",
        "prof_goals": "🎯 عدد الأهداف",
        "prof_interview": "⏳ حالة الإنترفيو",
        "prof_edit_info": "تعديل البيانات الشخصية",
        "prof_name_placeholder": "أدخل اسمك الجديد",
        "prof_email_placeholder": "أدخل بريدك الإلكتروني الجديد",
        "prof_save": "حفظ التعديلات",
        "prof_cancel": "إلغاء",
        "prof_danger_zone": "منطقة الخطر",
        "prof_danger_desc": "تسجيل الخروج من حسابك في فكرني. ستحتاج لتسجيل الدخول مرة أخرى.",
        "prof_logout": "تسجيل خروج",
        
        // Notifications Page
        "notif_title": "الإشعارات",
        "notif_empty": "لا توجد إشعارات",
        "notif_empty_desc": "ستظهر الإشعارات الجديدة هنا عند توفرها",
        "notif_go_back": "العودة للرئيسية",
        
        // Tasks Page
        "tasks_title": "المهام الخاصة بك ✅",
        "tasks_new_btn": "+ مهمة جديدة",
        "tasks_all": "الكل",
        "tasks_pending": "قيد الإنجاز",
        "tasks_completed": "مكتملة",
        "tasks_overdue": "متأخرة",
        
        // Dashboard Inner Widgets
        "dash_greeting": "مرحباً بعودتك!",
        "dash_subtitle": "إليك ملخص سريع لأدائك ومهامك اليوم.",
        "kpi_completed": "المهام المكتملة",
        "kpi_in_progress": "قيد التنفيذ",
        "kpi_focus_hours": "ساعات التركيز",
        "kpi_distraction": "معدل التشتت",
        "kpi_this_week": "هذا الأسبوع",
        "chart_focus_weekly": "أداء التركيز الأسبوعي",
        "chart_goal_tree": "شجرة الأهداف (مسار الزمن)",
        
        // Focus Room
        "focus_title": "غرفة التركيز (مراقبة بالذكاء الاصطناعي)",
        "focus_subtitle": "شغل الكاميرا، ابدأ المهمة، وفكرني هيراقب تركيزك وينبهك لو سرحت.",
        "cam_offline": "الكاميرا متوقفة",
        "cam_offline_desc": "اضغط على الزر لبدء المراقبة الدقيقة",
        "btn_start_cam": "تشغيل غرفة التركيز",
        "btn_stop_cam": "إنهاء الجلسة",
        "focus_current_time": "وقت الجلسة الحالي",
        "focus_analyzing": "جاري تحليل التركيز",
        
        // Chat Assistant
        "chat_title": "المساعد الذكي",
        "chat_subtitle": "اطلب من فكرني إضافة مهام، أو اتكلم معاه بالمايك مباشرة.",
        "chat_bot_name": "فكرني (AI Copilot)",
        "chat_bot_status": "متصل وجاهز للمساعدة",
        "chat_placeholder": "اكتب أمرك هنا... (مثال: اخلص فرونت إند لموقع ويب)",
        
        // Add Task Modal
        "modal_new_task": "إضافة مهمة جديدة",
        "lbl_task_title": "عنوان المهمة *",
        "placeholder_task_title": "مثال: إكمال تقرير المشروع",
        "lbl_task_desc": "الوصف (اختياري)",
        "placeholder_task_desc": "أضف تفاصيل عن المهمة...",
        "lbl_priority": "الأولوية",
        "prior_low": "منخفضة",
        "prior_med": "متوسطة",
        "prior_high": "عالية",
        "prior_vhigh": "عالية جداً",
        "btn_save_task": "حفظ المهمة",
        "btn_cancel": "إلغاء",
        "btn_breakdown": "تقسيم بـ AI",
        "btn_delete": "حذف"
    },
    en: {
        // Shared / Navigation
        "btn_dark_mode": "🌙 Dark Mode",
        "btn_light_mode": "☀️ Light Mode",
        "btn_login": "Login",
        "btn_signup": "Sign Up",
        "btn_language": "🌍 عربي",
        "btn_ok": "Okay",
        
        // Homepage / Landing
        "hero_title": "Fakarni — Your Smart Life Planner 🚀",
        "hero_subtitle": "Unlock the power of your daily habits, divide huge goals into actionable tasks, and monitor your focus stress-free! Fakarni isn't just an app, it's your buddy that cheers you on!",
        "hero_start_btn": "Start the Journey 🔥",
        "hero_account_btn": "I Already Have an Account",
        "features_title": "What Does Fakarni Offer You? ✨",
        "feature1_title": "Clear Goals",
        "feature1_desc": "Organizes your complex ambitions into tiny, clear fragments that you can conquer easily.",
        "feature2_title": "Smart Tailored Plan",
        "feature2_desc": "Analyzes your mindset & learning pace to craft the absolute perfect study schedule for you.",
        "feature3_title": "Focus Camera",
        "feature3_desc": "AI secretly monitors your focus levels while working to ensure you never get distracted.",
        "feature4_title": "Cheering Daily Reports",
        "feature4_desc": "Provides stunning charts displaying your growing progress every single day.",
        "feature5_title": "Chat Assistant",
        "feature5_desc": "Your buddy Fakarni answers your questions and strictly motivates you when you slack off.",
        "feature6_title": "Absolute Privacy",
        "feature6_desc": "All of your data, tasks, and deepest dreams are secured inside a highly encrypted virtual safe.",
        
        // Auth (Login / Signup)
        "auth_welcome_login": "Welcome Back",
        "auth_welcome_signup": "New Account",
        "auth_tab_login": "Login",
        "auth_tab_signup": "Sign Up",
        "lbl_fullname": "Full Name",
        "lbl_email": "Email Address",
        "lbl_password": "Password",
        "lbl_confirm_password": "Confirm Password",
        "btn_submit_login": "Login",
        "btn_submit_signup": "Create Account",
        "lnk_forgot_password": "Forgot your password?",
        "lnk_no_account": "Don't have an account?",
        "lnk_has_account": "Already have an account?",
        "click_here": "Click Here",
        "login_here": "Log in from here",
        "pwd_strength": "Password Strength: ",
        "pwd_weak": "Weak 🔴",
        "pwd_medium": "Medium 🟠",
        "pwd_strong": "Strong 🟢",
        "signup_subtitle": "Register now and start your journey with Fakarni 🚀",
        
        // Learning Interview
        "intv_title": "Getting to Know You 🤝",
        "intv_desc": "Hello! I am Fakarni. Let me understand your learning & working style so I can map out things perfectly for you.",
        "intv_q1_title": "What's your preferred learning style?",
        "intv_q1_desc": "Choose the closest option to how your brain absorbs things",
        "intv_q1_opt1": "👁️ Visual (Images & Graphs)",
        "intv_q1_opt2": "👂 Auditory (Listen & Explain)",
        "intv_q1_opt3": "📖 Reading & Writing",
        "intv_q1_opt4": "✋ Kinesthetic (Practice & Do)",
        "intv_q2_title": "What's your learning pace?",
        "intv_q2_desc": "How much time do you require to grasp an entirely new concept?",
        "intv_q2_label_fast": "Very Fast",
        "intv_q2_label_slow": "Very Slow",
        "intv_q2_value_mod": "Moderate",
        "intv_q3_title": "What are your primary goals?",
        "intv_q3_desc": "Tell me about your aspirations and dreams",
        "intv_q4_title": "What highly motivates you?",
        "intv_q4_desc": "How can I keep your fire burning?",
        "intv_q4_opt1": "🏆 Achievements & Progress",
        "intv_q4_opt2": "👥 Competition & Comparisons",
        "intv_q4_opt3": "🎯 Absolute Freedom & Autonomy",
        "intv_q4_opt4": "🎓 Specialization & Mastery",
        "intv_complete_h2": "Excellent Job, Hero! 🎉",
        "intv_complete_p": "I've memorized everything about you. I'm modifying my algorithms right now. Let's head straight to your Dashboard!",
        "btn_prev": "Previous",
        "btn_next": "Next",
        "btn_finish": "Finish",
        "btn_go_home": "Go to Dashboard",
        
        // Dashboard Sidebar
        "nav_main": "Main",
        "nav_dashboard": "Dashboard",
        "nav_tasks": "Task Management",
        "nav_ai": "Artificial Intelligence",
        "nav_focus": "Focus Room (Camera)",
        "nav_assistant": "Smart Assistant",
        "nav_settings": "Settings",
        "nav_profile": "Profile",
        "btn_language_icon": "عربي",
        
        // Profile Page
        "prof_task_count": "📊 Total Tasks",
        "prof_completed": "✅ Completed Tasks",
        "prof_goals": "🎯 Total Goals",
        "prof_interview": "⏳ Interview Status",
        "prof_edit_info": "Edit Personal Info",
        "prof_name_placeholder": "Enter your new name",
        "prof_email_placeholder": "Enter your new email",
        "prof_save": "Save Changes",
        "prof_cancel": "Cancel",
        "prof_danger_zone": "Danger Zone",
        "prof_danger_desc": "Sign out of your Fakarni account. You will need to log in again.",
        "prof_logout": "Log Out",
        
        // Notifications Page
        "notif_title": "Notifications",
        "notif_empty": "No Notifications",
        "notif_empty_desc": "New notifications will appear here when available",
        "notif_go_back": "Back to Home",
        
        // Tasks Page
        "tasks_title": "Your Tasks ✅",
        "tasks_new_btn": "+ New Task",
        "tasks_all": "All",
        "tasks_pending": "Pending",
        "tasks_completed": "Completed",
        "tasks_overdue": "Overdue",
        
        // Dashboard Inner Widgets
        "dash_greeting": "Welcome back!",
        "dash_subtitle": "Here is a quick summary of your performance and tasks today.",
        "kpi_completed": "Completed Tasks",
        "kpi_in_progress": "In Progress",
        "kpi_focus_hours": "Focus Hours",
        "kpi_distraction": "Distraction Rate",
        "kpi_this_week": "This Week",
        "chart_focus_weekly": "Weekly Focus Performance",
        "chart_goal_tree": "Goals Tree (Timeline)",
        
        // Focus Room
        "focus_title": "Focus Room (AI Monitored)",
        "focus_subtitle": "Turn on your camera, start your task, and Fakarni will monitor your focus.",
        "cam_offline": "Camera Offline",
        "cam_offline_desc": "Click the button below to strictly monitor your focus",
        "btn_start_cam": "Start Focus Room",
        "btn_stop_cam": "End Session",
        "focus_current_time": "Current Session Time",
        "focus_analyzing": "Analyzing Focus...",
        
        // Chat Assistant
        "chat_title": "Smart Assistant",
        "chat_subtitle": "Ask Fakarni to add tasks, or use the mic strictly to command.",
        "chat_bot_name": "Fakarni (AI Copilot)",
        "chat_bot_status": "Online and ready to assist",
        "chat_placeholder": "Type your command here... (e.g. Finish frontend for a website)",
        
        // Add Task Modal
        "modal_new_task": "Add New Task",
        "lbl_task_title": "Task Title *",
        "placeholder_task_title": "e.g. Complete Project Report",
        "lbl_task_desc": "Description (Optional)",
        "placeholder_task_desc": "Add task details...",
        "lbl_priority": "Priority",
        "prior_low": "Low",
        "prior_med": "Medium",
        "prior_high": "High",
        "prior_vhigh": "Very High",
        "btn_save_task": "Save Task",
        "btn_cancel": "Cancel",
        "btn_breakdown": "AI Breakdown",
        "btn_delete": "Delete"
    }
};

// Global Translation Logic
function initTranslations() {
    let currentLang = localStorage.getItem('lang') || 'ar';
    
    // Set Document Direction
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLang;

    // Apply translations to data-i18n attributes
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang] && translations[currentLang][key]) {
            el.innerHTML = translations[currentLang][key];
        }
    });

    // Apply translations to placeholders
    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[currentLang] && translations[currentLang][key]) {
            el.placeholder = translations[currentLang][key];
        }
    });
}

function toggleLanguage() {
    let currentLang = localStorage.getItem('lang') || 'ar';
    let nextLang = currentLang === 'ar' ? 'en' : 'ar';
    localStorage.setItem('lang', nextLang);
    initTranslations();
    
    // Also toggle the Dark Mode text specifically if it's there
    const darkModeBtn = document.getElementById('darkModeToggle');
    if (darkModeBtn) {
        // We evaluate its current state directly based on body class
        if (document.body.classList.contains('dark-mode')) {
            darkModeBtn.innerHTML = translations[nextLang]["btn_light_mode"];
        } else {
            darkModeBtn.innerHTML = translations[nextLang]["btn_dark_mode"];
        }
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', initTranslations);
