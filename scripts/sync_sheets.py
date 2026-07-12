"""sync_sheets.py — render public Google Sheets as Quartz table pages.

This is Spider-Verse's "spreadsheet support". For each sheet listed in SHEETS below,
it pulls the sheet as CSV (no login needed — the sheet must be shared
"anyone with the link -> viewer"), renders it into a markdown table page under
content/, and then publishes the site with `npx quartz sync`.

Design mirrors daily_sync.py: plain urllib for fetching, no external deps, no AI.

Safety / ownership:
  - The pages listed here are GENERATED and script-owned: they are OVERWRITTEN on
    every run. Never hand-edit them — edit the source sheet instead. This script
    only ever writes the exact target paths in SHEETS; every other file under
    content/ is left untouched.

Usage:
  python sync_sheets.py            # render every sheet, then publish
  python sync_sheets.py --no-sync  # render but skip the git publish
"""

import argparse
import csv
import datetime as dt
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"

# The tracker sheet's id is owned by the job-digest project, which records it here
# after creating the public sheet. We read it from there so the two stay in sync.
JOB_DIGEST_SHEET_STATE = Path(r"C:\Users\dhruv\job-digest\data\sheet_state.json")

# One entry per sheet to publish. Add more to render other spreadsheets on the site.
#   sheet_id       : the Google Sheet id (or use sheet_id_from to read it from a file)
#   sheet_id_from  : path to a JSON file holding {"spreadsheet_id": "..."}
#   target         : page path under content/, without the .md extension
#   title          : page title (frontmatter + H1)
#   columns        : optional whitelist of header names to show, in this order.
#                    Omit to render every column the sheet has.
SHEETS = [
    {
        "sheet_id_from": JOB_DIGEST_SHEET_STATE,
        "target": "Career-and-Money/Job-Applications",
        "title": "Job Applications",
        "columns": ["Company", "Role", "Applied on", "Status", "URL"],
    },
]


def resolve_sheet_id(entry: dict) -> str:
    """Return the sheet id for one entry, from sheet_id or a sheet_id_from file."""
    if entry.get("sheet_id"):
        return entry["sheet_id"]
    ref = entry.get("sheet_id_from")
    if ref and Path(ref).exists():
        state = json.loads(Path(ref).read_text(encoding="utf-8") or "{}")
        return state.get("spreadsheet_id", "")
    return ""


def fetch_csv(sheet_id: str) -> list[list[str]]:
    """Download a public sheet as CSV and parse it into rows. Raises on failure."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (sync-sheets)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    # A private sheet hands back an HTML login page instead of CSV — catch that early
    # so we fail with a clear message rather than rendering a junk table.
    if "accounts.google.com" in body[:2000] or body[:200].lstrip().lower().startswith("<!doctype"):
        raise ValueError("sheet is not public — share it 'Anyone with the link -> Viewer'")
    return list(csv.reader(body.splitlines()))


def _cell(value: str) -> str:
    """Make one cell safe for a markdown table and auto-link bare URLs."""
    text = value.replace("\r", " ").replace("\n", " ").strip()
    if text.startswith("http://") or text.startswith("https://"):
        return f"[link]({text})"
    return text.replace("|", "\\|")  # a literal | would break the table


def _select_columns(header: list[str], columns: list[str] | None):
    """Return the indexes of the columns to render, in display order."""
    if not columns:
        return list(range(len(header)))
    lookup = {h.strip().lower(): i for i, h in enumerate(header)}
    return [lookup[c.lower()] for c in columns if c.lower() in lookup]


def summary_line(header: list[str], data_rows: list[list[str]]) -> str:
    """A one-line count, plus a per-Status breakdown when a Status column exists."""
    total = len(data_rows)
    noun = "application" if total == 1 else "applications"
    parts = [f"**{total} {noun}**"]
    status_idx = next((i for i, h in enumerate(header) if h.strip().lower() == "status"), None)
    if status_idx is not None:
        counts: dict[str, int] = {}
        for row in data_rows:
            val = (row[status_idx] if status_idx < len(row) else "").strip() or "—"
            counts[val] = counts.get(val, 0) + 1
        breakdown = " · ".join(f"{n} {name}" for name, n in sorted(counts.items()))
        if breakdown:
            parts.append(breakdown)
    return " · ".join(parts)


def render_page(entry: dict, rows: list[list[str]]) -> str:
    """Render one sheet's rows into a full markdown page (frontmatter + table)."""
    title = entry["title"]
    today = dt.date.today().isoformat()

    if not rows:
        header, data_rows, cols = [], [], []
    else:
        header, data_rows = rows[0], rows[1:]
        cols = _select_columns(header, entry.get("columns"))

    out = [
        "---",
        f"title: {title}",
        "---",
        "",
        "<!-- GENERATED by scripts/sync_sheets.py — do not hand-edit. Edit the source sheet. -->",
        f"*Auto-generated from the tracker sheet · last updated {today}. "
        "Edit the sheet, not this page.*",
        "",
    ]

    if not data_rows:
        out.append("_No entries yet._")
        return "\n".join(out).rstrip() + "\n"

    out += [summary_line(header, data_rows), ""]
    # Table header + separator, then one row per record, projected to chosen columns.
    out.append("| " + " | ".join(_cell(header[i]) for i in cols) + " |")
    out.append("| " + " | ".join("---" for _ in cols) + " |")
    for row in data_rows:
        cells = [_cell(row[i]) if i < len(row) else "" for i in cols]
        out.append("| " + " | ".join(cells) + " |")

    return "\n".join(out).rstrip() + "\n"


def _strip_timestamp(text: str) -> str:
    """Drop the 'last updated ...' line so we can tell real changes from a new date.
    Without this the page would differ every single day and force an empty commit."""
    return "\n".join(
        ln for ln in text.splitlines()
        if not ln.startswith("*Auto-generated from the tracker sheet")
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sync", action="store_true", help="write pages but skip publish")
    args = ap.parse_args()

    written, unchanged, errors = [], [], []
    for entry in SHEETS:
        target = (CONTENT / (entry["target"] + ".md"))
        sheet_id = resolve_sheet_id(entry)
        if not sheet_id:
            errors.append((entry["target"], "no sheet id (has job-digest created the public sheet yet?)"))
            continue
        try:
            rows = fetch_csv(sheet_id)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as exc:
            errors.append((entry["target"], f"could not read sheet: {exc}"))
            continue

        new_text = render_page(entry, rows)
        # Skip the write when only the date would change — keeps git history clean.
        if target.exists() and _strip_timestamp(target.read_text(encoding="utf-8")) == _strip_timestamp(new_text):
            unchanged.append(target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_text, encoding="utf-8", newline="\n")
        written.append(target)

    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{stamp}] rendered: {len(written)}, unchanged: {len(unchanged)}, errors: {len(errors)}")
    for path in written:
        print(f"  + {path}")
    for path in unchanged:
        print(f"  = {path} (no change)")
    for tgt, why in errors:
        print(f"  ! {tgt}: {why}")

    if written and not args.no_sync:
        result = subprocess.run(
            'npx quartz sync -m "sync job tracker sheet"',
            shell=True, cwd=REPO, capture_output=True, text=True,
        )
        print(result.stdout[-2000:])
        if result.returncode != 0:
            print(result.stderr[-2000:])
            sys.exit("ERROR: quartz sync failed — pages written locally but not published.")
        print("Published.")
    elif not written:
        print("Nothing rendered — nothing to publish.")


if __name__ == "__main__":
    main()
