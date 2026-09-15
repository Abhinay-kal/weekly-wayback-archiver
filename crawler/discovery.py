import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from crawler.config import TIMEOUT, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = parsed.netloc.lower()
    path = parsed.path or "/"

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return f"{scheme}://{hostname}{path}"

def get_sitemap_urls(base_url: str):
    base = base_url.rstrip("/")
    candidates = [
        f"{base}/sitemap.xml",
        f"{base}/sitemap_index.xml",
        f"{base}/wp-sitemap.xml",
    ]

    urls = set()
    for sitemap in candidates:
        try:
            response = requests.get(sitemap, headers=HEADERS, timeout=TIMEOUT)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "xml")
            
            # Handle sitemap index
            for sitemap_loc in soup.find_all("sitemap"):
                loc = sitemap_loc.find("loc")
                if loc and loc.text:
                    sub_urls = get_sitemap_urls(loc.text.strip())
                    urls.update(sub_urls)

            # Handle direct URLs
            for url_loc in soup.find_all("url"):
                loc = url_loc.find("loc")
                if loc and loc.text:
                    urls.add(normalize_url(loc.text.strip()))

        except requests.RequestException:
            pass

    return list(urls)

def discover_html_links(url: str, base_url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code >= 400:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        base_netloc = urlparse(base_url).netloc.lower()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("mailto:", "tel:", "javascript:")) or href.startswith("#"):
                continue

            absolute = urljoin(url, href)
            parsed = urlparse(absolute)
            
            if parsed.scheme not in ("http", "https"):
                continue
            
            # Remove fragments
            absolute = absolute.split("#")[0]
            absolute = normalize_url(absolute)
            
            if urlparse(absolute).netloc.lower() == base_netloc:
                links.add(absolute)

        return list(links)
    except requests.RequestException:
        return []

def discover_all_urls(site_config):
    sitemap_url = site_config.sitemap_url or site_config.base_url
    urls = get_sitemap_urls(sitemap_url)
    
    if not urls:
        urls = [normalize_url(site_config.base_url)]
        urls.extend(discover_html_links(site_config.base_url, site_config.base_url))
        
    return list(set(urls))
