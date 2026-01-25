#!/usr/bin/env python3
"""Port status reporting tool for worktree port allocations."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import (  # type: ignore[import-not-found]  # noqa: E402
    file_lock,
    get_atlas_dir,
    is_port_available,
)


def check_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is actually in use by attempting to connect."""
    return not is_port_available(port, host)


def load_port_allocations() -> dict[str, Any]:
    """Load port allocations from the registry file."""
    registry_file = get_atlas_dir() / "worktrees" / ".port_registry.json"

    with file_lock(registry_file):
        if not registry_file.exists():
            return {"allocations": []}

        try:
            with open(registry_file, "r") as f:
                return cast(dict[str, Any], json.load(f))
        except Exception as e:
            print(f"Error loading port registry: {e}", file=sys.stderr)
            return {"allocations": []}


def filter_allocations(
    allocations: list[dict[str, Any]],
    worktree: str | None = None,
    service: str | None = None,
) -> list[dict[str, Any]]:
    """Filter allocations based on criteria."""
    filtered = allocations

    if worktree:
        filtered = [a for a in filtered if a.get("worktree") == worktree]

    if service:
        filtered = [a for a in filtered if a.get("service") == service]

    return filtered


def format_table(allocations: list[dict[str, Any]], health_check: bool = False) -> str:
    """Format allocations as a table with Unicode borders."""
    if not allocations:
        return "No port allocations found."

    lines = ["Port Allocations:"]

    if health_check:
        lines.append("┌──────┬─────────────┬─────────┬────────────────────┬────────┐")
        lines.append("│ Port │ Worktree    │ Service │ Allocated          │ In Use │")
        lines.append("├──────┼─────────────┼─────────┼────────────────────┼────────┤")
    else:
        lines.append("┌──────┬─────────────┬─────────┬────────────────────┐")
        lines.append("│ Port │ Worktree    │ Service │ Allocated          │")
        lines.append("├──────┼─────────────┼─────────┼────────────────────┤")

    # Sort by port number for consistent display
    sorted_allocs = sorted(allocations, key=lambda x: x.get("port", 0))

    for alloc in sorted_allocs:
        port = str(alloc.get("port", "")).ljust(4)
        worktree = str(alloc.get("worktree", ""))[:12].ljust(11)
        service = str(alloc.get("service", ""))[:8].ljust(7)
        allocated = str(alloc.get("allocated", ""))[:18].ljust(18)

        if health_check:
            port_val = alloc.get("port")
            in_use = (
                "Yes"
                if port_val is not None and check_port_in_use(int(port_val))
                else "No"
            )
            in_use = in_use.ljust(6)
            lines.append(f"│ {port} │ {worktree} │ {service} │ {allocated} │ {in_use}│")
        else:
            lines.append(f"│ {port} │ {worktree} │ {service} │ {allocated} │")

    if health_check:
        lines.append("└──────┴─────────────┴─────────┴────────────────────┴────────┘")
    else:
        lines.append("└──────┴─────────────┴─────────┴────────────────────┘")

    return "\n".join(lines)


def format_summary(
    allocations: list[dict[str, Any]], health_check: bool = False
) -> str:
    """Format summary statistics."""
    total = len(allocations)

    if total == 0:
        return "\nSummary: No allocations"

    worktrees = len(set(a.get("worktree") for a in allocations))
    services = len(set(a.get("service") for a in allocations))

    summary = [
        "\nSummary:",
        f"  Total allocations: {total}",
        f"  Unique worktrees: {worktrees}",
        f"  Unique services: {services}",
    ]

    if health_check:
        in_use_count = sum(
            1
            for a in allocations
            if a.get("port") is not None and check_port_in_use(int(a["port"]))
        )
        summary.append(f"  Ports in use: {in_use_count}/{total}")

    return "\n".join(summary)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Port status reporting tool for worktree port allocations"
    )
    parser.add_argument("--all", action="store_true", help="Show all allocated ports")
    parser.add_argument("--worktree", type=str, help="Filter by worktree ID")
    parser.add_argument("--service", type=str, help="Filter by service type")
    parser.add_argument(
        "--health-check", action="store_true", help="Check if ports are actually in use"
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Load allocations
    data = load_port_allocations()
    raw_allocations: list[dict[str, Any]] = data.get("allocations", [])
    allocations: list[dict[str, Any]] = raw_allocations

    # Filter allocations
    filtered = filter_allocations(
        allocations, worktree=args.worktree, service=args.service
    )

    # Output
    if args.json:
        output: dict[str, Any] = {
            "allocations": filtered,
            "total": len(filtered),
        }
        if args.health_check:
            output_allocs: list[dict[str, Any]] = output["allocations"]
            for alloc in output_allocs:
                port_val = alloc.get("port")
                alloc["in_use"] = port_val is not None and check_port_in_use(
                    int(port_val)
                )
        print(json.dumps(output, indent=2))
    else:
        print(format_table(filtered, health_check=args.health_check))
        print(format_summary(filtered, health_check=args.health_check))

    return 0


if __name__ == "__main__":
    sys.exit(main())
