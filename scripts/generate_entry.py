"""
Read a Co-Star screenshot and generate a daily Sefiathan entry using Claude vision.

Usage:
    python scripts/generate_entry.py screenshots/2026-02-15.png

Environment variables required:
    ANTHROPIC_API_KEY - Your Anthropic API key
"""

import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic


def read_screenshot(image_path: str) -> str:
    """Encode the screenshot as base64."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def generate_entry(image_path: str) -> str:
    """Generate today's Sefiathan entry from a Co-Star screenshot via Claude vision."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday

    image_data = read_screenshot(image_path)

    # Determine media type from extension
    ext = Path(image_path).suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(ext, "image/png")

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
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
                            f"Today is {today} (day {day_of_year} of the year). "
                            "This is a screenshot from the Co-Star astrology app. "
                            "Read the horoscope content in this screenshot and transform it into "
                            "a short, reflective Sefiathan entry — a personal horoscope-style "
                            "passage that blends the Co-Star reading with introspection and poetic memoir. "
                            "It should feel like a journal entry from the universe addressed to the reader. "
                            "Weave in the specific astrological details and advice from the screenshot. "
                            "Keep it between 100-300 words. "
                            "Start with a bold date line, then the entry body. "
                            "No markdown headers — just the date as a bold line, then flowing prose."
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

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path("chapters")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{today}.md"

    if output_path.exists():
        print(f"Entry for {today} already exists. Skipping.")
        sys.exit(0)

    print(f"Generating Sefiathan entry from {image_path}...")
    entry = generate_entry(image_path)

    output_path.write_text(entry, encoding="utf-8")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
