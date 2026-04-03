#!/usr/bin/env python3
"""
Button Integration Verification Script
Tests all button fixes applied during Phase 2 audit
"""

import re
import os
from pathlib import Path

def read_file(path):
    """Read file content"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return None

def check_action_registry(content, page_name, expected_actions):
    """Check if action registry is properly defined"""
    print(f"\n{'='*60}")
    print(f"🔍 Checking {page_name} Action Registry")
    print(f"{'='*60}")
    
    # Look for action registry pattern
    registry_pattern = rf"const \w+Actions\s*=\s*\{{([^}}]+)\}}"
    match = re.search(registry_pattern, content, re.DOTALL)
    
    if not match:
        print(f"❌ NO ACTION REGISTRY FOUND in {page_name}")
        return False
    
    registry_content = match.group(1)
    print(f"✅ Found action registry")
    
    # Check for each expected action
    all_found = True
    for action in expected_actions:
        if action in registry_content:
            print(f"   ✅ Action '{action}' registered")
        else:
            print(f"   ❌ Action '{action}' NOT found")
            all_found = False
    
    return all_found

def check_data_actions(content, page_name, expected_actions):
    """Check if buttons have data-action attributes"""
    print(f"\n🔍 Checking {page_name} data-action attributes")
    print(f"{'-'*60}")
    
    all_found = True
    for action in expected_actions:
        pattern = rf'data-action\s*=\s*["\']?{action}["\']?'
        if re.search(pattern, content):
            print(f"   ✅ Button with data-action='{action}' found")
        else:
            print(f"   ❌ Button with data-action='{action}' NOT found")
            all_found = False
    
    return all_found

def check_button_manager_init(content, page_name):
    """Check if ButtonManager is initialized"""
    print(f"\n🔍 Checking {page_name} ButtonManager initialization")
    print(f"{'-'*60}")
    
    if 'new ButtonManager' in content:
        print(f"   ✅ ButtonManager initialized")
        return True
    else:
        print(f"   ❌ ButtonManager NOT initialized")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 BUTTON INTEGRATION VERIFICATION SUITE")
    print("="*60)
    
    base_path = Path("a:\\FoUcs\\FoUcEs\\front\\html")
    results = {}
    
    # ===== TEST 1: tasks.html =====
    print("\n\n📄 TEST 1: tasks.html (10 buttons)")
    print("="*60)
    tasks_file = base_path / "tasks.html"
    tasks_content = read_file(tasks_file)
    
    if tasks_content:
        expected_task_actions = [
            'openTaskModal',
            'saveTask', 
            'filterTasks',
            'completeTask',
            'deleteTask'
        ]
        
        results['tasks.html'] = {
            'registry': check_action_registry(tasks_content, 'tasks.html', expected_task_actions),
            'data_actions': check_data_actions(tasks_content, 'tasks.html', expected_task_actions),
            'button_manager': check_button_manager_init(tasks_content, 'tasks.html')
        }
    
    # ===== TEST 2: learning-interview.html =====
    print("\n\n📄 TEST 2: learning-interview.html (3 buttons)")
    print("="*60)
    interview_file = base_path / "learning-interview.html"
    interview_content = read_file(interview_file)
    
    if interview_content:
        expected_interview_actions = [
            'previousQuestion',
            'nextQuestion',
            'redirectHome'
        ]
        
        results['learning-interview.html'] = {
            'registry': check_action_registry(interview_content, 'learning-interview.html', expected_interview_actions),
            'data_actions': check_data_actions(interview_content, 'learning-interview.html', expected_interview_actions),
            'button_manager': check_button_manager_init(interview_content, 'learning-interview.html')
        }
    
    # ===== TEST 3: home.html =====
    print("\n\n📄 TEST 3: home.html (AI button + task modal buttons)")
    print("="*60)
    home_file = base_path / "home.html"
    home_content = read_file(home_file)
    
    if home_content:
        expected_home_actions = [
            'aiBreakdown',
            'closeTaskModal',
            'saveTask'
        ]
        
        results['home.html'] = {
            'registry': check_action_registry(home_content, 'home.html', expected_home_actions),
            'data_actions': check_data_actions(home_content, 'home.html', expected_home_actions),
            'button_manager': check_button_manager_init(home_content, 'home.html')
        }
        
        # Special check for AI button data-action
        print(f"\n🔍 Special Check: AI Button data-action attribute")
        print(f"{'-'*60}")
        if 'ai-breakdown-btn' in home_content and 'data-action="aiBreakdown"' in home_content:
            print(f"   ✅ AI button has proper data-action attribute")
            results['home.html']['ai_button'] = True
        else:
            print(f"   ❌ AI button missing data-action attribute")
            results['home.html']['ai_button'] = False
    
    # ===== FINAL SUMMARY =====
    print("\n\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for page, tests in results.items():
        print(f"\n📄 {page}:")
        for test_name, passed in tests.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {test_name}")
            if not passed:
                all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Button integration fixes are complete!")
        print("="*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        print("="*60)
        return 1

if __name__ == "__main__":
    exit(main())
