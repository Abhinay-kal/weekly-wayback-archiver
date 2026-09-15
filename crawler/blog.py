import re
from urllib.parse import urlparse

def classify_urls(urls, config):
    normal = []
    blog_index = []
    blog_posts = []
    
    for url in urls:
        if url in config.blog_index_urls:
            blog_index.append(url)
            continue
            
        path = urlparse(url).path.lower()
        is_post = False
        if config.blog_enabled and config.blog_article_patterns:
            for pattern in config.blog_article_patterns:
                if re.search(pattern, path) and path != pattern.strip("^$"):
                    is_post = True
                    break
                    
        if is_post:
            blog_posts.append(url)
        else:
            normal.append(url)
            
    # Select representative
    selected = None
    if blog_posts:
        # Default to newest (we'll just sort alphabetically for now as a fallback)
        selected = sorted(blog_posts, reverse=True)[0]
        
    skipped = [p for p in blog_posts if p != selected]
    return normal, blog_index, selected, skipped
