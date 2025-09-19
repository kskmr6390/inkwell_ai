#!/usr/bin/env python3
"""
Test script for Twitter API integration
"""

import os
from dotenv import load_dotenv
from src.tools.blog_platform.twitter import TwitterPostTool

def test_twitter_integration():
    """Test the Twitter API integration"""
    load_dotenv()
    
    # Check if Twitter credentials are available
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET", 
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing Twitter credentials: {missing_vars}")
        print("Please add them to your .env file")
        return False
    
    print("✅ All Twitter credentials found")
    
    # Test the Twitter tool
    twitter_tool = TwitterPostTool()
    
    # Test with a sample tweet
    test_content = "🚀 Testing Twitter API integration for InkwellAI blog promotion tool!"
    test_devto_url = "https://dev.to/test/article"
    
    print(f"\n🐦 Testing tweet posting...")
    print(f"Content: {test_content}")
    print(f"Dev.to URL: {test_devto_url}")
    
    try:
        result = twitter_tool._run(content=test_content, devto_url=test_devto_url)
        print(f"\n✅ Test result: {result}")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Twitter API Integration")
    print("=" * 50)
    
    success = test_twitter_integration()
    
    if success:
        print("\n🎉 Twitter integration test passed!")
        print("Your crew is ready to post tweets after Dev.to publications!")
    else:
        print("\n⚠️ Twitter integration test failed!")
        print("Please check your credentials and try again.") 