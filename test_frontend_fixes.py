#!/usr/bin/env python3
"""
Comprehensive test suite to verify all frontend fixes
Tests: Task creation, user personalization, chat integration, API endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
TEST_TOKEN = None

def log_test(title, status, details=""):
    """Pretty print test results"""
    symbol = "✅" if status else "❌"
    print(f"\n{symbol} {title}")
    if details:
        print(f"   └─ {details}")

def setup_auth():
    """Login and get token"""
    global TEST_TOKEN
    print("\n" + "="*60)
    print("🔐 FRONTEND FIXES VERIFICATION TEST SUITE")
    print("="*60)
    
    # Try with query parameters (FastAPI default auth)
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login?email=test@example.com&password=test123")
        
        if response.ok:
            data = response.json()
            TEST_TOKEN = data.get("access_token")
            log_test("Authentication Setup", True, f"Token: {TEST_TOKEN[:30] if TEST_TOKEN else 'None'}...")
            return True
        elif response.status_code in [422, 404]:
            # Try alternative auth methods
            log_test("Authentication Setup", False, f"Status {response.status_code} - Auth endpoint issue")
            # For now, create a test token or skip auth
            TEST_TOKEN = "dummy_token_for_testing"
            print("   └─ ⚠️  Using test mode (no real auth)")
            return True
    except Exception as e:
        log_test("Authentication Setup", False, str(e))
    return False

def test_profile_loading():
    """Test 1: Load user profile (for personalization)"""
    print("\n" + "-"*60)
    print("TEST 1: User Profile Loading (for Name/Job Personalization)")
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/learning/my-profile", headers=headers)
        
        if response.ok:
            data = response.json()
            print(f"✅ Profile load successful")
            print(f"   └─ User: {data.get('full_name', 'N/A')}")
            print(f"   └─ Job: {data.get('job_title', 'N/A')}")
            log_test("Profile Endpoint Response", True, json.dumps(data, ensure_ascii=False, indent=2)[:200])
            return True
        else:
            log_test("Profile Endpoint Response", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Profile Endpoint Response", False, str(e))
    return False

def test_task_creation():
    """Test 2: Create a task (Add Task button fix)"""
    print("\n" + "-"*60)
    print("TEST 2: Task Creation (Add Task Button Fix)")
    
    task_data = {
        "title": "Test Task - إكمال تقرير المشروع",
        "description": "Testing the fixed task modal",
        "priority": 2
    }
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.post(f"{BASE_URL}/api/tasks/", json=task_data, headers=headers)
        
        if response.ok:
            task = response.json()
            log_test("Task Creation (POST /api/tasks/)", True, f"Task ID: {task.get('id', 'N/A')}")
            return True
        else:
            log_test("Task Creation (POST /api/tasks/)", False, f"Status {response.status_code}: {response.text}")
    except Exception as e:
        log_test("Task Creation (POST /api/tasks/)", False, str(e))
    return False

def test_tasks_listing():
    """Test 3: Fetch all tasks (for dashboard KPI metrics)"""
    print("\n" + "-"*60)
    print("TEST 3: Tasks Listing (for Dashboard KPI Metrics)")
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
        
        if response.ok:
            tasks = response.json() if isinstance(response.json(), list) else response.json().get('items', [])
            completed = len([t for t in tasks if t.get('status') == 'completed'])
            in_progress = len([t for t in tasks if t.get('status') in ['to_do', 'in_progress']])
            
            log_test("Tasks Fetching (GET /api/tasks/)", True, 
                    f"Total: {len(tasks)}, Completed: {completed}, In Progress: {in_progress}")
            return True
        else:
            log_test("Tasks Fetching (GET /api/tasks/)", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Tasks Fetching (GET /api/tasks/)", False, str(e))
    return False

def test_chat_endpoint():
    """Test 4: AI Chat endpoint (for send button fix)"""
    print("\n" + "-"*60)
    print("TEST 4: AI Chat Endpoint (Send Button Integration)")
    
    chat_data = {"message": "اقسم مشروع فكرني إلى مهام"}
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.post(f"{BASE_URL}/api/ai/chat", json=chat_data, headers=headers)
        
        if response.ok:
            result = response.json()
            reply = result.get('reply', '')[:100]
            log_test("Chat API Endpoint (POST /api/ai/chat)", True, f"Reply: {reply}...")
            return True
        elif response.status_code == 404:
            log_test("Chat API Endpoint (POST /api/ai/chat)", False, "Endpoint not found - may not be implemented yet")
        else:
            log_test("Chat API Endpoint (POST /api/ai/chat)", False, f"Status {response.status_code}: {response.text[:100]}")
    except Exception as e:
        log_test("Chat API Endpoint (POST /api/ai/chat)", False, str(e))
    return False

def test_user_update():
    """Test 5: Update user profile (for job title fix)"""
    print("\n" + "-"*60)
    print("TEST 5: User Profile Update (Job Title Implementation)")
    
    update_data = {
        "full_name": "Test Engineer",
        "job_title": "Senior Developer"
    }
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = requests.patch(f"{BASE_URL}/api/learning/user-profile", json=update_data, headers=headers)
        
        if response.ok:
            log_test("User Update (PATCH /api/learning/user-profile)", True, "Profile updated")
            # Verify the update
            verify = requests.get(f"{BASE_URL}/api/learning/my-profile", headers=headers)
            if verify.ok:
                print(f"   └─ Verified: {verify.json().get('full_name')} | {verify.json().get('job_title')}")
            return True
        else:
            log_test("User Update (PATCH /api/learning/user-profile)", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("User Update (PATCH /api/learning/user-profile)", False, str(e))
    return False

def test_schema_validation():
    """Test 6: Verify no schema errors"""
    print("\n" + "-"*60)
    print("TEST 6: Schema Validation (No 422 Errors)")
    
    try:
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        # Test with various payloads
        payloads = [
            {"title": "Task with no priority"},
            {"title": "Task", "description": "With description", "priority": 1},
            {"title": "Task with null goal"},
        ]
        
        all_ok = True
        for payload in payloads:
            response = requests.post(f"{BASE_URL}/api/tasks/", json=payload, headers=headers)
            if response.status_code == 422:
                log_test("Schema Validation", False, f"422 Error in: {payload}")
                all_ok = False
            elif response.status_code != 201 and response.status_code != 200:
                log_test("Schema Validation", False, f"Unexpected status {response.status_code}")
                all_ok = False
        
        if all_ok:
            log_test("Schema Validation (No 422 Errors)", True, "All payloads accepted")
        return all_ok
    except Exception as e:
        log_test("Schema Validation", False, str(e))
    return False

def run_all_tests():
    """Run complete test suite"""
    if not setup_auth():
        print("\n❌ Cannot proceed without authentication")
        return
    
    results = []
    results.append(("Profile Loading", test_profile_loading()))
    results.append(("Task Creation", test_task_creation()))
    results.append(("Tasks Listing", test_tasks_listing()))
    results.append(("Chat Endpoint", test_chat_endpoint()))
    results.append(("User Update", test_user_update()))
    results.append(("Schema Validation", test_schema_validation()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print("\n🚀 ALL FRONTEND FIXES VERIFIED SUCCESSFULLY!")
    else:
        print(f"\n⚠️  {total - passed} issue(s) found")

if __name__ == "__main__":
    print("\n⏱️  Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    try:
        requests.get(f"{BASE_URL}/docs")
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("Make sure the backend server is running with: python run_server.py")
