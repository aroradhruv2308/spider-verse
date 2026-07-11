"""
daily_sync.py — Google Doc -> Quartz daily notes, with zero AI involvement.

Reads the "Daily Log" Google Doc via its public markdown-export URL, slices it
into dated daily entries plus optional "File: <path>.md" topic notes, writes
any that don't exist yet into content/, and publishes with `npx quartz sync`.

Conventions expected in the Doc:
  - Each day starts with a heading containing the date, e.g. "July 12, 2026"
    (also accepted: "12 July 2026", "2026-07-12").
  - Inside a day, optional labeled sections: One line / What happened /
    What I learned / Tomorrow (with or without bold / trailing colon).
  - A line like "File: AI-and-ML/LLM-Basic/Transformers.md" starts a topic
    note; everything until the next File: line or date heading is its body.

Safety rules:
  - Never overwrites an existing file (edits belong in Obsidian); collisions
    are reported and skipped.
  - Topic-note paths must live inside one of the allowed top-level sections.
  - Catches up on any missed days each time it runs.

Usage:
  python daily_sync.py                 # fetch Doc, write new notes, sync
  python daily_sync.py --dry-run       # show what would happen, write nothing
  python daily_sync.py --input x.md    # parse a local file instead of the Doc
  python daily_sync.py --no-sync       # write files but skip git publish
"""

import argparse
import datetime as dt
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent


def load_doc_id() -> str:
    """Doc id stays OUT of the public repo: read from scripts/doc_id.txt
    (git-ignored) or the SPIDERVERSE_DOC_ID environment variable."""
    import os
    id_file = REPO / "scripts" / "doc_id.txt"
    if id_file.exists():
        return id_file.read_text(encoding="utf-8").strip()
    return os.environ.get("SPIDERVERSE_DOC_ID", "")
CONTENT = REPO / "content"
DAILY_DIR = CONTENT / "Daily"

ALLOWED_SECTIONS = {
    "daily": "Daily",
    "ai-and-ml": "AI-and-ML",
    "software-engineering": "Software-Engineering",
    "system-design-and-lld": "System-Design-and-LLD",
    "fitness": "Fitness",
    "general-concepts": "General-Concepts",
    "mind-and-life": "Mind-and-Life",
    "career-and-money": "Career-and-Money",
    "english": "English",
}

DATE_FORMATS = ["%B %d, %Y", "%B %d %Y", "%d %B %Y", "%d %B, %Y", "%Y-%m-%d", "%d/%m/%Y"]
SECTION_LABELS = {
    "one line": "One line",
    "what happened": "What happened",
    "what i learned": "What I learned",
    "tomorrow": "Tomorrow",
}

DATE_HEADING_RE = re.compile(r"^(?:#{1,6}\s*|\*\*)?\s*([A-Za-z0-9 ,/-]+?)\s*(?:\*\*)?\s*$")
FILE_LINE_RE = re.compile(r"^(?:#{1,6}\s*)?\**\s*File:\s*(\S+?\.md)\s*\**\s*$", re.IGNORECASE)
LABEL_RE = re.compile(
    r"^\**\s*(one line|what happened|what i learned|tomorrow)\s*\**\s*:?\s*\**\s*(.*)$",
    re.IGNORECASE,
)


def parse_date(text: str):
    cleaned = re.sub(r"\s+", " ", text.strip().strip("#*").strip()).title()
    for fmt in DATE_FORMATS:
        try:
            return dt.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def fetch_doc_markdown() -> str:
    doc_id = load_doc_id()
    if not doc_id:
        sys.exit("ERROR: no Doc id. Put it in scripts/doc_id.txt (one line) "
                 "or set SPIDERVERSE_DOC_ID.")
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=markdown"
    for fmt in ("markdown", "txt"):
        try:
            req = urllib.request.Request(
                url.replace("format=markdown", f"format={fmt}"),
                headers={"User-Agent": "Mozilla/5.0 (daily-sync script)"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            if "accounts.google.com" in body[:2000]:
                sys.exit("ERROR: Doc is not link-shared (got a login page). "
                         "Share -> Anyone with the link -> Viewer.")
            return body
        except urllib.error.HTTPError as e:
            if fmt == "txt":
                sys.exit(f"ERROR: could not export the Doc (HTTP {e.code}).")
    return ""


def split_days(md: str):
    """Return list of (date, lines) chunks in document order."""
    days, current_date, buf = [], None, []
    for line in md.splitlines():
        maybe = DATE_HEADING_RE.match(line)
        parsed = parse_date(maybe.group(1)) if maybe else None
        if parsed:
            if current_date:
                days.append((current_date, buf))
            current_date, buf = parsed, []
        elif current_date:
            buf.append(line)
    if current_date:
        days.append((current_date, buf))
    return days


def split_file_sections(lines):
    """Split one day's lines into (daily_lines, [(path, note_lines), ...])."""
    daily, notes, target, buf = [], [], None, []
    for line in lines:
        m = FILE_LINE_RE.match(line)
        if m:
            if target:
                notes.append((target, buf))
            target, buf = m.group(1), []
        elif target:
            buf.append(line)
        else:
            daily.append(line)
    if target:
        notes.append((target, buf))
    return daily, notes


def render_daily(date: dt.date, lines) -> str | None:
    sections, current, free = {}, None, []
    for line in lines:
        m = LABEL_RE.match(line)
        if m:
            current = m.group(1).lower()
            sections[current] = [m.group(2)] if m.group(2).strip() else []
        elif current:
            sections[current].append(line)
        elif line.strip():
            free.append(line)

    if not sections and not any(l.strip() for l in free):
        return None  # empty day — nothing to publish

    out = [
        "---",
        f'title: "{date.strftime("%A, %B %#d") if sys.platform == "win32" else date.strftime("%A, %B %-d")}"',
        f"date: {date.isoformat()}",
        "type: daily",
        "tags:",
        "  - daily",
        "---",
        "",
    ]
    for label, heading in SECTION_LABELS.items():
        if label in sections:
            body = "\n".join(sections[label]).strip()
            out += [f"## {heading}", "", body, ""]
    if free and not sections:
        out += ["\n".join(free).strip(), ""]
    return "\n".join(out).rstrip() + "\n"


def resolve_note_path(raw: str) -> Path | None:
    p = raw.replace("\\", "/").lstrip("/")
    if ".." in p.split("/"):
        return None
    parts = p.split("/")
    section = ALLOWED_SECTIONS.get(parts[0].lower())
    if not section or len(parts) < 2:
        return None
    return CONTENT.joinpath(section, *parts[1:])


def render_note(path: Path, lines) -> str:
    title = path.stem.replace("-", " ").replace("_", " ")
    body = "\n".join(lines).strip()
    return f"---\ntitle: {title}\n---\n\n{body}\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-sync", action="store_true")
    ap.add_argument("--input", help="parse a local markdown file instead of fetching")
    args = ap.parse_args()

    md = Path(args.input).read_text(encoding="utf-8") if args.input else fetch_doc_markdown()

    created, skipped = [], []
    for date, day_lines in split_days(md):
        daily_lines, note_sections = split_file_sections(day_lines)

        target = DAILY_DIR / f"{date.isoformat()}.md"
        rendered = render_daily(date, daily_lines)
        if rendered:
            if target.exists():
                skipped.append((target, "already exists"))
            elif args.dry_run:
                created.append(target)
                print(f"--- would write {target} ---\n{rendered}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(rendered, encoding="utf-8", newline="\n")
                created.append(target)

        for raw_path, note_lines in note_sections:
            npath = resolve_note_path(raw_path)
            if npath is None:
                skipped.append((raw_path, "invalid path (must be inside a known section)"))
                continue
            if npath.exists():
                skipped.append((npath, "already exists — edit it in Obsidian instead"))
                continue
            rendered = render_note(npath, note_lines)
            if args.dry_run:
                created.append(npath)
                print(f"--- would write {npath} ---\n{rendered}")
            else:
                npath.parent.mkdir(parents=True, exist_ok=True)
                npath.write_text(rendered, encoding="utf-8", newline="\n")
                created.append(npath)

    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{stamp}] created: {len(created)}, skipped: {len(skipped)}")
    for path in created:
        print(f"  + {path}")
    for path, why in skipped:
        print(f"  ~ skipped {path}: {why}")

    if created and not args.dry_run and not args.no_sync:
        names = ", ".join(p.name for p in created[:5])
        result = subprocess.run(
            f'npx quartz sync -m "daily sync: {names}"',
            shell=True, cwd=REPO, capture_output=True, text=True,
        )
        print(result.stdout[-2000:])
        if result.returncode != 0:
            print(result.stderr[-2000:])
            sys.exit("ERROR: quartz sync failed — notes are written locally but not published.")
        print("Published.")
    elif not created:
        print("Nothing new to publish.")


if __name__ == "__main__":
    main()
