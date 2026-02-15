"""
Split the existing chronicle files into individual chapter files.
Reads the large chronicle, Day 26-35 file, and Days 36-38 file,
and outputs individual chapters/YYYY-MM-DD.md files.
"""

import re
from pathlib import Path

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
}

OUTPUT_DIR = Path("chapters")


def extract_date_from_header(header: str) -> str | None:
    """Try to extract a date from a day header line. Returns YYYY-MM-DD or None."""
    match = re.search(r'(\w+)\s+(\d{1,2}),?\s*(\d{4})', header)
    if match:
        month_str = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        month = MONTHS.get(month_str)
        if month:
            return f"{year}-{month:02d}-{day:02d}"
    return None


def extract_day_number(header: str) -> int | None:
    """Extract the day number from a header."""
    match = re.search(r'[Dd]ay\s+(\d+)', header)
    if match:
        return int(match.group(1))
    return None


def day_number_to_date(day_num: int) -> str:
    """Convert a day number to a date string. Day 1 = Jan 1, 2026."""
    from datetime import date, timedelta
    base = date(2026, 1, 1)
    target = base + timedelta(days=day_num - 1)
    return target.strftime("%Y-%m-%d")


def clean_text(text: str) -> str:
    """Pre-clean text: insert newlines before smushed day headers."""
    # Handle smushed patterns like "certain.day 27Jan 30Day 27 - January 27, 2026"
    # Insert a newline before lowercase "day \d+" when preceded by text
    text = re.sub(r'([a-z.])day\s+(\d+)', r'\1\nday \2', text)
    # Insert newline before "Day N" when preceded by text on same line
    text = re.sub(r'([a-z0-9.])Day\s+(\d+)', r'\1\nDay \2', text)
    return text


def split_chronicle(filepath: str) -> dict[str, str]:
    """Split a chronicle file into individual entries. Returns {date: content}."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    text = clean_text(text)
    entries = {}

    # Split on "Day N" headers (capital D) - these are the real entry headers
    # Match "### Day N", "Day N -", "Day N —", "Day N:"
    pattern = r'(?:^|\n)\s*(?:###?\s*)?Day\s+\d+'
    headers = list(re.finditer(pattern, text))

    for i, match in enumerate(headers):
        start = match.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)

        header_line = text[start:start + 200].strip().split('\n')[0]
        content = text[start:end].strip()

        # Remove markdown header prefixes
        content = re.sub(r'^#+\s*', '', content)
        content = content.strip()

        # Remove trailing --- separators and "day N" metadata junk at the end
        content = re.sub(r'\s*-{3,}\s*$', '', content)
        content = re.sub(r'\s*day\s+\d+\w+\s*\d*\s*$', '', content, flags=re.IGNORECASE)
        content = content.rstrip()

        day_num = extract_day_number(header_line)
        date_str = extract_date_from_header(header_line)

        if not date_str and day_num:
            date_str = day_number_to_date(day_num)

        if date_str and content:
            entries[date_str] = content
            print(f"  Found Day {day_num} -> {date_str} ({len(content.split())} words)")

    return entries


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    all_entries = {}
    source_dir = Path(r"C:\Users\sethg\Sefiathan")

    # Process main chronicle (Days 1-25)
    chronicle = source_dir / "sefiathan_chronicle.md"
    if chronicle.exists():
        print(f"Processing {chronicle}...")
        entries = split_chronicle(str(chronicle))
        all_entries.update(entries)
        print(f"  -> {len(entries)} entries\n")

    # Process Day 26-35
    day26_35 = source_dir / "Day 26 - Day 35.txt"
    if day26_35.exists():
        print(f"Processing {day26_35}...")
        entries = split_chronicle(str(day26_35))
        all_entries.update(entries)
        print(f"  -> {len(entries)} entries\n")

    # Process Days 36-38
    day36_38 = source_dir / "sefiathans-journey-days-36-38.md"
    if day36_38.exists():
        print(f"Processing {day36_38}...")
        entries = split_chronicle(str(day36_38))
        all_entries.update(entries)
        print(f"  -> {len(entries)} entries\n")

    # Write individual chapter files
    print(f"\nWriting {len(all_entries)} chapter files...")
    for date_str in sorted(all_entries.keys()):
        output_path = OUTPUT_DIR / f"{date_str}.md"
        output_path.write_text(all_entries[date_str], encoding="utf-8")
        print(f"  {output_path}")

    print(f"\nDone! {len(all_entries)} chapters written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
