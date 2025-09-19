#!/usr/bin/env python
import os
import asyncio
from src.tools.blog_platform.medium import MediumPostTool

def test_medium_posting():
    """Test the Medium posting tool with an existing blog post"""
    
    # Check if blog_post.md exists
    if not os.path.exists("blog_post.md"):
        print("❌ blog_post.md not found!")
        return
    
    # Read the blog post content
    with open("blog_post.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract title from the first line (assuming it starts with #)
    lines = content.split('\n')
    title = "AI and Machine Learning Trends 2024"  # Default title
    
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    print(f"📝 Title: {title}")
    print(f"📄 Content length: {len(content)} characters")
    
    # Check environment variables
    if not os.getenv("GOOGLE_EMAIL") or not os.getenv("GOOGLE_PASSWORD"):
        print("❌ GOOGLE_EMAIL and GOOGLE_PASSWORD must be set in .env file")
        return
    
    print("✅ Environment variables found")
    
    # Create and run the Medium posting tool
    medium_tool = MediumPostTool()
    
    print("🚀 Starting Medium publishing...")
    result = medium_tool._run(title, content)
    
    print("\n" + "="*50)
    print("MEDIUM POSTING RESULT:")
    print("="*50)
    print(result)

if __name__ == "__main__":
    test_medium_posting() 