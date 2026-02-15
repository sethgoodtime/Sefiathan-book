"""
Read a Co-Star screenshot and generate the next page of Sefiathan's Journey.

Uses the full story bible as a system prompt, the previous day's entry for
continuity, and the Co-Star screenshot as thematic inspiration.

Usage:
    python scripts/generate_entry.py screenshots/2026-02-15.png

Environment variables required:
    ANTHROPIC_API_KEY - Your Anthropic API key
"""

import base64
import sys
import glob
from datetime import datetime, timezone, date
from pathlib import Path

import anthropic

# Day 1 of the story is January 2, 2026
STORY_START = date(2026, 1, 2)


def read_screenshot(image_path: str) -> str:
    """Encode the screenshot as base64."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def load_system_prompt() -> str:
    """Load the story bible / system prompt."""
    prompt_path = Path("prompts/system_prompt.md")
    if not prompt_path.exists():
        print("ERROR: prompts/system_prompt.md not found!")
        sys.exit(1)
    return prompt_path.read_text(encoding="utf-8")


def get_previous_entries(n: int = 3) -> str:
    """Load the last N chapter entries for continuity context."""
    chapter_files = sorted(glob.glob("chapters/*.md"))
    if not chapter_files:
        return ""

    recent = chapter_files[-n:]
    entries = []
    for filepath in recent:
        day_date = Path(filepath).stem
        content = Path(filepath).read_text(encoding="utf-8").strip()
        entries.append(f"--- {day_date} ---\n{content}")

    return "\n\n".join(entries)


def get_story_day(target_date: date | None = None) -> int:
    """Calculate what story day we're on based on the date."""
    d = target_date or date.today()
    delta = (d - STORY_START).days + 1
    return max(1, delta)


def generate_entry(image_path: str, target_date: date | None = None) -> str:
    """Generate a Sefiathan entry from a Co-Star screenshot."""
    d = target_date or date.today()
    today = d.strftime("%Y-%m-%d")
    story_day = get_story_day(d)

    image_data = read_screenshot(image_path)

    ext = Path(image_path).suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(ext, "image/png")

    system_prompt = load_system_prompt()
    previous_entries = get_previous_entries(3)

    continuity_context = ""
    if previous_entries:
        continuity_context = (
            f"\n\n## RECENT ENTRIES (for continuity - flow naturally from where the last entry ended)\n\n"
            f"{previous_entries}"
        )

    full_system = system_prompt + continuity_context

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=3072,
        system=full_system,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Today is {today} — Day {story_day} of Sefiathan's journey.\n\n"
                            "Here is today's Co-Star reading. Extract the core theme and write "
                            "today's page. Flow naturally from where yesterday's entry ended. "
                            "~1200-1500 words. Pure prose, no formatting beyond the bold date line."
                        ),
                    },
                ],
            }
        ],
    )

    return message.content[0].text


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_entry.py <screenshot_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    if not Path(image_path).exists():
        print(f"Screenshot not found: {image_path}")
        sys.exit(1)

    # Derive the target date from the screenshot filename (e.g., 2026-02-08.jpg)
    stem = Path(image_path).stem
    try:
        target_date = date.fromisoformat(stem)
    except ValueError:
        target_date = date.today()

    date_str = target_date.strftime("%Y-%m-%d")
    story_day = get_story_day(target_date)
    output_dir = Path("chapters")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{date_str}.md"

    if output_path.exists():
        print(f"Entry for {date_str} already exists. Skipping.")
        sys.exit(0)

    print(f"Day {story_day} — Generating Sefiathan entry from {image_path}...")
    entry = generate_entry(image_path, target_date)

    output_path.write_text(entry, encoding="utf-8")
    print(f"Saved: {output_path} (Day {story_day}, {len(entry.split())} words)")


if __name__ == "__main__":
    main()
