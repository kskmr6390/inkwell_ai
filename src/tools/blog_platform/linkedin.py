import os
import requests
from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import re
from src.utils import url_exists, get_newsletter_status, safe_replace_links

class LinkedInPostToolInput(BaseModel):
    title: str = Field(..., description="Title of the blog post.")
    summary: str = Field(..., description="Summary or main points of the blog post.")
    link: str = Field(..., description="URL to the full blog post (e.g., Dev.to link).")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="List of hashtags to include.")

class LinkedInPostTool(BaseTool):
    name: str = "LinkedInPostTool"
    description: str = "Posts an engaging update to LinkedIn with a blog link. (Live API integration)"
    args_schema: Type[BaseModel] = LinkedInPostToolInput

    def _run(self, title: str, summary: str, link: str, hashtags: Optional[List[str]] = None) -> str:
        # Safe check for the blog link
        if not url_exists(link):
            link = "#"
        
        hashtags_str = ' '.join(f"#{tag}" for tag in (hashtags or []))
        post = (
            f"🚀 {title}\n\n"
            f"{summary}\n\n"
            f"🔗 Read the full blog here: {link}\n\n"
            f"💬 I'd love to hear your thoughts—what excites or concerns you most about this topic?\n\n"
            f"{hashtags_str}"
        )
        
        # Safe check for newsletter mentions
        post = re.sub(r'\[Newsletter:.*?\]\([^)]+\)', get_newsletter_status(), post)
        
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        author_urn = os.getenv("LINKEDIN_AUTHOR_URN")
        if not access_token or not author_urn:
            return "Error: LINKEDIN_ACCESS_TOKEN and/or LINKEDIN_AUTHOR_URN environment variables are not set."
        try:
            response = publish_linkedin_post(access_token, author_urn, post)
            return f"LinkedIn post published successfully. Post URN: {response.get('id', 'unknown')}"
        except Exception as e:
            return f"Error publishing to LinkedIn: {e}\n(Stub) LinkedIn post content:\n{post}"

def publish_linkedin_post(access_token: str, author_urn: str, post_content: str) -> dict:
    """
    Publishes a post to LinkedIn.
    :param access_token: OAuth2 access token with w_member_social permission
    :param author_urn: LinkedIn URN of the author (e.g., 'urn:li:person:xxxx')
    :param post_content: The text content of the post
    :return: LinkedIn API response as a dict
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json() 