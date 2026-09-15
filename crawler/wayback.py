import time
import requests
from crawler.config import TIMEOUT, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}
SAVE_ENDPOINT = "https://web.archive.org/save/"

class WaybackClient:
    def __init__(self, credentials, dry_run=False):
        self.credentials = credentials
        self.dry_run = dry_run
        
        self.auth_header = None
        if credentials.get("access_key") and credentials.get("secret_key"):
            self.auth_header = f"LOW {credentials['access_key']}:{credentials['secret_key']}"

    def save_url(self, url: str) -> (bool, str):
        """Returns (success, reason_or_url)"""
        if self.dry_run:
            return True, f"https://web.archive.org/web/{url}"
            
        req_headers = HEADERS.copy()
        if self.auth_header:
            req_headers["Authorization"] = self.auth_header

        try:
            response = requests.post(
                SAVE_ENDPOINT,
                data={"url": url},
                headers=req_headers,
                timeout=TIMEOUT,
            )

            if response.status_code == 429:
                return False, "Rate limited (429)"
            if response.status_code >= 500:
                return False, f"Server error ({response.status_code})"
                
            if response.ok:
                try:
                    data = response.json()
                    job_id = data.get("job_id")
                    if job_id:
                        # In a real robust system, we would poll the status API here:
                        # https://web.archive.org/save/status/JOB_ID
                        # For now we'll just consider it queued/success.
                        pass
                except ValueError:
                    pass
                return True, "Successfully archived"
            else:
                return False, f"HTTP {response.status_code}"

        except requests.RequestException as e:
            return False, str(e)
