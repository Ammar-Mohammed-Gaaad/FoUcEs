/**
 * Fakarni AI - Onboarding & Profile Manager (جلسة التعارف)
 * الملف ده مسؤول عن إدارة "جلسة التعارف" بين المستخدم وفكرني
 * وتظبيط إعدادات البروفايل (الأحلام، طريقة الشغل، والتركيز).
 */

const LearningInterviewManager = {
    
    /**
     * فكرني بيدور على تصريح الدخول (التوكن) في المتصفح
     */
    getAuthToken() {
        // Try localStorage first (متوافق مع التحديثات اللي عملناها)
        let token = localStorage.getItem('token') || localStorage.getItem('access_token');
        if (token) return token;
        
        // Try cookies لو التوكن متسجل كـ كوكي
        const name = 'access_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const cookieArray = decodedCookie.split(';');
        
        for (let cookie of cookieArray) {
            cookie = cookie.trim();
            if (cookie.startsWith(name)) {
                token = cookie.substring(name.length);
                // نحفظه تاني عشان الطوارئ
                localStorage.setItem('access_token', token);
                localStorage.setItem('token', token);
                return token;
            }
        }
        
        return null;
    },
    
    /**
     * بيشيك لو المستخدم قعد مع فكرني قبل كده وحدد أهدافه ولا لأ
     * (بتشتغل أوتوماتيك بعد اللوجين)
     */
    async checkAndRedirectIfNeeded() {
        try {
            const token = this.getAuthToken();
            if (!token) return;

            const response = await fetch('/api/learning/profile-status', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.redirect_to_interview) {
                    // المستخدم لسه معملش جلسة التعارف
                    console.log("فكرني لسه ميعرفكش كويس، يلا بينا على جلسة التعارف! 🤝");
                    window.location.href = '/learning-interview';
                }
            }
        } catch (error) {
            console.warn('فكرني مش قادر يتأكد من حالة البروفايل بتاعك ⚠️:', error);
        }
    },

    /**
     * بيجيب تفاصيل دماغك وأهدافك اللي فكرني مسجلها عنده
     */
    async getLearningProfile() {
        try {
            const token = this.getAuthToken();
            if (!token) throw new Error('فكرني مش لاقي التوكن بتاعك!');

            const response = await fetch('/api/learning/my-profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('السيرفر مرضيش يبعت البروفايل');
            return await response.json();
        } catch (error) {
            console.error('فكرني واجه مشكلة وهو بيجيب بياناتك ❌:', error);
            return null;
        }
    },

    /**
     * بيحلل طريقة استيعابك وشغلك (عشان فكرني يعرف يقسم لك التاسكات صح)
     */
    async getLearningStyles() {
        try {
            const token = this.getAuthToken();
            if (!token) throw new Error('فكرني مش لاقي التوكن بتاعك!');

            const response = await fetch('/api/learning/learning-styles', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('فشل في جلب أسلوب التعلم');
            return await response.json();
        } catch (error) {
            console.error('فكرني مش عارف يحلل دماغك دلوقتي 🧠:', error);
            return null;
        }
    },

    /**
     * فكرني بيسجل التعديلات الجديدة في أحلامك أو طريقة مذاكرتك/شغلك
     */
    async updateLearningProfile(updates) {
        try {
            const token = this.getAuthToken();
            if (!token) throw new Error('فكرني مش لاقي التوكن بتاعك!');

            const response = await fetch('/api/learning/my-profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(updates)
            });

            if (!response.ok) throw new Error('فشل في تحديث البروفايل');
            return await response.json();
        } catch (error) {
            console.error('فكرني مقدرش يحفظ التعديلات الجديدة 💾:', error);
            return null;
        }
    },

    /**
     * تظبيط شكل البيانات عشان فكرني يفهمها ويقسم التاسكات على أساسها
     */
    formatProfile(profile) {
        // درجات الاستيعاب (بصري، سمعي، قراءة، حركي)
        const styles = {
            'Visual': profile.visual_score,
            'Auditory': profile.auditory_score,
            'Reading/Writing': profile.reading_writing_score,
            'Kinesthetic': profile.kinesthetic_score
        };

        // تحديد أعلى درجة عشان فكرني يعرف أسلوبك الغالب
        const dominant = Object.keys(styles).reduce((a, b) => 
            styles[a] > styles[b] ? a : b
        );

        return {
            dominant_style: dominant,
            styles: styles,
            learning_pace: profile.learning_pace, // رتمك سريع ولا بطيء
            preferred_difficulty: profile.preferred_difficulty, // بتحب التاسكات الصعبة ولا السهلة
            interaction_style: profile.interaction_style,
            motivation_type: profile.motivation_type, // إيه اللي بيحفزك
            goal_orientation: profile.goal_orientation, // توجهك ناحية الأحلام والأهداف
            content_preferences: profile.content_preferences,
            game_preferences: profile.game_preferences, // إعدادات التركيز والمكافآت
            chat_preferences: profile.chat_preferences // إعدادات الدردشة مع فكرني
        };
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LearningInterviewManager;
}