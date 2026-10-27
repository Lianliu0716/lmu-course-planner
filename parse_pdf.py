"""
Turn the LMU faculty course PDF into courses.js for planner.html.

Usage:
  uv run --with pdfplumber parse_pdf.py   (or: pdftotext -layout file.pdf out.txt; python parse_pdf.py out.txt)
"""
import re, sys, json, pathlib, subprocess

PDF = "veranstaltungsverzeichnis-der-fak.-16-wise-2026_27.pdf"
DAYS = {"Mo": 0, "Di": 1, "Mi": 2, "Do": 3, "Fr": 4}
SESSION = re.compile(r"((?:Mo|Di|Mi|Do|Fr)(?:\s*(?:,|und)\s*(?:Mo|Di|Mi|Do|Fr))*)\.?\s+(\d{1,2})(?::(\d\d))?\s*-\s*(\d{1,2})(?::(\d\d))?(\s*Uhr)?(\s*[cs]\.t\.)?")
TYPES = ["Vorlesung", "Übung", "Seminar", "Praktikum", "Proseminar", "Hauptseminar", "Oberseminar", "Kolloquium", "Tutorium"]

def get_text():
    if len(sys.argv) > 1:
        return pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    try:
        return subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True, check=True).stdout
    except Exception:
        import pdfplumber
        with pdfplumber.open(PDF) as pdf:
            return "\n".join(p.extract_text(layout=True) or "" for p in pdf.pages)

SECTIONS = {"1. Mathematik": "Mathematics", "2. Informatik": "Computer Science", "3. Statistik": "Statistics", "4. Lehrstuhl": "History of Science"}

def entries(text):
    cur = None
    dept, level = "", ""
    for line in text.splitlines():
        st = line.strip()
        for k, val in SECTIONS.items():
            if st.startswith(k):
                dept, level = val, ""
        if not re.match(r"^\d{5}", line) and re.search(r"Bachelor|Master", st) and len(st) < 120:
            level = "Master" if "Master" in st else "Bachelor"
        m = re.match(r"^(\d{5})\s{2,}(.*)$", line)
        if m:
            if cur: yield cur
            body = m.group(2)
            parts = re.split(r"\s{3,}", body.rstrip())
            lecturer = parts[-1].strip() if len(parts) > 1 else ""
            cur = {"no": m.group(1), "text": " ".join(parts[:-1]) if len(parts) > 1 else body, "lecturer": lecturer, "dept": dept, "level": level}
        elif cur and line.startswith(" " * 6) and line.strip() and not re.match(r"^\s{6,}(P|WP)\s?\d", line):
            cur["text"] += " " + re.split(r"\s{3,}", line.strip())[0]
        elif cur:
            yield cur; cur = None
    if cur: yield cur

def parse(e):
    t = re.sub(r"\s+", " ", e["text"]).strip()
    parts = [p.strip() for p in t.split(",")]
    name = parts[0]
    ctype = next((p for p in parts[1:3] if p in TYPES), "")
    if "Gruppe" in t:
        return None  # exercise groups: too many slots for a timetable
    sessions = []
    ms = list(SESSION.finditer(t))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        after = t[m.end():end]
        after = re.split(r"Beginn:|Ende:", after)[0]
        room = after.strip(" ,()")
        room = re.sub(r"^\(|\)$", "", room).strip(" ,")
        s = int(m.group(2)) + int(m.group(3) or 0) / 60
        en = int(m.group(4)) + int(m.group(5) or 0) / 60
        ct = bool(m.group(7) and "c" in m.group(7))
        for d in re.findall(r"Mo|Di|Mi|Do|Fr", m.group(1)):
            sessions.append({"d": DAYS[d], "s": s, "e": en, "ct": ct, "room": room or None})
    # carry the last known room forward to sessions that list none
    last = None
    for x in sessions:
        last = x["room"] or last
    for x in reversed(sessions):
        if x["room"]: last = x["room"]
        elif last: x["room"] = last
    if not sessions or len(sessions) > 4:
        return None
    period = re.search(r"Beginn:\s*([\d.]+).*?Ende:\s*([\d.]+)", t)
    return {
        "id": e["no"], "name": name, "type": ctype, "lecturer": e["lecturer"],
        "sessions": sessions, "period": f"{period.group(1)}–{period.group(2)}" if period else "",
        "st": "ok" if all(x["room"] for x in sessions) else "check",
        "dept": e["dept"], "levels": [e["level"]] if e["level"] else [], "lang": guess_lang(name),
    }

GERMAN = re.compile(r"[äöüÄÖÜß]|\b(und|der|die|das|zu|zur|für|mit|von|in die|Einführung|Grundlagen|Übung|Übungen|Vorlesung|Seminar zu|Praktikum|Programmierung|Rechnung|Theorie der)\b")
def guess_lang(name):
    return "German" if GERMAN.search(name) else "English"

def main():
    seen, out, byno = set(), [], {}
    for e in entries(get_text()):
        if e["no"] in seen:
            c = byno.get(e["no"])
            if c and e["level"] and e["level"] not in c["levels"]:
                c["levels"].append(e["level"])
            continue
        seen.add(e["no"])
        c = parse(e)
        if c:
            out.append(c); byno[c["id"]] = c
    pathlib.Path("courses.js").write_text("window.COURSES = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(seen)} entries found, {len(out)} with a usable weekly time -> courses.js")
    for c in out[:8]:
        print(" ", c["id"], c["name"][:45], c["type"], [(x["d"], x["s"], x["e"], x["room"]) for x in c["sessions"]])

if __name__ == "__main__":
    main()
