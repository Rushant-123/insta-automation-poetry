#!/usr/bin/env python3
"""
Test script for Poetry Video Generator API
Run this to test basic functionality before deployment.
"""

import requests
import json
import time
import sys
from typing import Dict, Any


def test_health_endpoint(base_url: str) -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_themes_endpoint(base_url: str) -> bool:
    """Test the themes endpoint."""
    try:
        response = requests.get(f"{base_url}/themes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            themes = data.get('themes', [])
            print(f"✅ Themes endpoint works: {len(themes)} themes available")
            for theme in themes[:3]:  # Show first 3 themes
                print(f"   - {theme['name']}: {theme['description']}")
            return True
        else:
            print(f"❌ Themes endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Themes endpoint error: {e}")
        return False


def test_random_poetry_endpoint(base_url: str) -> bool:
    """Test the random poetry endpoint."""
    try:
        response = requests.get(f"{base_url}/poetry/random", timeout=10)
        if response.status_code == 200:
            data = response.json()
            lines = data.get('lines', [])
            print(f"✅ Random poetry works: {len(lines)} lines")
            print(f"   Sample: {lines[0] if lines else 'No lines'}")
            return True
        else:
            print(f"❌ Random poetry failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Random poetry error: {e}")
        return False


def test_video_generation(base_url: str, test_mode: bool = True) -> bool:
    """Test video generation endpoint."""
    try:
        # Test payload
        payload = {
            "theme": "nature",
            "custom_poetry": "This is a test poem\nfor video generation\nwith beautiful themes\nand peaceful music"
        }
        
        if test_mode:
            print("🧪 Testing video generation (this may take a while)...")
        
        response = requests.post(
            f"{base_url}/generate-video",
            json=payload,
            timeout=300  # 5 minutes timeout for video generation
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Video generation successful!")
                print(f"   Video ID: {data.get('video_id')}")
                print(f"   Video URL: {data.get('video_url')}")
                print(f"   Theme: {data.get('theme')}")
                print(f"   Duration: {data.get('duration')} seconds")
                return True
            else:
                print(f"❌ Video generation failed: {data.get('error_message')}")
                return False
        else:
            print(f"❌ Video generation request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Video generation timed out (this might be normal for first run)")
        return False
    except Exception as e:
        print(f"❌ Video generation error: {e}")
        return False


def run_tests(base_url: str = "http://localhost:8000", include_video_test: bool = False):
    """Run all API tests."""
    print("🚀 Testing Poetry Video Generator API")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)
    
    results = []
    
    # Test health endpoint
    print("1. Testing Health Endpoint...")
    results.append(test_health_endpoint(base_url))
    print()
    
    # Test themes endpoint
    print("2. Testing Themes Endpoint...")
    results.append(test_themes_endpoint(base_url))
    print()
    
    # Test random poetry endpoint
    print("3. Testing Random Poetry Endpoint...")
    results.append(test_random_poetry_endpoint(base_url))
    print()
    
    # Test video generation (optional, as it requires S3 setup)
    if include_video_test:
        print("4. Testing Video Generation...")
        print("⚠️  This requires proper S3 configuration!")
        results.append(test_video_generation(base_url))
        print()
    else:
        print("4. Skipping Video Generation Test")
        print("   Run with --include-video-test to test video generation")
        print()
    
    # Summary
    print("-" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        if not include_video_test:
            print("💡 To test video generation, ensure S3 is configured and run:")
            print(f"   python test_api.py --include-video-test")
    else:
        print(f"⚠️  Some tests failed: {passed}/{total} passed")
        print("📚 Check the README.md for setup instructions")
    
    return passed == total


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Poetry Video Generator API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--include-video-test",
        action="store_true",
        help="Include video generation test (requires S3 setup)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    success = run_tests(args.url, args.include_video_test)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 