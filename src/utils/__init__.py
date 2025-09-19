import requests
import re
from typing import Optional, List, Dict, Tuple
from urllib.parse import urlparse

def url_exists(url: str, timeout: float = 5.0) -> bool:
    """
    Check if a URL exists and is reachable (status code 200-399).
    Returns True if reachable, False otherwise.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        return 200 <= response.status_code < 400
    except Exception:
        return False

def validate_url_detailed(url: str, timeout: float = 5.0) -> Tuple[bool, str, int]:
    """
    Validate URL with detailed information.
    Returns (is_valid, reason, status_code)
    """
    try:
        # Basic URL format validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format", 0
        
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        status_code = response.status_code
        
        if 200 <= status_code < 400:
            return True, "URL is valid and reachable", status_code
        elif status_code == 404:
            return False, "URL not found (404)", status_code
        elif status_code >= 500:
            return False, "Server error", status_code
        else:
            return False, f"HTTP {status_code}", status_code
            
    except requests.exceptions.Timeout:
        return False, "Request timeout", 0
    except requests.exceptions.ConnectionError:
        return False, "Connection error", 0
    except Exception as e:
        return False, f"Validation error: {str(e)}", 0

def get_newsletter_status(newsletter_url: str = None) -> str:
    """
    Return newsletter link if provided and valid, else 'Newsletter coming soon'.
    """
    if newsletter_url and url_exists(newsletter_url):
        return f"[Subscribe to our newsletter]({newsletter_url})"
    return "Newsletter coming soon"

def validate_image_url(image_url: str, topic_keywords: Optional[List[str]] = None) -> tuple[bool, str]:
    """
    Validate if an image URL exists and optionally check topic relevance.
    Returns (is_valid, reason) tuple.
    """
    if not url_exists(image_url):
        return False, "Image URL not reachable"
    
    # Basic image format check
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    if not any(ext in image_url.lower() for ext in image_extensions):
        return False, "URL does not appear to be an image"
    
    # Optional topic relevance check
    if topic_keywords:
        url_lower = image_url.lower()
        if not any(keyword.lower() in url_lower for keyword in topic_keywords):
            return False, "Image may not be relevant to blog topic"
    
    return True, "Image is valid and relevant"

def safe_replace_links(content: str, link_mappings: dict) -> str:
    """
    Safely replace links in content based on provided mappings.
    link_mappings: {original_url: fallback_url_or_text}
    """
    for original_url, fallback in link_mappings.items():
        if original_url in content and not url_exists(original_url):
            content = content.replace(original_url, fallback)
    return content

def extract_topic_keywords(topic: str) -> List[str]:
    """
    Extract relevant keywords from a blog topic for image validation.
    """
    # Remove common words and extract meaningful keywords
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
    
    words = re.findall(r'\b\w+\b', topic.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords[:5]  # Return top 5 keywords

def extract_urls_from_content(content: str) -> List[str]:
    """
    Extract all URLs from blog content (markdown links, plain URLs, etc.).
    Returns list of unique URLs found in the content.
    """
    urls = set()
    
    # Extract markdown links [text](url)
    markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
    for text, url in markdown_links:
        if url.startswith(('http://', 'https://')):
            urls.add(url)
    
    # Extract plain URLs (improved regex to avoid capturing numbered lists)
    plain_urls = re.findall(r'(?<!\d\.\s)https?://[^\s\)\]\>]+', content)
    urls.update(plain_urls)
    
    # Extract URLs from reference sections
    reference_patterns = [
        r'\[(\d+)\]:\s*(https?://[^\s]+)',  # [1]: https://...
        r'Source:\s*(https?://[^\s]+)',     # Source: https://...
        r'Reference:\s*(https?://[^\s]+)',  # Reference: https://...
    ]
    
    for pattern in reference_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if matches and isinstance(matches[0], tuple):
            urls.update([match[1] for match in matches if len(match) > 1])
        elif matches:
            urls.update(matches)
    
    return list(urls)

def validate_all_urls_in_content(content: str, timeout: float = 5.0) -> Dict[str, Dict]:
    """
    Validate all URLs found in blog content.
    Returns dictionary with URL validation results.
    """
    urls = extract_urls_from_content(content)
    results = {}
    
    for url in urls:
        is_valid, reason, status_code = validate_url_detailed(url, timeout)
        results[url] = {
            'valid': is_valid,
            'reason': reason,
            'status_code': status_code
        }
    
    return results

def clean_invalid_urls_from_content(content: str, timeout: float = 5.0, remove_invalid: bool = True) -> Tuple[str, Dict[str, Dict]]:
    """
    Clean invalid URLs from content and return cleaned content with validation results.
    
    Args:
        content: Blog content to clean
        timeout: Request timeout for URL validation
        remove_invalid: If True, removes invalid URLs; if False, replaces with placeholder
    
    Returns:
        Tuple of (cleaned_content, validation_results)
    """
    validation_results = validate_all_urls_in_content(content, timeout)
    cleaned_content = content
    
    for url, result in validation_results.items():
        if not result['valid']:
            if remove_invalid:
                # Remove invalid URLs completely
                cleaned_content = cleaned_content.replace(url, '')
                # Clean up any orphaned markdown syntax
                cleaned_content = re.sub(r'\[([^\]]*)\]\(\s*\)', r'\1', cleaned_content)
                cleaned_content = re.sub(r'\[\s*\]\([^)]*\)', '', cleaned_content)
            else:
                # Replace with placeholder
                placeholder = f"[Invalid URL - {result['reason']}]"
                cleaned_content = cleaned_content.replace(url, placeholder)
    
    return cleaned_content, validation_results

def get_url_validation_report(validation_results: Dict[str, Dict]) -> str:
    """
    Generate a human-readable report of URL validation results.
    """
    total_urls = len(validation_results)
    valid_urls = sum(1 for result in validation_results.values() if result['valid'])
    invalid_urls = total_urls - valid_urls
    
    report = f"URL Validation Report:\n"
    report += f"Total URLs found: {total_urls}\n"
    report += f"Valid URLs: {valid_urls}\n"
    report += f"Invalid URLs: {invalid_urls}\n\n"
    
    if invalid_urls > 0:
        report += "Invalid URLs:\n"
        for url, result in validation_results.items():
            if not result['valid']:
                report += f"  ❌ {url} - {result['reason']}\n"
    
    if valid_urls > 0:
        report += "\nValid URLs:\n"
        for url, result in validation_results.items():
            if result['valid']:
                report += f"  ✅ {url} (HTTP {result['status_code']})\n"
    
    return report 