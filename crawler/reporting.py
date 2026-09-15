import json
from datetime import datetime

class Reporter:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()

    def add_site_result(self, result: dict):
        self.results.append(result)

    def save(self, filepath="run-results.json"):
        summary = {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "sites": self.results
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    def print_summary(self):
        print("\n==============================")
        print("WEEKLY ARCHIVE SUMMARY")
        print("==============================")
        
        total_urls = 0
        total_success = 0
        total_failed = 0
        
        for r in self.results:
            total_urls += r["selected_count"]
            total_success += r["archived_count"]
            total_failed += r["failed_count"]
            
        print(f"Sites processed: {len(self.results)}")
        print(f"URLs selected: {total_urls}")
        print(f"Wayback successes: {total_success}")
        print(f"Failures: {total_failed}\n")
        
        for r in self.results:
            print(f"{r['site']}")
            print(f"  selected: {r['selected_count']}")
            print(f"  archived: {r['archived_count']}")
            print(f"  failed: {r['failed_count']}")
            if r.get("representative_article"):
                print(f"  representative article:")
                print(f"    {r['representative_article']}")
            print("")
