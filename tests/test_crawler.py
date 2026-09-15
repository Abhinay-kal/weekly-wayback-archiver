import unittest
from crawler.filtering import is_excluded
from crawler.config import SiteConfig
from crawler.blog import classify_urls
from crawler.discovery import normalize_url

class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.site = SiteConfig(
            name="test",
            base_url="https://example.com/",
            blog_enabled=True,
            blog_index_urls=["https://example.com/blog/"],
            blog_article_patterns=["/blog/"]
        )

    def test_normalize_url(self):
        self.assertEqual(normalize_url("https://example.com/blog"), "https://example.com/blog")
        self.assertEqual(normalize_url("https://example.com/blog/"), "https://example.com/blog")
        self.assertEqual(normalize_url("HTTP://Example.COM/"), "http://example.com/")

    def test_filtering_query_string(self):
        excluded, reason = is_excluded("https://example.com/page?sort=asc", self.site)
        self.assertTrue(excluded)
        self.assertEqual(reason, "query string")

    def test_filtering_pagination(self):
        excluded, reason = is_excluded("https://example.com/page/2/", self.site)
        self.assertTrue(excluded)
        self.assertEqual(reason, "pagination")

    def test_blog_classification(self):
        urls = [
            "https://example.com/about",
            "https://example.com/blog/",
            "https://example.com/blog/article-1",
            "https://example.com/blog/article-2"
        ]
        
        normal, index, selected, skipped = classify_urls(urls, self.site)
        self.assertIn("https://example.com/about", normal)
        self.assertIn("https://example.com/blog/", index)
        # alphabetical reverse sort selects article-2
        self.assertEqual(selected, "https://example.com/blog/article-2")
        self.assertIn("https://example.com/blog/article-1", skipped)

if __name__ == '__main__':
    unittest.main()
