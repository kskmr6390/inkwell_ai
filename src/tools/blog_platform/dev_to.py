from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DevToPostToolInput(BaseModel):
    title: str = Field(..., description="Title of the dev.to article.")
    body_markdown: str = Field(..., description="Markdown content of the article.")
    tags: Optional[List[str]] = Field(default=None, description="List of tags for the article.")
    published: bool = Field(default=True, description="Whether to publish immediately.")

class DevToPostTool(BaseTool):
    name: str = "DevToPostTool"
    description: str = "Posts a markdown article to dev.to using the dev.to API. The API key is loaded from the DEVTO_API_KEY environment variable."
    args_schema: Type[BaseModel] = DevToPostToolInput

    def _run(self, title: str, body_markdown: str, tags: Optional[List[str]] = None, published: bool = True) -> str:
        api_key = os.getenv("DEVTO_API_KEY")
        if not api_key:
            return "Error: DEVTO_API_KEY not found in environment or .env file."
        url = "https://dev.to/api/articles"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        # Enforce a maximum of 4 tags
        safe_tags = (tags or [])[:4]
        data = {
            "article": {
                "title": title,
                "published": published,
                "body_markdown": body_markdown,
                "tags": safe_tags
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            return f"Success! Article posted: {response.json().get('url', 'No URL returned')}"
        else:
            return f"Failed to post article: {response.status_code} {response.text}" 