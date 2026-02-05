#!/usr/bin/env python3
"""
worktree_list.py - List worktrees from EIA registry

Lists all worktrees registered in the EIA worktree registry with filtering,
validation, and formatting options.

Usage:
    python worktree_list.py                          # List all worktrees (table format)
    python worktree_list.py --purpose review         # Filter by purpose
    python worktree_list.py --status active          # Filter by status
    python worktree_list.py --ports                  # Show port allocations
    python worktree_list.py --json                   # JSON output
    python worktree_list.py --validate               # Validate against git worktree list
    python worktree_list.py --purpose review --json  # Combine filters
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
# ruff: noqa: E402
from cross_platform import file_lock  # type: ignore[import-not-found]
from cross_platform import get_atlas_dir
from cross_platform import git_worktree_list


# ANSI color codes for pretty output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


def get_registry_path() -> Path:
    """
    Get the path to the worktree registry file.

    Returns:
        Path to design/worktrees/registry.json
    """
    return cast(Path, get_atlas_dir()) / "worktrees" / "registry.json"


def load_registry() -> dict[str, Any]:
    """
    Load the worktree registry from disk.

    Returns:
        Registry dictionary with 'worktrees', 'port_ranges', 'naming_convention'

    Raises:
        FileNotFoundError: If registry file doesn't exist
        json.JSONDecodeError: If registry file is corrupted
    """
    registry_path = get_registry_path()

    with file_lock(registry_path):
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Registry not found at {registry_path}\n"
                f"Run worktree_create.py to create your first worktree."
            )

        with open(registry_path, "r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))


def get_git_worktrees() -> list[dict[str, str]]:
    """
    Get list of worktrees from git.

    Returns:
        List of dicts with 'worktree' and 'branch' keys
    """
    try:
        git_wts = git_worktree_list()
        return [
            {
                "worktree": str(wt.get("path", "")),
                "branch": wt.get("branch", "").replace("refs/heads/", ""),
            }
            for wt in git_wts
        ]
    except Exception:
        return []


def validate_against_git(worktrees: list[dict[str, Any]]) -> dict[str, list[str]]:
    """
    Validate registry worktrees against actual git worktrees.

    Args:
        worktrees: List of worktree entries from registry

    Returns:
        Dict with 'missing', 'orphaned', and 'valid' lists of worktree IDs
    """
    git_wts = get_git_worktrees()
    git_paths = {os.path.abspath(wt["worktree"]) for wt in git_wts}

    validation: dict[str, list[str]] = {
        "valid": [],
        "missing": [],  # In registry but not in git
        "orphaned": [],  # In git but not in registry
    }

    registry_paths: set[str] = set()

    for wt in worktrees:
        abs_path = os.path.abspath(wt["path"])
        registry_paths.add(abs_path)

        if abs_path in git_paths:
            validation["valid"].append(wt["id"])
        else:
            validation["missing"].append(wt["id"])

    # Check for orphaned git worktrees
    for git_path in git_paths:
        if git_path not in registry_paths:
            validation["orphaned"].append(git_path)

    return validation


def filter_worktrees(
    worktrees: list[dict[str, Any]],
    purpose: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """
    Filter worktrees by purpose and/or status.

    Args:
        worktrees: List of worktree entries
        purpose: Filter by purpose (review, feature, bugfix, test, hotfix, refactor)
        status: Filter by status (active, locked, pending-removal)

    Returns:
        Filtered list of worktree entries
    """
    filtered = worktrees

    if purpose:
        filtered = [wt for wt in filtered if wt.get("purpose") == purpose]

    if status:
        filtered = [wt for wt in filtered if wt.get("status") == status]

    return filtered


def format_table(
    worktrees: list[dict[str, Any]],
    show_ports: bool = False,
    validation: dict[str, list[str]] | None = None,
) -> str:
    """
    Format worktrees as a pretty table.

    Args:
        worktrees: List of worktree entries
        show_ports: Whether to include port allocations column
        validation: Validation results from validate_against_git

    Returns:
        Formatted table string
    """
    if not worktrees:
        return f"{Colors.YELLOW}No worktrees found.{Colors.RESET}\n"

    # Calculate column widths
    id_width = max(len(wt.get("id", "")) for wt in worktrees)
    id_width = max(id_width, len("ID"))

    branch_width = max(len(wt.get("branch", "")) for wt in worktrees)
    branch_width = max(branch_width, len("BRANCH"))

    purpose_width = max(len(wt.get("purpose", "")) for wt in worktrees)
    purpose_width = max(purpose_width, len("PURPOSE"))

    status_width = max(len(wt.get("status", "")) for wt in worktrees)
    status_width = max(status_width, len("STATUS"))

    # Build header
    header_parts = [
        f"{'ID':<{id_width}}",
        f"{'BRANCH':<{branch_width}}",
        f"{'PURPOSE':<{purpose_width}}",
        f"{'STATUS':<{status_width}}",
        f"{'ISSUE':<10}",
        f"{'CREATED':<11}",
    ]

    if show_ports:
        header_parts.append(f"{'PORTS':<20}")

    if validation:
        header_parts.append(f"{'VALID':<6}")

    header = "  ".join(header_parts)
    separator = "\u2550" * len(header)

    # Build rows
    lines = [f"{Colors.BOLD}{header}{Colors.RESET}", separator]

    for wt in worktrees:
        wt_id = wt.get("id", "")
        branch = wt.get("branch", "")
        purpose = wt.get("purpose", "")
        status = wt.get("status", "")
        issue = wt.get("issue") or "-"
        created = wt.get("created", "")

        # Format creation date
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                created_str = dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                created_str = created[:10] if len(created) >= 10 else created
        else:
            created_str = "-"

        # Color status
        status_colored = status
        if status == "active":
            status_colored = f"{Colors.GREEN}{status}{Colors.RESET}"
        elif status == "locked":
            status_colored = f"{Colors.YELLOW}{status}{Colors.RESET}"
        elif status == "pending-removal":
            status_colored = f"{Colors.RED}{status}{Colors.RESET}"

        # Color purpose
        purpose_colored = purpose
        if purpose == "review":
            purpose_colored = f"{Colors.CYAN}{purpose}{Colors.RESET}"
        elif purpose == "feature":
            purpose_colored = f"{Colors.BLUE}{purpose}{Colors.RESET}"
        elif purpose == "bugfix":
            purpose_colored = f"{Colors.MAGENTA}{purpose}{Colors.RESET}"
        elif purpose == "test":
            purpose_colored = f"{Colors.GRAY}{purpose}{Colors.RESET}"

        row_parts = [
            f"{wt_id:<{id_width}}",
            f"{branch:<{branch_width}}",
            f"{purpose_colored:<{purpose_width + 9}}",  # +9 for ANSI codes
            f"{status_colored:<{status_width + 9}}",  # +9 for ANSI codes
            f"{issue:<10}",
            f"{created_str:<11}",
        ]

        if show_ports:
            ports = wt.get("port_allocations", [])
            ports_str = ", ".join(map(str, ports)) if ports else "-"
            row_parts.append(f"{ports_str:<20}")

        if validation:
            is_valid = wt_id in validation["valid"]
            valid_str = (
                f"{Colors.GREEN}\u2713{Colors.RESET}"
                if is_valid
                else f"{Colors.RED}\u2717{Colors.RESET}"
            )
            row_parts.append(f"{valid_str:<6}")

        lines.append("  ".join(row_parts))

    return "\n".join(lines) + "\n"


def format_json(worktrees: list[dict[str, Any]]) -> str:
    """
    Format worktrees as JSON.

    Args:
        worktrees: List of worktree entries

    Returns:
        JSON string
    """
    return json.dumps(worktrees, indent=2)


def print_validation_summary(validation: dict[str, list[str]]) -> None:
    """
    Print validation summary.

    Args:
        validation: Validation results from validate_against_git
    """
    print(f"\n{Colors.BOLD}Validation Summary:{Colors.RESET}")
    print(f"  {Colors.GREEN}Valid:{Colors.RESET} {len(validation['valid'])}")
    print(
        f"  {Colors.RED}Missing (in registry, not in git):{Colors.RESET} "
        f"{len(validation['missing'])}"
    )
    print(
        f"  {Colors.YELLOW}Orphaned (in git, not in registry):{Colors.RESET} "
        f"{len(validation['orphaned'])}"
    )

    if validation["missing"]:
        print(f"\n{Colors.RED}Missing worktrees:{Colors.RESET}")
        for wt_id in validation["missing"]:
            print(f"  - {wt_id}")

    if validation["orphaned"]:
        print(f"\n{Colors.YELLOW}Orphaned worktrees:{Colors.RESET}")
        for path in validation["orphaned"]:
            print(f"  - {path}")


def main() -> None:
    """Main entry point for worktree_list.py."""
    parser = argparse.ArgumentParser(
        description="List worktrees from EIA registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          List all worktrees (table format)
  %(prog)s --purpose review         Filter by purpose
  %(prog)s --status active          Filter by status
  %(prog)s --ports                  Show port allocations
  %(prog)s --json                   JSON output
  %(prog)s --validate               Validate against git worktree list
  %(prog)s --purpose review --json  Combine filters

Purpose values: review, feature, bugfix, test, hotfix, refactor
Status values: active, locked, pending-removal
        """,
    )

    parser.add_argument(
        "--purpose",
        choices=["review", "feature", "bugfix", "test", "hotfix", "refactor"],
        help="Filter by purpose",
    )

    parser.add_argument(
        "--status",
        choices=["active", "locked", "pending-removal"],
        help="Filter by status",
    )

    parser.add_argument(
        "--ports",
        action="store_true",
        help="Show port allocations in table",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate against git worktree list",
    )

    args = parser.parse_args()

    try:
        # Load registry
        registry = load_registry()
        worktrees: list[dict[str, Any]] = registry.get("worktrees", [])

        # Filter worktrees
        filtered = filter_worktrees(worktrees, args.purpose, args.status)

        # Validate if requested
        validation: dict[str, list[str]] | None = None
        if args.validate:
            validation = validate_against_git(worktrees)

        # Output
        if args.json:
            print(format_json(filtered))
        else:
            print(format_table(filtered, args.ports, validation))

        # Print validation summary if requested
        if args.validate and not args.json and validation is not None:
            print_validation_summary(validation)

        # Exit with appropriate code
        if args.validate and validation is not None:
            if validation["missing"] or validation["orphaned"]:
                sys.exit(1)  # Validation failed

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"{Colors.RED}Error:{Colors.RESET} {e}", file=sys.stderr)
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(
            f"{Colors.RED}Error:{Colors.RESET} Registry file is corrupted: {e}",
            file=sys.stderr,
        )
        print(f"Registry path: {get_registry_path()}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"{Colors.RED}Unexpected error:{Colors.RESET} {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
