#!/usr/bin/env python3
"""Validate that CHANGELOG.md contains an entry for a given version.

This script reads CHANGELOG.md from the current directory (or a specified path)
and checks whether a version header exists for the requested version number.
If the entry is found, the script prints the extracted section and exits with
code 0. If the entry is missing, the script prints an error message with fix
instructions and exits with code 1.

Usage:
    python3 eia_validate_changelog.py <version> [--changelog <path>]

Examples:
    python3 eia_validate_changelog.py 1.2.3
    python3 eia_validate_changelog.py 2.0.0 --changelog docs/CHANGELOG.md
    python3 eia_validate_changelog.py 1.0.0-beta.1

Supported changelog formats:
    - Keep a Changelog: ## [1.2.3] - 2025-02-05
    - Simple headers:   ## 1.2.3 - Release Title
    - Bracketed:        ## [1.2.3]
    - Bare:             ## 1.2.3
    - git-cliff output: ## [1.2.3] - 2025-02-05 (same as Keep a Changelog)

Exit codes:
    0 - Version entry found and extracted successfully
    1 - Version entry missing or changelog file not found
"""

import argparse
import re
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace with 'version' and 'changelog' attributes.
    """
    parser = argparse.ArgumentParser(
        description="Validate that CHANGELOG.md has an entry for a given version.",
        epilog="Exit code 0 means the entry was found. Exit code 1 means it was missing.",
    )
    parser.add_argument(
        "version",
        help="The version number to search for (e.g., 1.2.3 or 2.0.0-beta.1). "
        "Do not include the 'v' prefix.",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to the changelog file (default: CHANGELOG.md in current directory).",
    )
    return parser.parse_args()


def normalize_version(version: str) -> str:
    """Remove a leading 'v' or 'V' prefix from the version string if present.

    Args:
        version: The version string, possibly with a 'v' prefix.

    Returns:
        The version string without the 'v' prefix.

    Example:
        >>> normalize_version("v1.2.3")
        '1.2.3'
        >>> normalize_version("1.2.3")
        '1.2.3'
    """
    if version.startswith(("v", "V")):
        return version[1:]
    return version


def build_version_pattern(version: str) -> re.Pattern:
    """Build a compiled regular expression that matches a version header line.

    The pattern matches any of these changelog header formats:
        ## 1.2.3
        ## 1.2.3 - Title
        ## [1.2.3]
        ## [1.2.3] - 2025-02-05
        ## [1.2.3] - Title (2025-02-05)

    The version is escaped so that dots and hyphens in the version string
    are treated as literal characters, not regex metacharacters.

    Args:
        version: The bare version string (without 'v' prefix).

    Returns:
        A compiled regex pattern for matching the version header.
    """
    escaped = re.escape(version)
    # Match "## " followed by optional "[", the version, optional "]",
    # then optional whitespace and anything else (title, date, etc.)
    pattern = rf"^##\s+\[?{escaped}\]?(\s|$)"
    return re.compile(pattern)


def find_version_section(lines: list[str], version: str) -> tuple[int, int] | None:
    """Find the start and end line indices of the version section.

    Searches for the version header and captures all content lines until
    the next level-2 header ("## ") or a horizontal rule ("---") is
    encountered, or the file ends.

    Args:
        lines: All lines of the changelog file.
        version: The bare version string to search for.

    Returns:
        A tuple of (start_index, end_index) where start_index is the line
        after the header and end_index is the line before the next section.
        Returns None if the version header is not found.
    """
    pattern = build_version_pattern(version)
    header_index = None

    # Find the header line
    for i, line in enumerate(lines):
        if pattern.match(line.strip()):
            header_index = i
            break

    if header_index is None:
        return None

    # Find the end of the section (next "## " header or "---" separator)
    content_start = header_index + 1
    content_end = len(lines)

    for i in range(content_start, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## ") or stripped == "---":
            content_end = i
            break

    return (content_start, content_end)


def extract_section_content(lines: list[str], start: int, end: int) -> str:
    """Extract and clean the content between start and end indices.

    Removes leading and trailing blank lines from the extracted section.

    Args:
        lines: All lines of the changelog file.
        start: The first line index to include (inclusive).
        end: The last line index to include (exclusive).

    Returns:
        The extracted section content as a string, with leading and trailing
        blank lines removed.
    """
    section_lines = lines[start:end]

    # Strip leading blank lines
    while section_lines and not section_lines[0].strip():
        section_lines.pop(0)

    # Strip trailing blank lines
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()

    return "\n".join(section_lines)


def print_success(version: str, content: str) -> None:
    """Print the extracted changelog section with formatting.

    Args:
        version: The version number that was found.
        content: The extracted changelog content.
    """
    print(f"Changelog entry found for version {version}")
    print()
    print("--- Extracted Release Notes ---")
    print(content)
    print("--- End Release Notes ---")


def print_failure(version: str, changelog_path: str) -> None:
    """Print an error message with fix instructions.

    Args:
        version: The version number that was not found.
        changelog_path: The path to the changelog file that was searched.
    """
    print("ERROR: CHANGELOG VALIDATION FAILED", file=sys.stderr)
    print(file=sys.stderr)
    print(
        f"  Version {version} was not found in {changelog_path}.",
        file=sys.stderr,
    )
    print(file=sys.stderr)
    print(
        f"  Before releasing, add an entry to {changelog_path} with this format:",
        file=sys.stderr,
    )
    print(file=sys.stderr)
    print(f"    ## {version} - Your Release Title", file=sys.stderr)
    print(file=sys.stderr)
    print("    ### Features", file=sys.stderr)
    print("    - Description of new feature", file=sys.stderr)
    print(file=sys.stderr)
    print("    ### Bug Fixes", file=sys.stderr)
    print("    - Description of bug fix", file=sys.stderr)
    print(file=sys.stderr)
    print(
        f"  Then commit and push the updated {changelog_path}.",
        file=sys.stderr,
    )


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 if the version entry was found, 1 if missing.
    """
    args = parse_arguments()
    version = normalize_version(args.version)
    changelog_path = Path(args.changelog)

    # Check that the changelog file exists
    if not changelog_path.is_file():
        print(
            f"ERROR: {changelog_path} not found.",
            file=sys.stderr,
        )
        print(
            f"  Create {changelog_path} with at least one version entry.",
            file=sys.stderr,
        )
        return 1

    # Read the changelog file
    try:
        content = changelog_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not read {changelog_path}: {exc}", file=sys.stderr)
        return 1

    lines = content.splitlines()

    # Search for the version section
    section = find_version_section(lines, version)

    if section is None:
        print_failure(version, str(changelog_path))
        return 1

    start, end = section
    section_content = extract_section_content(lines, start, end)

    if not section_content.strip():
        print(
            f"WARNING: Version {version} header found but the section is empty.",
            file=sys.stderr,
        )
        print(
            f"  Add at least one line of content under the ## {version} header.",
            file=sys.stderr,
        )
        return 1

    print_success(version, section_content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
