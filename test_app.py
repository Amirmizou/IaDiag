#!/usr/bin/env python3
"""
Simple test script for the Medical Diagnosis AI Application
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are properly set"""
    print("Testing environment configuration...")
    
    required_vars = ['HUGGINGFACE_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    else:
        print("✅ Environment variables are properly configured")
        return True

def test_huggingface_api():
    """Test Hugging Face API connection"""
    print("\nTesting Hugging Face API connection...")
    
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ No Hugging Face API key found")
        return False
    
    # Test API with a simple request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Simple test request to check if API key is valid
        response = requests.get(
            "https://api-inference.huggingface.co/models/google/medgemma-2b",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Hugging Face API connection successful")
            return True
        else:
            print(f"❌ Hugging Face API connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Hugging Face API: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be imported and basic functionality works"""
    print("\nTesting Flask application...")
    
    try:
        # Import the app
        from app import app, diagnosis_system
        
        # Test basic functionality
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Flask app starts successfully")
                print("✅ Home page is accessible")
            else:
                print(f"❌ Home page error: {response.status_code}")
                return False
            
            # Test API endpoint
            response = client.get('/api/diagnoses')
            if response.status_code == 200:
                print("✅ API endpoints are accessible")
            else:
                print(f"❌ API endpoint error: {response.status_code}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\nTesting dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'transformers',
        'torch',
        'pillow',
        'python_dotenv',
        'requests',
        'numpy',
        'pandas',
        'reportlab',
        'python_dateutil',
        'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required dependencies are installed")
        return True

def main():
    """Run all tests"""
    print("🧪 Medical Diagnosis AI Application - Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_environment,
        test_huggingface_api,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please fix the issues before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    main() 