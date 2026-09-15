import os
import json
from dataclasses import dataclass
from typing import List, Optional, Dict

TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (compatible; WeeklyWebsiteArchive/1.0; +https://github.com/)"

@dataclass
class SiteConfig:
    name: str
    base_url: str
    blog_enabled: bool = True
    blog_index_urls: List[str] = None
    blog_article_patterns: List[str] = None
    excluded_patterns: List[str] = None
    included_patterns: List[str] = None
    select_strategy: str = "newest"
    sitemap_url: Optional[str] = None
    max_pages: int = 5000

def load_sites(filepath: str) -> List[SiteConfig]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    sites = []
    for item in data:
        # Default handling
        blog_cfg = item.get("blog", {})
        
        site = SiteConfig(
            name=item["name"],
            base_url=item["base_url"],
            blog_enabled=blog_cfg.get("enabled", True),
            blog_index_urls=blog_cfg.get("index_urls", []),
            blog_article_patterns=blog_cfg.get("article_patterns", []),
            select_strategy=blog_cfg.get("select", "newest"),
            excluded_patterns=item.get("excluded_patterns", []),
            included_patterns=item.get("included_patterns", []),
            sitemap_url=item.get("sitemap_url"),
            max_pages=item.get("max_pages", 5000)
        )
        sites.append(site)
    return sites

def get_wayback_credentials():
    return {
        "access_key": os.environ.get("WAYBACK_ACCESS_KEY"),
        "secret_key": os.environ.get("WAYBACK_SECRET_KEY")
    }

def is_archive_enabled() -> bool:
    return os.environ.get("ARCHIVE_ENABLED", "false").lower() == "true"
