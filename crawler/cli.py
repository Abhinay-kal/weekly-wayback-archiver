import argparse
import sys
import time
from crawler.config import load_sites, get_wayback_credentials, is_archive_enabled
from crawler.discovery import discover_all_urls
from crawler.filtering import is_excluded
from crawler.blog import classify_urls
from crawler.wayback import WaybackClient
from crawler.reporting import Reporter

def main():
    parser = argparse.ArgumentParser(description="Weekly Website Archiver")
    parser.add_argument("--dry-run", action="store_true", help="Do not submit to Wayback")
    parser.add_argument("--site", type=str, help="Process a specific site by name")
    parser.add_argument("--config", type=str, default="sites.json", help="Path to config file")
    
    args = parser.parse_args()
    
    # Check env var for archive mode if --dry-run is not explicitly passed
    dry_run = args.dry_run
    if not dry_run and not is_archive_enabled():
        print("ARCHIVE_ENABLED is false/missing. Defaulting to DRY-RUN mode.")
        dry_run = True

    sites = load_sites(args.config)
    if args.site:
        sites = [s for s in sites if s.name == args.site]
        if not sites:
            print(f"Site '{args.site}' not found in {args.config}")
            return 1

    creds = get_wayback_credentials()
    if not dry_run and not (creds.get("access_key") and creds.get("secret_key")):
        print("WARNING: Wayback credentials not found in environment variables.")
        
    client = WaybackClient(credentials=creds, dry_run=dry_run)
    reporter = Reporter()

    print(f"Running in {'DRY-RUN' if dry_run else 'ARCHIVE'} mode\n")

    for site in sites:
        print(f"=== SITE: {site.name} ({site.base_url}) ===")
        
        # 1. Discovery
        urls = discover_all_urls(site)
        print(f"Discovered {len(urls)} URLs")
        
        # 2. Filtering
        kept_urls = []
        excluded_urls = []
        for url in urls:
            excluded, reason = is_excluded(url, site)
            if excluded:
                excluded_urls.append((url, reason))
            else:
                kept_urls.append(url)
                
        # 3. Blog Classification & Selection
        normal, blog_index, blog_selected, blog_skipped = classify_urls(kept_urls, site)
        
        urls_to_archive = normal + blog_index
        if blog_selected:
            urls_to_archive.append(blog_selected)
            
        print("\nSAVE:")
        for u in urls_to_archive[:10]:
            print(f"  {u}")
        if len(urls_to_archive) > 10:
            print(f"  ... and {len(urls_to_archive) - 10} more")
            
        if blog_selected:
            print(f"\nREPRESENTATIVE BLOG ARTICLE:\n  {blog_selected}")
            
        if blog_skipped:
            print(f"\nSKIP ({len(blog_skipped)} blog posts):")
            for u in blog_skipped[:5]:
                print(f"  {u}")
            if len(blog_skipped) > 5:
                print(f"  ... and {len(blog_skipped) - 5} more")
                
        if excluded_urls:
            print(f"\nEXCLUDED ({len(excluded_urls)} URLs):")
            for u, reason in excluded_urls[:5]:
                print(f"  {u} [{reason}]")
            if len(excluded_urls) > 5:
                print(f"  ... and {len(excluded_urls) - 5} more")
                
        print("\n" + "-"*30)
                
        # 4. Wayback Submission
        archived_count = 0
        failed_count = 0
        
        if not dry_run:
            print("\nStarting Wayback submission...")
            for url in urls_to_archive:
                success, reason = client.save_url(url)
                if success:
                    archived_count += 1
                else:
                    print(f"Failed to archive {url}: {reason}")
                    failed_count += 1
                # Rate limiting
                time.sleep(10)
        else:
            archived_count = len(urls_to_archive)
            
        reporter.add_site_result({
            "site": site.name,
            "discovered_count": len(urls),
            "selected_count": len(urls_to_archive),
            "archived_count": archived_count,
            "failed_count": failed_count,
            "representative_article": blog_selected
        })
        
    reporter.print_summary()
    reporter.save()
    return 0

if __name__ == "__main__":
    sys.exit(main())
