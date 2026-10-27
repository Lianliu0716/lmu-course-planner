"""
Fetch a few LSF course pages you choose, slowly, and save them as HTML.
Read-only, no login, no crawling: it only opens the URLs in urls.txt.

Usage:
  1. Open each course page in your browser, copy the URL into urls.txt (one per line, max ~5).
  2. pip install requests
  3. python fetch_lsf.py
"""
import time
import pathlib
import urllib.robotparser
import requests

URLS_FILE = "urls.txt"
OUT_DIR = pathlib.Path("lsf_pages")
DELAY_SECONDS = 5
MAX_PAGES = 5
HEADERS = {
    "User-Agent": "LMU student course-planner prototype (contact: see repository)"
}

def allowed_by_robots(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("https://www.lsf.lmu.de/robots.txt")
    try:
        rp.read()
    except Exception:
        print("Could not read robots.txt, stopping to be safe.")
        return False
    return rp.can_fetch(HEADERS["User-Agent"], url)

def main():
    urls = [u.strip() for u in open(URLS_FILE, encoding="utf-8") if u.strip() and not u.startswith("#")][:MAX_PAGES]
    OUT_DIR.mkdir(exist_ok=True)
    for i, url in enumerate(urls, 1):
        if not allowed_by_robots(url):
            print(f"[{i}] robots.txt disallows this URL, skipping: {url}")
            continue
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except requests.RequestException as e:
            print(f"[{i}] Network error, stopping: {e}")
            break
        if r.status_code != 200:
            print(f"[{i}] Got HTTP {r.status_code}, stopping.")
            break
        path = OUT_DIR / f"course_{i}.html"
        path.write_text(r.text, encoding=r.encoding or "utf-8")
        print(f"[{i}] Saved {path}")
        time.sleep(DELAY_SECONDS)
    print("Done. Tell Claude when lsf_pages/ is ready.")

if __name__ == "__main__":
    main()
