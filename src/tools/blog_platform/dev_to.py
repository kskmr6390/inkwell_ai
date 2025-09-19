from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import requests
import os
import re
from dotenv import load_dotenv
from src.utils import (
    url_exists, get_newsletter_status, validate_image_url, safe_replace_links, 
    extract_topic_keywords, clean_invalid_urls_from_content, get_url_validation_report
)

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

    def _process_markdown_for_devto(self, markdown_content: str, topic: str = None) -> str:
        """Process markdown content to fix common issues for Dev.to, with safe checks for links and images"""
        
        # First, validate and clean all URLs in the content
        cleaned_content, validation_results = clean_invalid_urls_from_content(markdown_content)
        
        # Log URL validation results
        if validation_results:
            validation_report = get_url_validation_report(validation_results)
            print(f"URL Validation Results:\n{validation_report}")
        
        # Remove duplicate headers (if title is already in content)
        lines = cleaned_content.split('\n')
        processed_lines = []
        
        # Skip the first header if it matches the title pattern
        skip_first_header = True
        
        for line in lines:
            # Skip the first # header (main title) as Dev.to uses the title field
            if skip_first_header and line.strip().startswith('# '):
                skip_first_header = False
                continue
            
            # Convert other headers to proper format
            if line.strip().startswith('## '):
                processed_lines.append(line)  # Keep ## headers
            elif line.strip().startswith('### '):
                processed_lines.append(line)  # Keep ### headers
            else:
                processed_lines.append(line)
        
        content = '\n'.join(processed_lines)
        
        # Fix table formatting for Dev.to
        content = self._fix_table_formatting(content)
        
        # Handle image placeholders - convert to proper markdown images with topic validation
        content = self._handle_image_placeholders(content, topic)
        
        # Convert tags to proper hashtags
        content = self._convert_tags_to_hashtags(content)
        
        # Handle quote placeholders - convert to markdown blockquotes
        content = self._handle_quote_placeholders(content)
        
        # Remove any remaining placeholder markers that weren't converted
        content = re.sub(r'\[CODE:.*?\]', '', content)
        content = re.sub(r'\[TABLE:.*?\]', '', content)
        
        # Safe check for call-to-action links
        content = self._safe_check_cta_links(content)
        
        return content.strip()

    def _fix_table_formatting(self, content: str) -> str:
        """Fix table formatting for Dev.to compatibility with proper column alignment"""
        
        lines = content.split('\n')
        fixed_lines = []
        in_table = False
        table_lines = []
        
        for line in lines:
            if '|' in line and not line.strip().startswith('#'):
                # This is a table line
                if not in_table:
                    in_table = True
                    table_lines = []
                
                table_lines.append(line)
            else:
                if in_table:
                    # Process the collected table lines
                    fixed_table = self._format_table_properly(table_lines)
                    fixed_lines.extend(fixed_table)
                    fixed_lines.append('')  # Add empty line after table
                    in_table = False
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _format_table_properly(self, table_lines: list) -> list:
        """Format table with proper column alignment and spacing"""
        if len(table_lines) < 2:
            return table_lines
        
        # Parse table to get column widths
        parsed_rows = []
        for line in table_lines:
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty cells at start/end if they exist
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            parsed_rows.append(cells)
        
        if not parsed_rows:
            return table_lines
        
        # Find maximum width for each column
        num_cols = max(len(row) for row in parsed_rows)
        col_widths = [0] * num_cols
        
        for row in parsed_rows:
            for i, cell in enumerate(row):
                if i < num_cols:
                    col_widths[i] = max(col_widths[i], len(cell))
        
        # Format each row with proper spacing
        formatted_rows = []
        for row in parsed_rows:
            formatted_cells = []
            for i, cell in enumerate(row):
                if i < num_cols:
                    # Pad cell to match column width
                    formatted_cells.append(f" {cell:<{col_widths[i]}} ")
                else:
                    formatted_cells.append(" ")
            
            formatted_row = "|".join(formatted_cells)
            formatted_rows.append(formatted_row)
        
        return formatted_rows

    def _handle_image_placeholders(self, content: str, topic: str = None) -> str:
        """Handle image placeholders and convert to Dev.to format with validation"""
        
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

    def _convert_tags_to_hashtags(self, content: str) -> str:
        """Convert tag sections to proper hashtags"""
        
        # Find tag sections and convert to hashtags
        tag_pattern = r'## Suggested Tags\s*\n\s*\n((?:- [^\n]+\s*\n?)+)'
        
        def replace_tags(match):
            tag_lines = match.group(1).strip().split('\n')
            hashtags = []
            
            for line in tag_lines:
                if line.strip().startswith('- '):
                    tag = line.strip()[2:].strip()  # Remove "- " prefix
                    # Convert to hashtag format
                    hashtag = '#' + tag.replace(' ', '').replace('-', '').lower()
                    hashtags.append(hashtag)
            
            if hashtags:
                return '\n\n' + ' '.join(hashtags) + '\n\n'
            return ''
        
        content = re.sub(tag_pattern, replace_tags, content)
        
        return content

    def _handle_quote_placeholders(self, content: str) -> str:
        """Handle quote placeholders and convert to markdown blockquotes"""
        
        # Convert [QUOTE: text] to markdown blockquotes
        content = re.sub(
            r'\[QUOTE:([^\]]+)\]', 
            r'> \\1', 
            content
        )
        
        # Handle multi-line quotes if needed
        # This handles cases where quotes might span multiple lines
        lines = content.split('\n')
        processed_lines = []
        in_quote = False
        
        for line in lines:
            if line.strip().startswith('[QUOTE:'):
                # Start of a quote
                quote_text = re.search(r'\[QUOTE:([^\]]+)\]', line)
                if quote_text:
                    processed_lines.append(f"> {quote_text.group(1)}")
                    in_quote = True
            elif in_quote and line.strip().startswith('[/QUOTE]'):
                # End of quote
                in_quote = False
            elif in_quote and line.strip():
                # Continuation of quote
                processed_lines.append(f"> {line.strip()}")
            else:
                # Regular line
                processed_lines.append(line)
                in_quote = False
        
        return '\n'.join(processed_lines)

    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract tags from content for the API"""
        
        # Look for hashtags in the content
        hashtags = re.findall(r'#(\w+)', content)
        
        # Also look for tag sections
        tag_pattern = r'## Suggested Tags\s*\n\s*\n((?:- [^\n]+\s*\n?)+)'
        match = re.search(tag_pattern, content)
        
        if match:
            tag_lines = match.group(1).strip().split('\n')
            for line in tag_lines:
                if line.strip().startswith('- '):
                    tag = line.strip()[2:].strip()
                    # Convert to tag format (lowercase, no spaces)
                    clean_tag = tag.replace(' ', '').replace('-', '').lower()
                    if clean_tag not in hashtags:
                        hashtags.append(clean_tag)
        
        # Ensure we have some default tags if none found
        if not hashtags:
            hashtags = ['ai', 'engineering', 'scalability', 'architecture']
        
        return hashtags[:4]  # Dev.to allows max 4 tags

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

    def _run(self, title: str, body_markdown: str, tags: Optional[List[str]] = None, published: bool = True) -> str:
        api_key = os.getenv("DEVTO_API_KEY")
        if not api_key:
            return "Error: DEVTO_API_KEY not found in environment or .env file."
        
        # Process the markdown content with topic for image validation
        processed_markdown = self._process_markdown_for_devto(body_markdown, title)
        
        # Extract tags from content if not provided
        if not tags:
            tags = self._extract_tags_from_content(body_markdown)
        
        # Ensure tags are in the right format for Dev.to
        clean_tags = []
        for tag in tags:
            # Convert to lowercase and remove spaces
            clean_tag = tag.lower().replace(' ', '').replace('-', '')
            if clean_tag not in clean_tags:
                clean_tags.append(clean_tag)
        
        # Enforce a maximum of 4 tags
        safe_tags = clean_tags[:4]
        
        url = "https://dev.to/api/articles"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "article": {
                "title": title,
                "published": published,
                "body_markdown": processed_markdown,
                "tags": safe_tags
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                article_data = response.json()
                article_url = article_data.get('url', 'No URL returned')
                return f"Success! Article posted to Dev.to: {article_url}"
            else:
                return f"Failed to post article: {response.status_code} {response.text}"
        except Exception as e:
            return f"Error posting to Dev.to: {str(e)}" 