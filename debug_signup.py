#!/usr/bin/env python3
"""
Debug script for signup issue
"""

import requests
import json

def test_signup_debug():
    url = "http://127.0.0.1:8000/api/auth/signup"
    data = {
        "email": "debug@example.com",
        "full_name": "Debug User",
        "password": "Debug123!"
    }

    print(f"Testing signup with URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 500:
            print("Internal Server Error - checking response content...")
            print(f"Response Text: {response.text}")
        else:
            print(f"Response JSON: {response.json()}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_signup_debug()