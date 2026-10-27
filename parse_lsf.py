"""
Turn saved LSF pages (lsf_pages/*.html) into courses.js for planner.html.

Usage:
  pip install beautifulsoup4
  python parse_lsf.py
Then open planner.html in your browser.
"""
import re
import json
import pathlib
from bs4 import BeautifulSoup

DAYS = {"Mo": 0, "Di": 1, "Mi": 2, "Do": 3, "Fr": 4, "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
DAY_RE = re.compile(r"\b(Mo|Di|Mi|Do|Fr|Mon|Tue|Wed|Thu|Fri)\b\.?")
TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*(?:bis|-|–|to)\s*(\d{1,2}):(\d{2})")

def cell_after(soup, label):
    for th in soup.find_all(["th", "td"]):
        if label.lower() in th.get_text(" ", strip=True).lower():
            nxt = th.find_next_sibling(["td", "th"])
            if nxt:
                return nxt.get_text(" ", strip=True)
    return None

def parse(path, url):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    h1 = soup.find("h1")
    name = h1.get_text(" ", strip=True) if h1 else path.stem
    name = re.sub(r"\s*-\s*Einzelansicht\s*$", "", name)
    ctype = cell_after(soup, "Veranstaltungsart") or cell_after(soup, "Type") or ""

    for tr in soup.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        text = " ".join(cells)
        d, t = DAY_RE.search(text), TIME_RE.search(text)
        if not (d and t):
            continue
        h1_, m1, h2, m2 = map(int, t.groups())
        room = None
        link = tr.find("a", href=re.compile("raum", re.I))
        if link:
            room = link.get_text(" ", strip=True)
        else:
            for c in reversed(cells):
                if len(c) > 3 and not DAY_RE.fullmatch(c) and not TIME_RE.search(c) and not re.search(r"\d{2}\.\d{2}\.\d{4}", c):
                    room = c
                    break
        return {
            "name": name, "type": ctype, "d": DAYS[d.group(1)],
            "s": h1_ + m1 / 60, "e": h2 + m2 / 60,
            "room": room or "Room not found", "st": "ok" if room else "check", "url": url,
        }
    print(f"  ! No weekly time found in {path.name}, skipped")
    return None

def main():
    urls = []
    if pathlib.Path("urls.txt").exists():
        urls = [u.strip() for u in open("urls.txt", encoding="utf-8") if u.strip() and not u.startswith("#")]
    courses = []
    for i, p in enumerate(sorted(pathlib.Path("lsf_pages").glob("*.html"))):
        c = parse(p, urls[i] if i < len(urls) else "https://www.lsf.lmu.de")
        if c:
            c["id"] = f"c{i}"
            courses.append(c)
            print(f"  {c['name']} | day {c['d']} | {c['s']:.2f}-{c['e']:.2f} | {c['room']}")
    pathlib.Path("courses.js").write_text("window.COURSES = " + json.dumps(courses, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"Wrote courses.js with {len(courses)} courses. Open planner.html.")

if __name__ == "__main__":
    main()
