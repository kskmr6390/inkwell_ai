from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class MediumPostToolInput(BaseModel):
    title: str = Field(..., description="Title of the Medium article.")
    content: str = Field(..., description="Content of the Medium article.")

class MediumPostTool(BaseTool):
    name: str = "MediumPostTool"
    description: str = "Posts an article to Medium. (Stub implementation)"
    args_schema: Type[BaseModel] = MediumPostToolInput

    def _run(self, title: str, content: str) -> str:
        # Stub: Replace with real Medium API integration
        return f"(Stub) Medium article posted: {title}" 