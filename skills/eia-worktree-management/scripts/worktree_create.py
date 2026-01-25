#!/usr/bin/env python3
"""
Worktree Creation Script
Creates git worktrees with automatic registry and port allocation.

Usage:
    worktree_create.py --purpose review --identifier 123 --branch pr-123
    worktree_create.py --purpose feature --identifier user-auth --branch feature/user-auth --ports
    worktree_create.py --purpose bugfix --identifier issue-456 --branch fix/issue-456
    worktree_create.py --purpose test --identifier e2e-suite --branch main --ports
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import (  # type: ignore[import-not-found]  # noqa: E402
    atomic_write_json,
    file_lock,
    get_atlas_dir,
    is_port_available,
)
from thresholds import WorktreeThresholds  # type: ignore[import-not-found]  # noqa: E402

# Get thresholds instance
THRESHOLDS = WorktreeThresholds()

# Constants
REGISTRY_PATH = get_atlas_dir() / "worktrees" / "registry.json"
DEFAULT_WORKTREE_BASE = Path(".worktrees")
# Port ranges from shared thresholds (converted to dict format for compatibility)
DEFAULT_PORT_RANGES = {
    service: {"start": range_val[0], "end": range_val[1]}
    for service, range_val in THRESHOLDS.PORT_RANGES.items()
}
NAMING_CONVENTION = {
    "review": "review-{identifier}",
    "feature": "feature-{identifier}",
    "bugfix": "bugfix-{identifier}",
    "test": "test-{identifier}",
}


class WorktreeError(Exception):
    """Custom exception for worktree operations."""

    pass


def run_command(
    cmd: list[str], check: bool = True, capture: bool = True
) -> subprocess.CompletedProcess[str]:
    """
    Run shell command with error handling.

    Args:
        cmd: Command and arguments as list
        check: Raise exception on non-zero exit
        capture: Capture stdout/stderr

    Returns:
        CompletedProcess instance

    Raises:
        WorktreeError: If command fails and check=True
    """
    try:
        result = subprocess.run(cmd, check=check, capture_output=capture, text=True)
        return result
    except subprocess.CalledProcessError as e:
        raise WorktreeError(
            f"Command failed: {' '.join(cmd)}\nError: {e.stderr}"
        ) from e


def load_registry() -> dict[str, Any]:
    """
    Load worktree registry from JSON file.

    Returns:
        Registry dictionary with worktrees, port_ranges, naming_convention
    """
    with file_lock(REGISTRY_PATH):
        if not REGISTRY_PATH.exists():
            # Initialize default registry structure
            return {
                "worktrees": [],
                "port_ranges": DEFAULT_PORT_RANGES,
                "naming_convention": NAMING_CONVENTION,
                "worktree_base": str(DEFAULT_WORKTREE_BASE),
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }

        try:
            registry: dict[str, Any] = json.loads(REGISTRY_PATH.read_text())
            # Validate registry structure
            if "worktrees" not in registry:
                registry["worktrees"] = []
            if "port_ranges" not in registry:
                registry["port_ranges"] = DEFAULT_PORT_RANGES
            if "naming_convention" not in registry:
                registry["naming_convention"] = NAMING_CONVENTION
            if "worktree_base" not in registry:
                registry["worktree_base"] = str(DEFAULT_WORKTREE_BASE)
            return registry
        except json.JSONDecodeError as e:
            raise WorktreeError(
                f"Failed to parse registry at {REGISTRY_PATH}: {e}"
            ) from e


def save_registry(registry: dict[str, Any]) -> None:
    """
    Save worktree registry to JSON file.

    Args:
        registry: Registry dictionary to save

    Raises:
        WorktreeError: If unable to save registry
    """
    with file_lock(REGISTRY_PATH):
        try:
            registry["last_updated"] = datetime.now().isoformat()
            atomic_write_json(registry, REGISTRY_PATH)
        except OSError as e:
            raise WorktreeError(
                f"Failed to save registry to {REGISTRY_PATH}: {e}"
            ) from e


def get_git_root() -> Path:
    """
    Get git repository root directory.

    Returns:
        Path to git root

    Raises:
        WorktreeError: If not in a git repository
    """
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    git_root = Path(result.stdout.strip())
    if not git_root.exists():
        raise WorktreeError("Not in a git repository")
    return git_root


def validate_branch(branch: str) -> bool:
    """
    Check if branch exists locally or remotely.

    Args:
        branch: Branch name to validate

    Returns:
        True if branch exists
    """
    # Check local branches
    result = run_command(["git", "branch", "--list", branch], check=False)
    if result.stdout.strip():
        return True

    # Check remote branches
    result = run_command(["git", "branch", "-r", "--list", f"*/{branch}"], check=False)
    if result.stdout.strip():
        return True

    return False


def check_worktree_exists(path: Path) -> bool:
    """
    Check if worktree already exists at given path.

    Args:
        path: Path to check

    Returns:
        True if worktree exists at path
    """
    result = run_command(["git", "worktree", "list", "--porcelain"], check=False)
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            worktree_path = Path(line.split(" ", 1)[1])
            if worktree_path.resolve() == path.resolve():
                return True
    return False


def get_worktree_name(purpose: str, identifier: str, registry: dict[str, Any]) -> str:
    """
    Generate worktree name based on naming convention.

    Args:
        purpose: Purpose type (review, feature, bugfix, test)
        identifier: Identifier (issue number, feature name, etc.)
        registry: Registry dictionary

    Returns:
        Worktree name following convention
    """
    convention: dict[str, str] = registry.get("naming_convention", NAMING_CONVENTION)
    template: str = convention.get(purpose, "{identifier}")
    return template.format(identifier=identifier)


def get_worktree_path(name: str, registry: dict[str, Any]) -> Path:
    """
    Get full path for worktree.

    Args:
        name: Worktree name
        registry: Registry dictionary

    Returns:
        Absolute path for worktree
    """
    git_root = get_git_root()
    worktree_base = Path(registry.get("worktree_base", str(DEFAULT_WORKTREE_BASE)))

    # Make worktree_base absolute if relative
    if not worktree_base.is_absolute():
        worktree_base = git_root / worktree_base

    return worktree_base / name


def allocate_ports(purpose: str, count: int, registry: dict[str, Any]) -> list[int]:
    """
    Allocate available ports for worktree services with system-level verification.

    Checks both registry allocations AND actual system port availability.
    FAIL-FAST: Exits if port conflict detected during allocation.

    Args:
        purpose: Purpose type to determine port range
        count: Number of ports to allocate
        registry: Registry dictionary

    Returns:
        List of allocated port numbers

    Raises:
        WorktreeError: If not enough ports available or port conflict detected
    """
    port_ranges = registry.get("port_ranges", DEFAULT_PORT_RANGES)

    if purpose not in port_ranges:
        raise WorktreeError(f"No port range defined for purpose: {purpose}")

    port_range = port_ranges[purpose]
    start_port: int = port_range["start"]
    end_port: int = port_range["end"]

    # Collect all registry-allocated ports
    allocated_ports: set[int] = set()
    for worktree in registry["worktrees"]:
        if "ports" in worktree and worktree["ports"]:
            allocated_ports.update(worktree["ports"])

    # Find available ports in range - check BOTH registry AND system
    available_ports: list[int] = []
    conflicts: list[int] = []  # Track ports that are registry-free but system-occupied

    for port in range(start_port, end_port + 1):
        # Skip if already in registry
        if port in allocated_ports:
            continue

        # CRITICAL: Verify port is actually available on system
        if not is_port_available(port):
            # Port is free in registry but occupied on system - conflict!
            conflicts.append(port)
            continue

        # Port is truly available - both registry and system
        available_ports.append(port)
        if len(available_ports) >= count:
            break

    # FAIL-FAST: Report conflicts immediately
    if conflicts:
        conflict_list = ", ".join(map(str, conflicts[:5]))  # Show first 5
        if len(conflicts) > 5:
            conflict_list += f" (and {len(conflicts) - 5} more)"
        raise WorktreeError(
            f"Port conflict detected in {purpose} range {start_port}-{end_port}. "
            f"Ports free in registry but occupied on system: {conflict_list}. "
            f"Run 'registry_validate.py --verify-ports' to detect and clean stale allocations."
        )

    # Check if we found enough ports
    if len(available_ports) < count:
        raise WorktreeError(
            f"Not enough ports available in range {start_port}-{end_port}. "
            f"Requested: {count}, Available: {len(available_ports)} "
            f"(Registry allocated: {len(allocated_ports)}, System conflicts: {len(conflicts)})"
        )

    return available_ports[:count]


def create_worktree_git(path: Path, branch: str, new_branch: bool = False) -> None:
    """
    Create git worktree using git worktree add command.

    Args:
        path: Path where worktree will be created
        branch: Branch to checkout in worktree
        new_branch: Create new branch if True

    Raises:
        WorktreeError: If git worktree creation fails
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Build git worktree add command
    cmd = ["git", "worktree", "add"]

    if new_branch:
        cmd.extend(["-b", branch])

    cmd.append(str(path))

    if not new_branch:
        cmd.append(branch)

    # Execute command
    run_command(cmd)


def register_worktree(
    name: str,
    path: Path,
    purpose: str,
    identifier: str,
    branch: str,
    ports: Optional[list[int]],
    registry: dict[str, Any],
) -> None:
    """
    Add worktree entry to registry.

    Args:
        name: Worktree name
        path: Worktree path
        purpose: Purpose type
        identifier: Identifier
        branch: Branch name
        ports: Allocated ports (if any)
        registry: Registry dictionary
    """
    entry: dict[str, Any] = {
        "name": name,
        "path": str(path.resolve()),
        "purpose": purpose,
        "identifier": identifier,
        "branch": branch,
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }

    if ports:
        entry["ports"] = ports

    registry["worktrees"].append(entry)
    save_registry(registry)


def create_worktree(
    purpose: str,
    identifier: str,
    branch: str,
    should_allocate_ports: bool = False,
    port_count: int = 1,
    new_branch: bool = False,
) -> tuple[str, Path, Optional[list[int]]]:
    """
    Create worktree with registry entry and optional port allocation.

    Args:
        purpose: Purpose type (review, feature, bugfix, test)
        identifier: Issue number or feature name
        branch: Branch to checkout
        should_allocate_ports: Whether to allocate ports
        port_count: Number of ports to allocate
        new_branch: Create new branch if True

    Returns:
        Tuple of (worktree_name, worktree_path, allocated_ports)

    Raises:
        WorktreeError: If worktree creation fails
    """
    # Load registry
    registry = load_registry()

    # Validate we're in a git repo
    get_git_root()

    # Validate branch exists (unless creating new)
    if not new_branch and not validate_branch(branch):
        raise WorktreeError(
            f"Branch '{branch}' does not exist. Use --new-branch to create it."
        )

    # Generate worktree name and path
    name = get_worktree_name(purpose, identifier, registry)
    path = get_worktree_path(name, registry)

    # Check if worktree already exists
    if check_worktree_exists(path):
        raise WorktreeError(f"Worktree already exists at: {path}")

    # Check if path already exists in registry
    for wt in registry["worktrees"]:
        if wt["path"] == str(path.resolve()):
            raise WorktreeError(f"Worktree path already registered: {path}")

    # Allocate ports if requested
    ports: Optional[list[int]] = None
    if should_allocate_ports:
        ports = allocate_ports(purpose, port_count, registry)

    # Create git worktree
    create_worktree_git(path, branch, new_branch=new_branch)

    # Register in registry
    register_worktree(name, path, purpose, identifier, branch, ports, registry)

    return name, path, ports


def print_success_message(name: str, path: Path, ports: Optional[list[int]]) -> None:
    """Print success message with worktree details."""
    print("Worktree created successfully")
    print(f"  Name: {name}")
    print(f"  Path: {path}")
    if ports:
        print(f"  Ports: {', '.join(map(str, ports))}")
    print("\nTo enter worktree:")
    print(f"  cd {path}")


def main() -> int:
    """Main entry point for worktree creation script."""
    parser = argparse.ArgumentParser(
        description="Create git worktree with registry integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create review worktree for PR 123
  %(prog)s --purpose review --identifier 123 --branch pr-123

  # Create feature worktree with port allocation
  %(prog)s --purpose feature --identifier user-auth --branch feature/user-auth --ports

  # Create new branch in worktree
  %(prog)s --purpose bugfix --identifier issue-456 --branch fix/issue-456 --new-branch

  # Allocate multiple ports for test worktree
  %(prog)s --purpose test --identifier e2e --branch main --ports --port-count 3
        """,
    )

    parser.add_argument(
        "--purpose",
        choices=["review", "feature", "bugfix", "test"],
        required=True,
        help="Purpose of the worktree",
    )

    parser.add_argument(
        "--identifier",
        required=True,
        help="Issue number, feature name, or test identifier",
    )

    parser.add_argument(
        "--branch", required=True, help="Branch to checkout in worktree"
    )

    parser.add_argument(
        "--ports", action="store_true", help="Allocate ports for worktree services"
    )

    parser.add_argument(
        "--port-count",
        type=int,
        default=1,
        help="Number of ports to allocate (default: 1)",
    )

    parser.add_argument(
        "--new-branch",
        action="store_true",
        help="Create new branch instead of checking out existing one",
    )

    args = parser.parse_args()

    try:
        # Create worktree
        name, path, ports = create_worktree(
            purpose=args.purpose,
            identifier=args.identifier,
            branch=args.branch,
            should_allocate_ports=args.ports,
            port_count=args.port_count,
            new_branch=args.new_branch,
        )

        # Print success message
        print_success_message(name, path, ports)

        return 0

    except WorktreeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
