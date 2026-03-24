#!/usr/bin/env python3
"""
generate_userstories.py

Scans a directory for document files (.txt, .md), extracts sentences or
paragraphs that describe requirements, and writes them as structured user
stories in Markdown format.

Usage:
    python3 generate_userstories.py [--input <docs_dir>] [--output <output_file>]

Defaults:
    --input   ./docs
    --output  ./user_stories.md
"""

import argparse
import os
import re
import sys
from datetime import date


SUPPORTED_EXTENSIONS = {".txt", ".md"}

# Patterns that suggest a requirement / user story seed
REQUIREMENT_PATTERNS = [
    re.compile(r"\bals\s+(gebruiker|beheerder|eigenaar|klant|admin|manager)\b", re.IGNORECASE),  # Dutch role: "als gebruiker"
    re.compile(r"\bwil\s+ik\b", re.IGNORECASE),          # Dutch: "wil ik"
    re.compile(r"\bzodat\b", re.IGNORECASE),              # Dutch: "zodat"
    re.compile(r"\bas\s+a\b", re.IGNORECASE),             # English: "as a user"
    re.compile(r"\bi\s+want\b", re.IGNORECASE),           # English: "I want to"
    re.compile(r"\bso\s+that\b", re.IGNORECASE),          # English: "so that"
    re.compile(r"\bmust\b|\bshould\b|\bshall\b", re.IGNORECASE),
]

# Minimum character length for a line to be considered a user story candidate
MIN_REQUIREMENT_LINE_LENGTH = 10


def is_requirement_line(line: str) -> bool:
    """Return True if the line looks like a requirement or user story seed."""
    return any(p.search(line) for p in REQUIREMENT_PATTERNS)


def collect_documents(docs_dir: str) -> list[tuple[str, str]]:
    """Return a list of (filename, content) for all supported documents."""
    documents = []
    if not os.path.isdir(docs_dir):
        print(f"[WARNING] Input directory '{docs_dir}' does not exist. No documents loaded.")
        return documents

    for root, _, files in os.walk(docs_dir):
        for fname in sorted(files):
            _, ext = os.path.splitext(fname)
            if ext.lower() in SUPPORTED_EXTENSIONS:
                fpath = os.path.join(root, fname)
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    documents.append((fpath, fh.read()))

    return documents


def extract_stories(content: str) -> list[str]:
    """Extract candidate user story lines from document content."""
    stories = []
    for line in content.splitlines():
        line = line.strip()
        if len(line) < MIN_REQUIREMENT_LINE_LENGTH:
            continue
        if is_requirement_line(line):
            stories.append(line)
    return stories


def format_story(index: int, raw: str) -> str:
    """Format a single raw story line as a Markdown user story entry."""
    return f"{index}. **User Story {index}**: {raw}"


def write_output(output_file: str, stories_by_source: dict[str, list[str]]) -> int:
    """Write all user stories to the output Markdown file. Returns total story count."""
    total = 0
    counter = 1

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(f"# User Stories\n\n")
        fh.write(f"_Gegenereerd op {date.today().isoformat()}_\n\n")

        if not stories_by_source:
            fh.write("_Geen documenten gevonden in de invoermap._\n")
            return 0

        all_empty = all(len(s) == 0 for s in stories_by_source.values())
        if all_empty:
            fh.write("_Geen user stories gevonden in de aangeleverde documenten._\n")
            return 0

        for source, stories in stories_by_source.items():
            if not stories:
                continue
            fh.write(f"## Bron: `{os.path.basename(source)}`\n\n")
            for raw in stories:
                fh.write(format_story(counter, raw) + "\n")
                counter += 1
                total += 1
            fh.write("\n")

    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verwerk documenten en genereer user stories in Markdown."
    )
    parser.add_argument(
        "--input",
        default="docs",
        metavar="DIR",
        help="Map met bronbestanden (standaard: ./docs)",
    )
    parser.add_argument(
        "--output",
        default="user_stories.md",
        metavar="FILE",
        help="Uitvoerbestand voor user stories (standaard: ./user_stories.md)",
    )
    args = parser.parse_args(argv)

    print(f"[INFO] Invoermap  : {args.input}")
    print(f"[INFO] Uitvoer    : {args.output}")

    documents = collect_documents(args.input)
    print(f"[INFO] Documenten gevonden: {len(documents)}")

    stories_by_source: dict[str, list[str]] = {}
    for fpath, content in documents:
        stories = extract_stories(content)
        stories_by_source[fpath] = stories
        print(f"[INFO]   {fpath}: {len(stories)} user stor{'y' if len(stories) == 1 else 'ies'} gevonden")

    total = write_output(args.output, stories_by_source)
    print(f"[INFO] Totaal {total} user stor{'y' if total == 1 else 'ies'} geschreven naar '{args.output}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
