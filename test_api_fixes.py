#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all critical fixes for backend/frontend integration
"""

import requests
import json
import sys
from typing import Dict, Any, Tuple

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS_JSON = {"Content-Type": "application/json"}

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.user_email = None
        self.passed = 0
        self.failed = 0
        
    def log_test(self, name: str, status: str, message: str = ""):
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {name}")
        if message:
            print(f"   └─ {message}")
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
    
    def test_1_health_check(self):
        """Test 1: Backend Health Check"""
        print("\n" + "="*60)
        print("TEST 1: Health Check")
        print("="*60)
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=3)
            if resp.status_code == 200 and resp.json().get("status") == "healthy":
                self.log_test("Health Check", "PASS", f"Status: {resp.json()}")
            else:
                self.log_test("Health Check", "FAIL", f"Unexpected status: {resp.status_code}")
        except Exception as e:
            self.log_test("Health Check", "FAIL", str(e))
    
    def test_2_signup(self):
        """Test 2: User Signup with Proper Schema"""
        print("\n" + "="*60)
        print("TEST 2: User Signup")
        print("="*60)
        try:
            payload = {
                "email": "testuser@example.com",
                "full_name": "Test User",
                "password": "Test@12345"
            }
            resp = requests.post(f"{BASE_URL}/auth/signup", json=payload, headers=HEADERS_JSON, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.user_email = data.get("email")
                self.log_test("User Signup", "PASS", f"User ID: {self.user_id}, Email: {self.user_email}")
            else:
                self.log_test("User Signup", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
        except Exception as e:
            self.log_test("User Signup", "FAIL", str(e))
    
    def test_3_profile_endpoint(self):
        """Test 3: GET Learning Profile (with goals field handling)"""
        print("\n" + "="*60)
        print("TEST 3: Get Learning Profile")
        print("="*60)
        if not self.token:
            print("⏭️  Skipping (no token from signup)")
            return
        
        try:
            headers = {**HEADERS_JSON, "Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{BASE_URL}/learning/my-profile", headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                goals_value = data.get("goals")
                
                # Check that goals is never None
                if goals_value is None:
                    self.log_test("Goals Field Handling", "FAIL", "goals field is None (should be empty string or value)")
                else:
                    self.log_test("Goals Field Handling", "PASS", f"goals = '{goals_value}' (type: {type(goals_value).__name__})")
                
                self.log_test("Get Profile Response", "PASS", f"Status: {resp.status_code}, Fields: {list(data.keys())}")
            else:
                self.log_test("Get Profile Response", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
        except Exception as e:
            self.log_test("Get Profile Response", "FAIL", str(e))
    
    def test_4_update_user_profile(self):
        """Test 4: PATCH User Profile (name/email)"""
        print("\n" + "="*60)
        print("TEST 4: Update User Profile (PATCH)")
        print("="*60)
        if not self.token:
            print("⏭️  Skipping (no token)")
            return
        
        try:
            payload = {
                "full_name": "Updated Test User",
                "email": "updated@example.com"
            }
            headers = {**HEADERS_JSON, "Authorization": f"Bearer {self.token}"}
            resp = requests.patch(f"{BASE_URL}/learning/user-profile", json=payload, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                self.log_test("PATCH User Profile", "PASS", f"Status: {resp.status_code}, Response keys: {list(data.keys())}")
            else:
                error_detail = resp.json().get("detail", "Unknown error") if resp.text else "No response"
                self.log_test("PATCH User Profile", "FAIL", f"Status: {resp.status_code}, Error: {error_detail}")
        except Exception as e:
            self.log_test("PATCH User Profile", "FAIL", str(e))
    
    def test_5_partial_profile_update(self):
        """Test 5: PATCH Learning Profile (partial update)"""
        print("\n" + "="*60)
        print("TEST 5: Partial Learning Profile Update")
        print("="*60)
        if not self.token:
            print("⏭️  Skipping (no token)")
            return
        
        try:
            payload = {
                "goals": "Learn Python and AI",
                "learning_style": "visual"
            }
            headers = {**HEADERS_JSON, "Authorization": f"Bearer {self.token}"}
            resp = requests.patch(f"{BASE_URL}/learning/my-profile", json=payload, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                goals = data.get("goals")
                self.log_test("Partial Update", "PASS", f"Status: {resp.status_code}, Goals: '{goals}'")
            else:
                error = resp.json().get("detail", "Unknown") if resp.text else "No response"
                self.log_test("Partial Update", "FAIL", f"Status: {resp.status_code}, Error: {error}")
        except Exception as e:
            self.log_test("Partial Update", "FAIL", str(e))
    
    def test_6_create_task(self):
        """Test 6: Create Task with Proper Schema"""
        print("\n" + "="*60)
        print("TEST 6: Create Task")
        print("="*60)
        if not self.token:
            print("⏭️  Skipping (no token)")
            return
        
        try:
            payload = {
                "title": "Test Task",
                "description": "This is a test task",
                "priority": 3
            }
            headers = {**HEADERS_JSON, "Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{BASE_URL}/tasks/", json=payload, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                self.log_test("Create Task", "PASS", f"Task ID: {data.get('id')}, Title: {data.get('title')}")
            else:
                error = resp.json().get("detail", "Unknown") if resp.text else "Unknown error"
                self.log_test("Create Task", "FAIL", f"Status: {resp.status_code}, Error: {error}")
        except Exception as e:
            self.log_test("Create Task", "FAIL", str(e))
    
    def test_7_list_tasks(self):
        """Test 7: List User Tasks"""
        print("\n" + "="*60)
        print("TEST 7: List Tasks")
        print("="*60)
        if not self.token:
            print("⏭️  Skipping (no token)")
            return
        
        try:
            headers = {**HEADERS_JSON, "Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{BASE_URL}/tasks/", headers=headers, timeout=5)
            
            if resp.status_code == 200:
                tasks = resp.json()
                self.log_test("List Tasks", "PASS", f"Found {len(tasks)} task(s)")
                for task in tasks:
                    print(f"   └─ Task {task.get('id')}: {task.get('title')}")
            else:
                self.log_test("List Tasks", "FAIL", f"Status: {resp.status_code}")
        except Exception as e:
            self.log_test("List Tasks", "FAIL", str(e))
    
    def test_8_auth_header_validation(self):
        """Test 8: Authorization Header Validation"""
        print("\n" + "="*60)
        print("TEST 8: Authorization Header Validation")
        print("="*60)
        
        # Test without token
        try:
            resp = requests.get(f"{BASE_URL}/learning/my-profile", headers=HEADERS_JSON, timeout=5)
            if resp.status_code == 401:
                self.log_test("No Token -> 401", "PASS", "Correctly rejected request without token")
            else:
                self.log_test("No Token -> 401", "FAIL", f"Expected 401, got {resp.status_code}")
        except Exception as e:
            self.log_test("No Token -> 401", "FAIL", str(e))
        
        # Test with invalid token
        try:
            bad_headers = {**HEADERS_JSON, "Authorization": "Bearer invalid_token_xyz"}
            resp = requests.get(f"{BASE_URL}/learning/my-profile", headers=bad_headers, timeout=5)
            if resp.status_code == 401:
                self.log_test("Invalid Token -> 401", "PASS", "Correctly rejected invalid token")
            else:
                self.log_test("Invalid Token -> 401", "FAIL", f"Expected 401, got {resp.status_code}")
        except Exception as e:
            self.log_test("Invalid Token -> 401", "FAIL", str(e))
    
    def test_9_cors_headers(self):
        """Test 9: CORS Headers"""
        print("\n" + "="*60)
        print("TEST 9: CORS Headers")
        print("="*60)
        
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            headers = resp.headers
            
            cors_origin = headers.get("access-control-allow-origin", "NOT SET")
            cors_methods = headers.get("access-control-allow-methods", "NOT SET")
            
            if cors_origin == "*":
                self.log_test("CORS Origin", "PASS", f"Allow-Origin: {cors_origin}")
            else:
                self.log_test("CORS Origin", "FAIL", f"Expected '*', got: {cors_origin}")
        except Exception as e:
            self.log_test("CORS Headers", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n🚀 STARTING COMPREHENSIVE API TEST SUITE")
        print("=" * 60)
        
        self.test_1_health_check()
        self.test_2_signup()
        self.test_3_profile_endpoint()
        self.test_4_update_user_profile()
        self.test_5_partial_profile_update()
        self.test_6_create_task()
        self.test_7_list_tasks()
        self.test_8_auth_header_validation()
        self.test_9_cors_headers()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total: {self.passed + self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if self.passed + self.failed > 0 else "")
        print("=" * 60 + "\n")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
