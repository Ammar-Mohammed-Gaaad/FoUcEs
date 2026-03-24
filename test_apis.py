#!/usr/bin/env python3
"""
اختبار شامل لجميع APIs المطلوبة
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """اختبار نقطة الصحة"""
    print("🔍 اختبار /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ /health يعمل بشكل صحيح")
            return True
        else:
            print(f"❌ /health فشل: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ في /health: {e}")
        return False

def test_signup():
    """اختبار التسجيل"""
    print("\n🔍 اختبار التسجيل...")
    data = {
        "email": "test@example.com",
        "full_name": "مستخدم اختبار",
        "password": "TestPass123!"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ التسجيل نجح")
            print(f"   Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"❌ التسجيل فشل: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ خطأ في التسجيل: {e}")
        return None

def test_login():
    """اختبار تسجيل الدخول"""
    print("\n🔍 اختبار تسجيل الدخول...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login?email=test@example.com&password=TestPass123!")
        if response.status_code == 200:
            result = response.json()
            print("✅ تسجيل الدخول نجح")
            print(f"   Token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"❌ تسجيل الدخول فشل: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ خطأ في تسجيل الدخول: {e}")
        return None

def test_save_learning_style(token):
    """اختبار حفظ أسلوب التعلم"""
    print("\n🔍 اختبار حفظ أسلوب التعلم...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/api/learning/save-style",
                               params={"learning_style": "visual"},
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ حفظ أسلوب التعلم نجح")
            print(f"   أسلوب: {result['learning_style']}")
            return True
        else:
            print(f"❌ حفظ أسلوب التعلم فشل: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطأ في حفظ أسلوب التعلم: {e}")
        return False

def test_get_tasks(token):
    """اختبار جلب المهام"""
    print("\n🔍 اختبار جلب المهام...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ جلب المهام نجح - عدد المهام: {len(tasks)}")
            return True
        else:
            print(f"❌ جلب المهام فشل: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطأ في جلب المهام: {e}")
        return False

def test_create_task(token):
    """اختبار إنشاء مهمة"""
    print("\n🔍 اختبار إنشاء مهمة...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "مهمة تجريبية",
        "description": "هذه مهمة للاختبار",
        "priority": 3
    }
    try:
        response = requests.post(f"{BASE_URL}/api/tasks/", json=data, headers=headers)
        if response.status_code == 200:
            task = response.json()
            print("✅ إنشاء المهمة نجح")
            print(f"   عنوان: {task['title']}")
            return task['id']
        else:
            print(f"❌ إنشاء المهمة فشل: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ خطأ في إنشاء المهمة: {e}")
        return None

def main():
    print("🚀 بدء اختبار جميع APIs المطلوبة")
    print("=" * 50)

    # اختبار الصحة
    if not test_health():
        print("\n❌ الخادم غير متاح. تأكد من تشغيل الخادم أولاً.")
        return

    # اختبار التسجيل
    signup_token = test_signup()
    if not signup_token:
        print("\n❌ فشل في التسجيل")
        return

    # اختبار تسجيل الدخول
    login_token = test_login()
    if not login_token:
        print("\n❌ فشل في تسجيل الدخول")
        return

    # استخدام token من تسجيل الدخول
    token = login_token

    # اختبار حفظ أسلوب التعلم
    if not test_save_learning_style(token):
        print("\n❌ فشل في حفظ أسلوب التعلم")
        return

    # اختبار جلب المهام
    if not test_get_tasks(token):
        print("\n❌ فشل في جلب المهام")
        return

    # اختبار إنشاء مهمة
    task_id = test_create_task(token)
    if not task_id:
        print("\n❌ فشل في إنشاء المهمة")
        return

    print("\n" + "=" * 50)
    print("🎉 جميع الاختبارات نجحت!")
    print("✅ قاعدة البيانات تعمل")
    print("✅ APIs التسجيل والدخول تعمل")
    print("✅ API حفظ أسلوب التعلم يعمل")
    print("✅ APIs المهام تعمل")
    print("\n📝 الآن يمكنك ربط الفرونت إند بالباك إند!")

if __name__ == "__main__":
    main()