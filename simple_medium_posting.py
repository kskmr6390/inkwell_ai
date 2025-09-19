#!/usr/bin/env python
import os
import subprocess

def simple_medium_posting():
    """Simple Medium posting that opens Medium in existing Chrome"""
    
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
    
    # Convert markdown to Medium format
    def convert_markdown_to_medium_format(markdown_content: str) -> str:
        """Convert markdown to Medium-compatible format"""
        import re
        
        # Convert markdown headers to plain text (Medium has its own header system)
        content = re.sub(r'^### (.*)$', r'\1', markdown_content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*)$', r'\1', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.*)$', r'\1', content, flags=re.MULTILINE)
        
        # Convert markdown bold to plain text (Medium has its own formatting)
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        
        # Convert markdown italic to plain text
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        
        # Convert code blocks to plain text (Medium has its own code formatting)
        content = re.sub(r'```.*?\n(.*?)```', r'\1', content, flags=re.DOTALL)
        content = re.sub(r'`(.*?)`', r'\1', content)
        
        # Convert markdown links to plain text
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Convert markdown lists to plain text
        content = re.sub(r'^\s*[-*+]\s+', r'• ', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s+', r'• ', content, flags=re.MULTILINE)
        
        # Remove any remaining markdown syntax
        content = re.sub(r'\[TABLE:.*?\]', '', content)
        content = re.sub(r'\[QUOTE:.*?\]', '', content)
        
        return content.strip()
    
    medium_content = convert_markdown_to_medium_format(content)
    
    print("\n🚀 Opening Medium in your Chrome browser...")
    
    try:
        # Open Medium in existing Chrome
        subprocess.run(["open", "-a", "Google Chrome", "https://medium.com/new-story"])
        
        print("\n✅ Medium opened in Chrome! Please complete the following steps:")
        print(f"📝 Title to copy: {title}")
        print(f"📄 Content length: {len(medium_content)} characters")
        print("\n💡 The content has been formatted for Medium. Copy it from below:")
        print("\n" + "="*50)
        print("MEDIUM CONTENT:")
        print("="*50)
        print(medium_content)
        print("="*50)
        
        # Wait for user to complete the process
        input("\n⏸️  Press Enter when you have published the article...")
        
        # Get the published URL
        published_url = input("🔗 Please enter the published URL: ").strip()
        
        if published_url:
            print(f"✅ Article published successfully!")
            print(f"🔗 Published URL: {published_url}")
            
            # Save the result
            with open("medium_post_result.md", "w", encoding="utf-8") as f:
                f.write(f"Publication Status: Success\n")
                f.write(f"Medium post URL: {published_url}\n")
                f.write(f"Title: {title}\n")
                f.write(f"Confirmation: Article published successfully to Medium.\n")
            
            print("📁 Result saved to medium_post_result.md")
        else:
            print("❌ No URL provided. Please try again.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_medium_posting() 