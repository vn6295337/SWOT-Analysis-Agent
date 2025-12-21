#!/usr/bin/env python3
"""
Test script to verify API connectivity
"""

import requests
import time
import sys

def test_api():
    print("🧪 Testing API Connection...")
    print("=" * 40)
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8002/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        return False
    
    # Test analysis endpoint
    print("🔍 Testing analysis endpoint...")
    try:
        response = requests.post(
            "http://localhost:8002/api/analyze",
            json={"company_name": "Tesla"},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Analysis endpoint works!")
            data = response.json()
            print(f"📋 Company: {data['company_name']}")
            print(f"📊 Score: {data['score']}/10")
            print(f"📝 Report length: {data['report_length']} characters")
            return True
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Analysis request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 API is working perfectly!")
    else:
        print("\n❌ API is not working. Check the troubleshooting guide.")
    sys.exit(0 if success else 1)