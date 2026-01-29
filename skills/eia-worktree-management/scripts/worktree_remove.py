#!/usr/bin/env python3
"""
Remove git worktrees with comprehensive cleanup.

This script provides safe worktree removal with:
- Pre-removal validation (uncommitted changes, active processes)
- Port deallocation
- Registry cleanup
- Force removal support
- Bulk removal of completed/merged worktrees
- Dry-run mode for safety

Usage:
    python worktree_remove.py <id_or_path>              # Remove specific worktree
    python worktree_remove.py <id> --force              # Force remove (skip checks)
    python worktree_remove.py --all-completed           # Remove all merged worktrees
    python worktree_remove.py <id> --dry-run            # Preview what would be removed

Examples:
    python worktree_remove.py review-GH-42
    python worktree_remove.py ../review-GH-42
    python worktree_remove.py review-GH-42 --force
    python worktree_remove.py --all-completed
    python worktree_remove.py --all-completed --dry-run

Exit codes:
    0 - Success
    1 - Validation error (uncommitted changes, etc.)
    2 - Removal failed
    3 - User cancelled operation
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast
import shutil

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
import cross_platform  # type: ignore[import-not-found]  # noqa: E402

file_lock = cross_platform.file_lock
atomic_write_json = cross_platform.atomic_write_json
get_atlas_dir = cross_platform.get_atlas_dir


class RegistryManager:
    """Manages worktree registry operations."""

    def __init__(self, registry_path: Path | None = None):
        """
        Initialize registry manager.

        Args:
            registry_path: Path to registry.json file. If None, uses default location.
        """
        if registry_path is None:
            # Default: design/worktrees/registry.json in repo root
            self.registry_path = self._find_registry_path()
        else:
            self.registry_path = registry_path

        self.registry: dict[str, Any] = self._load_registry()

    def _find_registry_path(self) -> Path:
        """Find registry.json by searching up from current directory."""
        return cast(Path, get_atlas_dir()) / "worktrees" / "registry.json"

    def _load_registry(self) -> dict[str, Any]:
        """Load registry from disk."""
        with file_lock(self.registry_path):
            if not self.registry_path.exists():
                return {"worktrees": [], "port_ranges": {}, "naming_convention": {}}

            try:
                with open(self.registry_path) as f:
                    return cast(dict[str, Any], json.load(f))
            except json.JSONDecodeError as e:
                print(f"ERROR: Registry file corrupted: {e}")
                print(f"Try restoring from backup: {self.registry_path}.backup")
                sys.exit(2)

    def _save_registry(self) -> None:
        """Save registry to disk with backup using atomic writes."""
        with file_lock(self.registry_path):
            # Create backup
            if self.registry_path.exists():
                backup_path = self.registry_path.with_suffix(".json.backup")
                shutil.copy2(self.registry_path, backup_path)

            # Write new registry atomically
            atomic_write_json(self.registry, self.registry_path)

    def find_worktree(self, id_or_path: str) -> dict[str, Any] | None:
        """
        Find worktree entry by ID or path.

        Args:
            id_or_path: Worktree ID (e.g., 'review-GH-42') or path (e.g., '../review-GH-42')

        Returns:
            Worktree entry dict or None if not found
        """
        for entry in self.registry["worktrees"]:
            if entry["id"] == id_or_path or entry["path"] == id_or_path:
                return cast(dict[str, Any], entry)
        return None

    def remove_entry(self, worktree_id: str) -> None:
        """
        Remove worktree entry from registry.

        Args:
            worktree_id: ID of worktree to remove
        """
        original_count = len(self.registry["worktrees"])
        self.registry["worktrees"] = [
            wt for wt in self.registry["worktrees"] if wt["id"] != worktree_id
        ]

        if len(self.registry["worktrees"]) == original_count:
            raise ValueError(f"Worktree '{worktree_id}' not found in registry")

        self._save_registry()

    def get_allocated_ports(self, worktree_id: str) -> list[int]:
        """
        Get ports allocated to a worktree.

        Args:
            worktree_id: ID of worktree

        Returns:
            List of allocated port numbers
        """
        entry = self.find_worktree(worktree_id)
        if entry is None:
            return []
        return cast(list[int], entry.get("port_allocations", []))

    def release_ports(self, worktree_id: str) -> list[int]:
        """
        Release ports allocated to a worktree.

        This makes the ports available for future worktrees.
        Note: Actual port release happens when entry is removed from registry.

        Args:
            worktree_id: ID of worktree

        Returns:
            List of released port numbers
        """
        return self.get_allocated_ports(worktree_id)

    def get_completed_worktrees(self) -> list[dict[str, Any]]:
        """
        Get worktrees whose branches have been merged.

        Returns:
            List of completed worktree entries
        """
        completed = []
        for entry in self.registry["worktrees"]:
            if self._is_branch_merged(entry["branch"]):
                completed.append(entry)
        return completed

    def _is_branch_merged(self, branch: str) -> bool:
        """
        Check if a branch has been merged into main/master.

        Args:
            branch: Branch name to check

        Returns:
            True if branch is merged, False otherwise
        """
        try:
            # Check if branch is merged into main
            result = subprocess.run(
                ["git", "branch", "--merged", "main"],
                capture_output=True,
                text=True,
                check=False,
            )
            if branch in result.stdout:
                return True

            # Check if branch is merged into master (fallback)
            result = subprocess.run(
                ["git", "branch", "--merged", "master"],
                capture_output=True,
                text=True,
                check=False,
            )
            return branch in result.stdout

        except subprocess.SubprocessError:
            return False


class WorktreeRemover:
    """Handles safe removal of git worktrees."""

    def __init__(self, force: bool = False, dry_run: bool = False):
        """
        Initialize worktree remover.

        Args:
            force: Skip safety checks and confirmations
            dry_run: Preview actions without executing them
        """
        self.force = force
        self.dry_run = dry_run
        self.registry = RegistryManager()

    def remove(self, id_or_path: str) -> bool:
        """
        Remove a worktree by ID or path.

        Args:
            id_or_path: Worktree ID or path

        Returns:
            True if removal successful, False otherwise
        """
        # Find worktree in registry
        entry = self.registry.find_worktree(id_or_path)
        if entry is None:
            print(f"ERROR: Worktree '{id_or_path}' not found in registry")
            print("\nAvailable worktrees:")
            self._list_worktrees()
            return False

        print(f"\nWorktree: {entry['id']}")
        print(f"  Path: {entry['path']}")
        print(f"  Branch: {entry['branch']}")
        print(f"  Purpose: {entry['purpose']}")
        print(f"  Created: {entry['created']}")
        if entry.get("port_allocations"):
            print(f"  Allocated ports: {entry['port_allocations']}")

        # Pre-removal checks
        if not self.force and not self._pre_removal_checks(entry):
            return False

        # Confirm removal
        if not self.force and not self.dry_run:
            response = input("\nConfirm removal? [y/N]: ")
            if response.lower() not in {"y", "yes"}:
                print("Removal cancelled")
                return False

        # Execute removal
        return self._execute_removal(entry)

    def remove_all_completed(self) -> bool:
        """
        Remove all worktrees whose branches have been merged.

        Returns:
            True if all removals successful, False otherwise
        """
        completed = self.registry.get_completed_worktrees()

        if not completed:
            print("No completed worktrees found (all branches are unmerged)")
            return True

        print(f"\nFound {len(completed)} completed worktree(s):\n")
        for entry in completed:
            print(f"  - {entry['id']} (branch: {entry['branch']})")

        if not self.force and not self.dry_run:
            response = input(
                f"\nRemove all {len(completed)} completed worktree(s)? [y/N]: "
            )
            if response.lower() not in {"y", "yes"}:
                print("Bulk removal cancelled")
                return False

        # Remove each completed worktree
        success_count = 0
        for entry in completed:
            print(f"\n{'[DRY-RUN] ' if self.dry_run else ''}Removing {entry['id']}...")
            if self._execute_removal(entry):
                success_count += 1

        print(
            f"\n{'[DRY-RUN] ' if self.dry_run else ''}Removed {success_count}/{len(completed)} worktree(s)"
        )
        return success_count == len(completed)

    def _pre_removal_checks(self, entry: dict[str, Any]) -> bool:
        """
        Perform safety checks before removal.

        Args:
            entry: Worktree entry to check

        Returns:
            True if all checks pass, False otherwise
        """
        worktree_path = Path(entry["path"]).resolve()

        # Check 1: Directory exists
        if not worktree_path.exists():
            print(f"\n  WARNING: Worktree directory does not exist: {worktree_path}")
            print("  This is likely a stale registry entry.")
            response = input("  Remove registry entry anyway? [y/N]: ")
            if response.lower() not in {"y", "yes"}:
                return False
            return True  # Skip other checks if directory missing

        # Check 2: Uncommitted changes
        if self._has_uncommitted_changes(worktree_path):
            print("\n  WARNING: Worktree has uncommitted changes!")
            print("  You will lose any uncommitted work.")
            response = input("  Continue anyway? [y/N]: ")
            if response.lower() not in {"y", "yes"}:
                return False

        # Check 3: Unpushed commits
        if self._has_unpushed_commits(worktree_path, entry["branch"]):
            print("\n  WARNING: Worktree has unpushed commits!")
            print("  These commits will be lost unless you push them first.")
            response = input("  Continue anyway? [y/N]: ")
            if response.lower() not in {"y", "yes"}:
                return False

        # Check 4: Active processes
        if self._has_active_processes(worktree_path):
            print("\n  WARNING: Active processes detected in worktree!")
            print("  Removing the worktree may cause errors.")
            response = input("  Continue anyway? [y/N]: ")
            if response.lower() not in {"y", "yes"}:
                return False

        return True

    def _has_uncommitted_changes(self, path: Path) -> bool:
        """Check if worktree has uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except subprocess.SubprocessError:
            return False

    def _has_unpushed_commits(self, path: Path, branch: str) -> bool:
        """Check if worktree has unpushed commits."""
        try:
            # Get commits ahead of remote
            result = subprocess.run(
                ["git", "-C", str(path), "rev-list", f"origin/{branch}..{branch}"],
                capture_output=True,
                text=True,
                check=False,  # Don't fail if remote doesn't exist
            )
            return bool(result.stdout.strip())
        except subprocess.SubprocessError:
            return False

    def _has_active_processes(self, path: Path) -> bool:
        """Check if any processes are running in worktree directory."""
        try:
            # Use lsof on Unix-like systems
            result = subprocess.run(
                ["lsof", "+D", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            return bool(result.stdout.strip())
        except (subprocess.SubprocessError, FileNotFoundError):
            # lsof not available or failed - skip check
            return False

    def _execute_removal(self, entry: dict[str, Any]) -> bool:
        """
        Execute worktree removal.

        Args:
            entry: Worktree entry to remove

        Returns:
            True if removal successful, False otherwise
        """
        worktree_id = entry["id"]
        worktree_path = Path(entry["path"]).resolve()

        if self.dry_run:
            print(f"[DRY-RUN] Would remove worktree: {worktree_id}")
            print(f"[DRY-RUN]   Directory: {worktree_path}")
            print(f"[DRY-RUN]   Release ports: {entry.get('port_allocations', [])}")
            print(f"[DRY-RUN]   Remove registry entry: {worktree_id}")
            return True

        # Step 1: Release ports
        ports = self.registry.release_ports(worktree_id)
        if ports:
            print(f"  Released ports: {ports}")

        # Step 2: Remove git worktree
        if worktree_path.exists():
            try:
                print(f"  Removing git worktree: {worktree_path}")
                subprocess.run(
                    [
                        "git",
                        "worktree",
                        "remove",
                        str(worktree_path),
                        "--force" if self.force else "",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"  ERROR: Failed to remove git worktree: {e.stderr}")
                print("  Attempting manual cleanup...")

                # Fallback: Remove directory manually
                try:
                    shutil.rmtree(worktree_path)
                    # Prune git worktree list
                    subprocess.run(["git", "worktree", "prune"], check=False)
                except Exception as cleanup_error:
                    print(f"  ERROR: Manual cleanup failed: {cleanup_error}")
                    return False

        # Step 3: Remove registry entry
        try:
            print(f"  Removing registry entry: {worktree_id}")
            self.registry.remove_entry(worktree_id)
        except ValueError as e:
            print(f"  ERROR: {e}")
            return False

        print(f"\n  SUCCESS: Worktree '{worktree_id}' removed")
        return True

    def _list_worktrees(self) -> None:
        """Print list of available worktrees."""
        worktrees = self.registry.registry["worktrees"]
        if not worktrees:
            print("  (none)")
            return

        for entry in worktrees:
            print(f"  - {entry['id']} ({entry['purpose']}) - {entry['branch']}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remove git worktrees with comprehensive cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s review-GH-42                 # Remove specific worktree
  %(prog)s ../review-GH-42              # Remove by path
  %(prog)s review-GH-42 --force         # Force remove (skip checks)
  %(prog)s --all-completed              # Remove all merged worktrees
  %(prog)s --all-completed --dry-run    # Preview bulk removal
        """,
    )

    parser.add_argument(
        "id_or_path",
        nargs="?",
        help="Worktree ID or path to remove",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force removal (skip safety checks and confirmations)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be removed without executing",
    )

    parser.add_argument(
        "--all-completed",
        action="store_true",
        help="Remove all worktrees whose branches have been merged",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.all_completed and args.id_or_path:
        parser.error("Cannot specify both worktree ID and --all-completed")

    if not args.all_completed and not args.id_or_path:
        parser.error("Must specify either worktree ID or --all-completed")

    # Initialize remover
    remover = WorktreeRemover(force=args.force, dry_run=args.dry_run)

    # Execute removal
    try:
        if args.all_completed:
            success = remover.remove_all_completed()
        else:
            success = remover.remove(args.id_or_path)

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 3
    except Exception as e:
        print(f"\nERROR: {e}")
        if not args.force:
            print("\nTry with --force to bypass safety checks")
        return 2


if __name__ == "__main__":
    sys.exit(main())
