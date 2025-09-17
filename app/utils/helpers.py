"""
Helper functions for the AI Content Factory application
"""
import re
from typing import Dict, Any
from datetime import datetime


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', filename)
    # Limit length
    return sanitized[:255]


def format_timestamp(timestamp: datetime) -> str:
    """Format a timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def merge_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge two dictionaries, with dict2 values overriding dict1 values"""
    result = dict1.copy()
    result.update(dict2)
    return result


def extract_domain(url: str) -> str:
    """Extract the domain from a URL"""
    # Simple regex to extract domain
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if match:
        return match.group(1)
    return url