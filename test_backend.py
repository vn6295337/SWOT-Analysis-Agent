#!/usr/bin/env python3
"""
Simple test to verify the backend is working
"""

import os
import sys
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append('.')

# Set environment variables (simulate Space environment)
os.environ['GROQ_API_KEY'] = 'your_groq_key'  # Will be overridden by Space secrets
os.environ['TAVILY_API_KEY'] = 'your_tavily_key'  # Will be overridden by Space secrets
os.environ['LANGCHAIN_API_KEY'] = 'your_langchain_key'  # Will be overridden by Space secrets

try:
    from api_real import app
    
    print("✅ Successfully imported FastAPI app")
    
    # Create test client
    client = TestClient(app)
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    response = client.get("/api/health")
    
    if response.status_code == 200:
        print("✅ Health check passed:", response.json())
    else:
        print("❌ Health check failed:", response.status_code, response.text)
    
    # Test analysis endpoint
    print("🔍 Testing analysis endpoint...")
    response = client.post("/api/analyze", json={"company_name": "Tesla"})
    
    if response.status_code == 200:
        print("✅ Analysis endpoint works:", response.json())
    else:
        print("❌ Analysis endpoint failed:", response.status_code, response.text)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This usually means a missing Python package.")
    print("Check that all requirements are installed:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()