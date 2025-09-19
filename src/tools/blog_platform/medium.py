from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from src.utils import url_exists, get_newsletter_status, validate_image_url, safe_replace_links, extract_topic_keywords
import re

class MediumPostToolInput(BaseModel):
    title: str = Field(..., description="Title of the Medium article.")
    content: str = Field(..., description="Content of the Medium article.")

class MediumPostTool(BaseTool):
    name: str = "MediumPostTool"
    description: str = "Posts an article to Medium. (Stub implementation)"
    args_schema: Type[BaseModel] = MediumPostToolInput

    def _run(self, title: str, content: str) -> str:
        # Process content with safe checks for links and images
        processed_content = self._process_content_for_medium(content, title)
        
        # Stub: Replace with real Medium API integration
        return f"(Stub) Medium article posted: {title}\n\nProcessed content length: {len(processed_content)} characters"

    def _process_content_for_medium(self, content: str, topic: str = None) -> str:
        """Process content for Medium with safe checks for links and images"""

        # Safe check for call-to-action links
        content = self._safe_check_cta_links(content)

        # Handle image placeholders with validation
        content = self._handle_image_placeholders(content, topic)

        # Convert markdown to Medium format
        content = self._convert_markdown_to_medium_format(content)

        return content

    def _safe_check_cta_links(self, content: str) -> str:
        """Check and update CTA links and newsletter mentions safely."""
        # Define link mappings for safe replacement
        link_mappings = {
            "https://dev.to/satyam_chourasiya_99ea2e4": "#",
            "https://www.satyam.my": "#"
        }

        # Use the utility function for safe link replacement
        content = safe_replace_links(content, link_mappings)

        # Handle newsletter mentions
        content = re.sub(r'\[Newsletter:.*?\]\([^)]+\)', get_newsletter_status(), content)

        return content

    def _handle_image_placeholders(self, content: str, topic: str = None) -> str:
        """Handle image placeholders with validation for Medium"""

        # Extract topic keywords for image relevance check
        topic_keywords = extract_topic_keywords(topic) if topic else None

        # Define image mappings with validation
        image_mappings = [
            (r'\[IMAGE:([^\]]+)\]', 'https://via.placeholder.com/800x400/2563eb/ffffff?text=\\1', 'general'),
            (r'\[DIAGRAM:([^\]]+)\]', 'https://via.placeholder.com/800x400/059669/ffffff?text=Diagram:+\\1', 'diagram'),
            (r'\[CHART:([^\]]+)\]', 'https://via.placeholder.com/800x400/d97706/ffffff?text=Chart:+\\1', 'chart'),
            (r'\[GRAPH:([^\]]+)\]', 'https://via.placeholder.com/800x400/7c3aed/ffffff?text=Graph:+\\1', 'graph'),
            (r'\[SCREENSHOT:([^\]]+)\]', 'https://via.placeholder.com/800x400/6b7280/ffffff?text=Screenshot:+\\1', 'screenshot')
        ]

        for pattern, placeholder_url, image_type in image_mappings:
            def replace_with_validation(match):
                description = match.group(1)
                # For placeholder images, we assume they're valid
                # For real image URLs, we would validate them here
                return f'![{description}]({placeholder_url})'

            content = re.sub(pattern, replace_with_validation, content)

        return content

    def _convert_markdown_to_medium_format(self, content: str) -> str:
        """Convert basic markdown to Medium's rich text format."""
        # This is a simplified conversion.
        # In a real Medium API, you'd use their rich text API.
        # For example, converting **bold** to <strong>bold</strong>
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
        content = re.sub(r'\n\n', r'\n\n', content) # Preserve newlines
        content = re.sub(r'\n', r'\n\n', content) # Convert single newlines to double newlines for Medium
        return content 