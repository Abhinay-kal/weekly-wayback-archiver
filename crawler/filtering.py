import re
from urllib.parse import urlparse

def is_excluded(url: str, config) -> (bool, str):
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Query strings
    if parsed.query:
        return True, "query string"
        
    # Common filters
    if "author" in path: return True, "author archive"
    if "tag" in path: return True, "tag archive"
    if "category" in path and not path.strip("/").endswith("blog"): return True, "category archive"
    if "/page/" in path: return True, "pagination"
    if "/search" in path: return True, "search"
    if "login" in path or "admin" in path: return True, "login/admin"
    
    # Explicit exclusions
    if config.excluded_patterns:
        for pattern in config.excluded_patterns:
            if re.search(pattern, path):
                return True, f"matches excluded pattern: {pattern}"
                
    return False, ""
