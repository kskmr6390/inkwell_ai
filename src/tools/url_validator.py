from crewai.tools import BaseTool
from typing import Type, Dict, Optional
from pydantic import BaseModel, Field
from src.utils import (
    validate_all_urls_in_content, 
    clean_invalid_urls_from_content,
    get_url_validation_report,
    extract_urls_from_content
)

class URLValidatorToolInput(BaseModel):
    """Input schema for URLValidatorTool."""
    content: str = Field(..., description="Blog content to validate URLs in")
    timeout: float = Field(default=5.0, description="Request timeout for URL validation in seconds")
    remove_invalid: bool = Field(default=True, description="Whether to remove invalid URLs or replace with placeholder")

class URLValidatorTool(BaseTool):
    name: str = "URLValidatorTool"
    description: str = (
        "Validates all URLs in blog content and removes/replaces invalid ones. "
        "This tool ensures all references and links in the blog post are valid and reachable."
    )
    args_schema: Type[BaseModel] = URLValidatorToolInput

    def _run(self, content: str, timeout: float = 5.0, remove_invalid: bool = True) -> str:
        """
        Validate all URLs in content and return cleaned content with validation report.
        
        Args:
            content: Blog content to validate
            timeout: Request timeout for URL validation
            remove_invalid: Whether to remove invalid URLs or replace with placeholder
            
        Returns:
            String containing cleaned content and validation report
        """
        try:
            # Clean invalid URLs from content
            cleaned_content, validation_results = clean_invalid_urls_from_content(
                content, timeout, remove_invalid
            )
            
            # Generate validation report
            report = get_url_validation_report(validation_results)
            
            # Combine cleaned content with report
            result = f"URL VALIDATION COMPLETED\n"
            result += "=" * 50 + "\n\n"
            result += report + "\n\n"
            result += "CLEANED CONTENT:\n"
            result += "=" * 50 + "\n"
            result += cleaned_content
            
            return result
            
        except Exception as e:
            return f"Error during URL validation: {str(e)}\n\nOriginal content:\n{content}"

class URLCheckerToolInput(BaseModel):
    """Input schema for URLCheckerTool."""
    content: str = Field(..., description="Blog content to check URLs in")

class URLCheckerTool(BaseTool):
    name: str = "URLCheckerTool"
    description: str = (
        "Checks all URLs in blog content without modifying the content. "
        "Returns a detailed report of URL validation results for review."
    )
    args_schema: Type[BaseModel] = URLCheckerToolInput

    def _run(self, content: str) -> str:
        """
        Check all URLs in content and return validation report without modifying content.
        
        Args:
            content: Blog content to check
            
        Returns:
            String containing validation report
        """
        try:
            # Extract and validate URLs
            urls = extract_urls_from_content(content)
            validation_results = {}
            
            from src.utils import validate_url_detailed
            for url in urls:
                is_valid, reason, status_code = validate_url_detailed(url)
                validation_results[url] = {
                    'valid': is_valid,
                    'reason': reason,
                    'status_code': status_code
                }
            
            # Generate validation report
            report = get_url_validation_report(validation_results)
            
            return report
            
        except Exception as e:
            return f"Error during URL checking: {str(e)}"

