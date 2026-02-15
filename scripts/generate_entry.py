"""
Generate a daily Sefiathan entry using the Anthropic API and save it as a chapter.

Usage:
    python scripts/generate_entry.py

Environment variables required:
    ANTHROPIC_API_KEY - Your Anthropic API key
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic


def generate_entry() -> str:
    """Generate today's Sefiathan entry via Claude."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Today is {today} (day {day_of_year} of the year). "
                    "Write a short, reflective daily Sefiathan entry — a personal horoscope-style "
                    "passage that blends astrology, introspection, and poetic memoir. "
                    "It should feel like a journal entry from the universe addressed to the reader. "
                    "Keep it between 100-300 words. "
                    "Start with a title line using the date, then the entry body. "
                    "No markdown headers — just the date as a bold line, then flowing prose."
                ),
            }
        ],
    )

    return message.content[0].text


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path("chapters")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{today}.md"

    if output_path.exists():
        print(f"Entry for {today} already exists. Skipping.")
        sys.exit(0)

    print(f"Generating Sefiathan entry for {today}...")
    entry = generate_entry()

    output_path.write_text(entry, encoding="utf-8")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
