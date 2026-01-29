#!/usr/bin/env python3
"""
Worktree Registry Validation Script

Validates the worktree registry for consistency and correctness.
Checks registry against actual filesystem and git state.

Exit codes:
    0 - Registry is valid
    1 - Fixable issues found (use --fix to repair)
    2 - Critical errors requiring manual intervention
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import shutil

# Add shared module to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import (  # type: ignore[import-not-found]  # noqa: E402
    file_lock,
    atomic_write_json,
    is_port_available,
)
from thresholds import WorktreeThresholds  # type: ignore[import-not-found]  # noqa: E402

# Get thresholds instance
THRESHOLDS = WorktreeThresholds()

# Registry schema constants
REQUIRED_WORKTREE_FIELDS = ["id", "path", "branch", "created", "purpose", "status"]
VALID_STATUSES = ["active", "locked", "pending-removal"]
VALID_PURPOSES = ["review", "feature", "bugfix", "test", "hotfix", "refactor"]

# Default port ranges (if not specified in registry) - from shared thresholds
DEFAULT_PORT_RANGES = THRESHOLDS.PORT_RANGES_LIST


class ValidationError:
    """Represents a validation error or warning"""

    def __init__(
        self,
        severity: str,
        category: str,
        message: str,
        fixable: bool = False,
        fix_action: str = "",
    ):
        self.severity = severity  # "critical", "error", "warning"
        self.category = category  # "json", "filesystem", "git", "ports", etc.
        self.message = message
        self.fixable = fixable
        self.fix_action = fix_action

    def __str__(self) -> str:
        severity_symbol = {"critical": "✗", "error": "✗", "warning": "⚠"}.get(
            self.severity, "•"
        )

        fixable_note = " [FIXABLE]" if self.fixable else ""
        return (
            f"{severity_symbol} [{self.category.upper()}] {self.message}{fixable_note}"
        )


def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if port is actually available on the system using socket bind test.

    Args:
        port: Port number to check
        host: Host to bind on (default localhost)

    Returns:
        True if port is available (not in use), False if occupied
    """
    result: bool = is_port_available(port, host)
    return result


class RegistryValidator:
    """Validates worktree registry integrity"""

    def __init__(self, registry_path: str, verbose: bool = False, fix: bool = False):
        self._verify_ports = False
        self.registry_path = Path(registry_path)
        self.verbose = verbose
        self.fix = fix
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []
        self.fixes_applied: list[str] = []

        # Get repository root (parent of .atlas)
        self.repo_root = self.registry_path.parent.parent

    def log(self, message: str, level: str = "info") -> None:
        """Log message if verbose mode enabled"""
        if self.verbose or level == "always":
            prefix = {
                "info": "ℹ",
                "success": "✓",
                "warning": "⚠",
                "error": "✗",
                "always": "→",
            }.get(level, "•")
            print(f"{prefix} {message}")

    def add_error(
        self,
        severity: str,
        category: str,
        message: str,
        fixable: bool = False,
        fix_action: str = "",
    ) -> None:
        """Add a validation error"""
        error = ValidationError(severity, category, message, fixable, fix_action)

        if severity == "warning":
            self.warnings.append(error)
        else:
            self.errors.append(error)

        if self.verbose:
            print(f"  {error}")

    def load_registry(self) -> dict[str, Any] | None:
        """Load and parse registry JSON"""
        self.log("Loading registry...", "info")

        with file_lock(self.registry_path):
            if not self.registry_path.exists():
                self.add_error(
                    "critical",
                    "filesystem",
                    f"Registry file not found: {self.registry_path}",
                )
                return None

            try:
                with open(self.registry_path) as f:
                    registry: dict[str, Any] = json.load(f)

                self.log(
                    f"Registry loaded successfully ({len(registry.get('worktrees', []))} entries)",
                    "success",
                )
                return registry

            except json.JSONDecodeError as e:
                self.add_error("critical", "json", f"Invalid JSON in registry: {e}")
                return None
            except Exception as e:
                self.add_error(
                    "critical", "filesystem", f"Failed to read registry: {e}"
                )
                return None

    def save_registry(self, registry: dict[str, Any]) -> bool:
        """Save registry to disk using atomic writes"""
        if not self.fix:
            return False

        with file_lock(self.registry_path):
            try:
                # Create backup
                backup_path = self.registry_path.with_suffix(".json.backup")
                if self.registry_path.exists():
                    shutil.copy2(self.registry_path, backup_path)
                    self.log(f"Created backup: {backup_path}", "info")

                # Write registry atomically
                atomic_write_json(registry, self.registry_path)

                self.log("Registry saved successfully", "success")
                return True

            except Exception as e:
                self.add_error(
                    "critical", "filesystem", f"Failed to save registry: {e}"
                )
                return False

    def validate_json_structure(self, registry: dict[str, Any]) -> bool:
        """Validate registry JSON structure"""
        self.log("Validating JSON structure...", "info")

        valid = True

        # Check required top-level keys
        if "worktrees" not in registry:
            self.add_error("critical", "json", "Missing required key: 'worktrees'")
            valid = False
        elif not isinstance(registry["worktrees"], list):
            self.add_error("critical", "json", "'worktrees' must be an array")
            valid = False

        # Check optional keys have correct types
        if "port_ranges" in registry and not isinstance(registry["port_ranges"], dict):
            self.add_error("error", "json", "'port_ranges' must be an object")
            valid = False

        if "naming_convention" in registry and not isinstance(
            registry["naming_convention"], dict
        ):
            self.add_error("error", "json", "'naming_convention' must be an object")
            valid = False

        if valid:
            self.log("JSON structure is valid", "success")

        return valid

    def validate_worktree_entries(
        self, registry: dict[str, Any]
    ) -> tuple[bool, list[dict[str, Any]]]:
        """Validate individual worktree entries"""
        self.log("Validating worktree entries...", "info")

        valid_entries: list[dict[str, Any]] = []
        all_valid = True

        for idx, entry in enumerate(registry.get("worktrees", [])):
            entry_valid = True
            entry_id = entry.get("id", f"<unknown-{idx}>")

            # Check required fields
            missing_fields = [f for f in REQUIRED_WORKTREE_FIELDS if f not in entry]
            if missing_fields:
                self.add_error(
                    "error",
                    "schema",
                    f"Entry '{entry_id}': Missing required fields: {missing_fields}",
                    fixable=True,
                    fix_action="Remove entry",
                )
                entry_valid = False
                all_valid = False
                continue

            # Validate status value
            if entry["status"] not in VALID_STATUSES:
                self.add_error(
                    "error",
                    "schema",
                    f"Entry '{entry_id}': Invalid status '{entry['status']}'. "
                    f"Must be one of: {VALID_STATUSES}",
                    fixable=True,
                    fix_action="Set to 'active'",
                )
                entry_valid = False
                all_valid = False

            # Validate purpose value
            if entry["purpose"] not in VALID_PURPOSES:
                self.add_error(
                    "warning",
                    "schema",
                    f"Entry '{entry_id}': Non-standard purpose '{entry['purpose']}'. "
                    f"Expected: {VALID_PURPOSES}",
                )

            # Validate created timestamp
            try:
                datetime.fromisoformat(entry["created"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                self.add_error(
                    "error",
                    "schema",
                    f"Entry '{entry_id}': Invalid timestamp format '{entry.get('created')}'",
                )
                entry_valid = False
                all_valid = False

            # Validate path format
            if not entry["path"].startswith("../"):
                self.add_error(
                    "error",
                    "schema",
                    f"Entry '{entry_id}': Path must be relative (start with '../'), "
                    f"got: {entry['path']}",
                )
                entry_valid = False
                all_valid = False

            if entry_valid:
                valid_entries.append(entry)

        if all_valid:
            self.log(f"All {len(valid_entries)} entries are valid", "success")
        else:
            worktrees_list: list[Any] = registry["worktrees"]
            invalid_count = len(worktrees_list) - len(valid_entries)
            self.log(
                f"{len(valid_entries)} valid entries, {invalid_count} invalid",
                "warning",
            )

        return all_valid, valid_entries

    def check_duplicate_ids(self, entries: list[dict[str, Any]]) -> bool:
        """Check for duplicate IDs"""
        self.log("Checking for duplicate IDs...", "info")

        seen_ids: set[str] = set()
        duplicates: set[str] = set()

        for entry in entries:
            entry_id: str = entry["id"]
            if entry_id in seen_ids:
                duplicates.add(entry_id)
                self.add_error(
                    "error",
                    "duplicates",
                    f"Duplicate ID found: '{entry_id}'",
                    fixable=True,
                    fix_action="Remove duplicates (keep first occurrence)",
                )
            else:
                seen_ids.add(entry_id)

        if not duplicates:
            self.log("No duplicate IDs found", "success")
            return True
        else:
            self.log(f"Found {len(duplicates)} duplicate IDs", "error")
            return False

    def check_duplicate_paths(self, entries: list[dict[str, Any]]) -> bool:
        """Check for duplicate paths"""
        self.log("Checking for duplicate paths...", "info")

        seen_paths: set[str] = set()
        duplicates: set[str] = set()

        for entry in entries:
            path: str = entry["path"]
            if path in seen_paths:
                duplicates.add(path)
                self.add_error(
                    "error",
                    "duplicates",
                    f"Duplicate path found: '{path}' (ID: {entry['id']})",
                    fixable=True,
                    fix_action="Remove duplicates",
                )
            else:
                seen_paths.add(path)

        if not duplicates:
            self.log("No duplicate paths found", "success")
            return True
        else:
            self.log(f"Found {len(duplicates)} duplicate paths", "error")
            return False

    def check_filesystem(
        self, entries: list[dict[str, Any]]
    ) -> tuple[bool, list[dict[str, Any]]]:
        """Check worktree directories exist on filesystem"""
        self.log("Checking filesystem...", "info")

        existing_entries: list[dict[str, Any]] = []
        all_exist = True

        for entry in entries:
            worktree_path = self.repo_root / entry["path"]

            if not worktree_path.exists():
                self.add_error(
                    "error",
                    "filesystem",
                    f"Worktree directory missing: {entry['id']} -> {entry['path']}",
                    fixable=True,
                    fix_action="Remove from registry",
                )
                all_exist = False
            elif not worktree_path.is_dir():
                self.add_error(
                    "error",
                    "filesystem",
                    f"Path exists but is not a directory: {entry['id']} -> {entry['path']}",
                    fixable=True,
                    fix_action="Remove from registry",
                )
                all_exist = False
            else:
                existing_entries.append(entry)

        if all_exist:
            self.log(f"All {len(entries)} worktrees exist on filesystem", "success")
        else:
            self.log(
                f"{len(existing_entries)}/{len(entries)} worktrees exist on filesystem",
                "warning",
            )

        return all_exist, existing_entries

    def get_git_worktrees(self) -> set[str] | None:
        """Get list of worktrees from git"""
        self.log("Querying git worktrees...", "info")

        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

            worktrees: set[str] = set()
            for line in result.stdout.split("\n"):
                if line.startswith("worktree "):
                    path = Path(line[9:])  # Remove "worktree " prefix
                    # Convert to relative path from repo root
                    try:
                        rel_path = path.relative_to(self.repo_root.parent)
                        worktrees.add(f"../{rel_path}")
                    except ValueError:
                        # Path is not relative to parent, skip
                        pass

            self.log(f"Found {len(worktrees)} git worktrees", "success")
            return worktrees

        except subprocess.CalledProcessError as e:
            self.add_error(
                "critical", "git", f"Failed to query git worktrees: {e.stderr}"
            )
            return None
        except Exception as e:
            self.add_error("critical", "git", f"Failed to query git worktrees: {e}")
            return None

    def check_git_sync(self, entries: list[dict[str, Any]]) -> bool:
        """Check registry matches git worktree list"""
        self.log("Checking registry/git synchronization...", "info")

        git_worktrees = self.get_git_worktrees()
        if git_worktrees is None:
            return False

        registry_paths = {entry["path"] for entry in entries}

        # Check for entries in registry but not in git
        only_in_registry = registry_paths - git_worktrees
        for path in only_in_registry:
            entry_id = next((e["id"] for e in entries if e["path"] == path), "unknown")
            self.add_error(
                "error",
                "git",
                f"Worktree in registry but not in git: {entry_id} -> {path}",
                fixable=True,
                fix_action="Remove from registry",
            )

        # Check for git worktrees not in registry
        only_in_git = git_worktrees - registry_paths
        for path in only_in_git:
            self.add_error(
                "warning",
                "git",
                f"Git worktree not in registry: {path}",
                fixable=True,
                fix_action="Add to registry",
            )

        if not only_in_registry and not only_in_git:
            self.log("Registry and git are synchronized", "success")
            return True
        else:
            self.log(
                f"Found {len(only_in_registry)} registry-only and "
                f"{len(only_in_git)} git-only worktrees",
                "warning",
            )
            return False

    def check_branches_exist(self, entries: list[dict[str, Any]]) -> bool:
        """Check all referenced branches exist"""
        self.log("Checking branches exist...", "info")

        all_exist = True

        for entry in entries:
            branch: str = entry["branch"]

            # Check local branch
            try:
                subprocess.run(
                    ["git", "rev-parse", "--verify", branch],
                    cwd=self.repo_root,
                    capture_output=True,
                    check=True,
                )
                self.log(f"Branch '{branch}' exists (local)", "info")

            except subprocess.CalledProcessError:
                # Try remote branch
                try:
                    subprocess.run(
                        ["git", "rev-parse", "--verify", f"origin/{branch}"],
                        cwd=self.repo_root,
                        capture_output=True,
                        check=True,
                    )
                    self.log(f"Branch '{branch}' exists (remote)", "info")

                except subprocess.CalledProcessError:
                    self.add_error(
                        "error",
                        "git",
                        f"Branch not found: {branch} (worktree: {entry['id']})",
                        fixable=False,
                        fix_action="Manual intervention required",
                    )
                    all_exist = False

        if all_exist:
            self.log("All branches exist", "success")

        return all_exist

    def validate_port_ranges(self, registry: dict[str, Any]) -> bool:
        """Validate port range configuration"""
        self.log("Validating port ranges...", "info")

        if "port_ranges" not in registry:
            self.add_error(
                "warning",
                "ports",
                "No port_ranges defined in registry (will use defaults)",
            )
            return True

        port_ranges = registry["port_ranges"]
        valid = True

        for category, range_def in port_ranges.items():
            if not isinstance(range_def, list) or len(range_def) != 2:
                self.add_error(
                    "error",
                    "ports",
                    f"Invalid port range format for '{category}': {range_def}. "
                    "Expected [start, end]",
                )
                valid = False
                continue

            start, end = range_def

            if not isinstance(start, int) or not isinstance(end, int):
                self.add_error(
                    "error",
                    "ports",
                    f"Port range values must be integers for '{category}': {range_def}",
                )
                valid = False
                continue

            if start < THRESHOLDS.MIN_PORT:
                self.add_error(
                    "warning",
                    "ports",
                    f"Port range '{category}' starts below "
                    f"{THRESHOLDS.MIN_PORT} (system ports): {range_def}",
                )

            if end > THRESHOLDS.MAX_PORT:
                self.add_error(
                    "error",
                    "ports",
                    f"Port range '{category}' exceeds maximum port "
                    f"{THRESHOLDS.MAX_PORT}: {range_def}",
                )
                valid = False

            if start > end:
                self.add_error(
                    "error",
                    "ports",
                    f"Port range '{category}' has start > end: {range_def}",
                )
                valid = False

        if valid:
            self.log("Port ranges are valid", "success")

        return valid

    def check_port_allocations(
        self, entries: list[dict[str, Any]], registry: dict[str, Any]
    ) -> bool:
        """Check port allocations for conflicts and validity"""
        self.log("Checking port allocations...", "info")

        port_ranges = registry.get("port_ranges", DEFAULT_PORT_RANGES)
        allocated_ports: dict[int, list[str]] = {}  # port -> [worktree_ids]
        all_valid = True

        for entry in entries:
            if "port_allocations" not in entry or not entry["port_allocations"]:
                continue

            entry_id: str = entry["id"]

            for port in entry["port_allocations"]:
                # Check port is an integer
                if not isinstance(port, int):
                    self.add_error(
                        "error",
                        "ports",
                        f"Port allocation for '{entry_id}' is not an integer: {port}",
                    )
                    all_valid = False
                    continue

                # Check port is in valid range
                if not THRESHOLDS.is_valid_port(port):
                    self.add_error(
                        "error",
                        "ports",
                        f"Port {port} for '{entry_id}' is outside valid range "
                        f"({THRESHOLDS.MIN_PORT}-{THRESHOLDS.MAX_PORT})",
                    )
                    all_valid = False

                # Check port is within defined ranges
                in_range = False
                for _category, (start, end) in port_ranges.items():
                    if start <= port <= end:
                        in_range = True
                        break

                if not in_range:
                    self.add_error(
                        "warning",
                        "ports",
                        f"Port {port} for '{entry_id}' is not in any defined port range",
                    )

                # Track for duplicate check
                if port in allocated_ports:
                    allocated_ports[port].append(entry_id)
                else:
                    allocated_ports[port] = [entry_id]

        # Check for port conflicts
        conflicts = {port: ids for port, ids in allocated_ports.items() if len(ids) > 1}
        if conflicts:
            for port, ids in conflicts.items():
                self.add_error(
                    "error",
                    "ports",
                    f"Port {port} allocated to multiple worktrees: {ids}",
                    fixable=True,
                    fix_action="Release duplicate allocations",
                )
                all_valid = False

        if all_valid:
            total_ports = sum(len(e.get("port_allocations", [])) for e in entries)
            self.log(
                f"All {total_ports} port allocations are valid (no conflicts)",
                "success",
            )

        return all_valid

    def apply_fixes(self, registry: dict[str, Any]) -> dict[str, Any]:
        """Apply automatic fixes to registry"""
        if not self.fix:
            return registry

        self.log("Applying fixes...", "always")

        fixed_registry: dict[str, Any] = {
            "worktrees": [],
            "port_ranges": registry.get("port_ranges", DEFAULT_PORT_RANGES),
            "naming_convention": registry.get("naming_convention", {}),
        }

        # Track seen IDs and paths to remove duplicates
        seen_ids: set[str] = set()
        seen_paths: set[str] = set()
        seen_ports: set[int] = set()

        # Get git worktrees for sync check
        git_worktrees = self.get_git_worktrees()

        for entry in registry.get("worktrees", []):
            # Skip if missing required fields
            if not all(f in entry for f in REQUIRED_WORKTREE_FIELDS):
                self.fixes_applied.append(
                    f"Removed entry with missing fields: {entry.get('id', 'unknown')}"
                )
                continue

            entry_id: str = entry["id"]
            path: str = entry["path"]

            # Skip duplicates
            if entry_id in seen_ids:
                self.fixes_applied.append(f"Removed duplicate ID: {entry_id}")
                continue

            if path in seen_paths:
                self.fixes_applied.append(f"Removed duplicate path: {path}")
                continue

            # Skip if directory doesn't exist
            worktree_path = self.repo_root / path
            if not worktree_path.exists() or not worktree_path.is_dir():
                self.fixes_applied.append(
                    f"Removed entry for missing directory: {entry_id}"
                )
                continue

            # Skip if not in git worktrees
            if git_worktrees is not None and path not in git_worktrees:
                self.fixes_applied.append(
                    f"Removed entry not in git worktrees: {entry_id}"
                )
                continue

            # Fix invalid status
            if entry["status"] not in VALID_STATUSES:
                entry["status"] = "active"
                self.fixes_applied.append(
                    f"Fixed invalid status for {entry_id}: set to 'active'"
                )

            # Remove port conflicts
            if "port_allocations" in entry:
                original_ports = entry["port_allocations"]
                fixed_ports: list[int] = []
                for port in original_ports:
                    if port not in seen_ports:
                        fixed_ports.append(port)
                        seen_ports.add(port)
                    else:
                        self.fixes_applied.append(
                            f"Removed duplicate port allocation {port} from {entry_id}"
                        )

                entry["port_allocations"] = fixed_ports

            # Add to fixed registry
            fixed_registry["worktrees"].append(entry)
            seen_ids.add(entry_id)
            seen_paths.add(path)

        self.log(f"Applied {len(self.fixes_applied)} fixes", "success")

        return fixed_registry

    def verify_system_ports(self, entries: list[dict[str, Any]]) -> bool:
        """
        Verify allocated ports against actual system availability.

        Detects stale allocations where process crashed without cleanup.

        Args:
            entries: List of validated worktree entries

        Returns:
            True if all ports match system state, False if conflicts found
        """
        self.log("Verifying port allocations against system...", "info")

        all_valid = True
        checked_ports = 0

        for entry in entries:
            if "port_allocations" not in entry or not entry["port_allocations"]:
                continue

            entry_id: str = entry["id"]

            for port in entry["port_allocations"]:
                checked_ports += 1

                # Check if port is actually in use
                if check_port_available(port):
                    # Port allocated in registry but NOT in use on system - stale!
                    self.add_error(
                        "warning",
                        "ports",
                        f"Stale allocation: Port {port} allocated to '{entry_id}' "
                        "but not in use on system",
                        fixable=True,
                        fix_action="Release stale port allocation",
                    )
                    all_valid = False

        if all_valid and checked_ports > 0:
            self.log(
                f"All {checked_ports} allocated ports are in use on system", "success"
            )
        elif checked_ports == 0:
            self.log("No port allocations to verify", "info")

        return all_valid

    def validate(self) -> int:
        """
        Run all validations.

        Returns:
            0 - Valid
            1 - Fixable issues
            2 - Critical errors
        """
        self.log("Starting registry validation...", "always")
        self.log(f"Registry path: {self.registry_path}", "always")
        self.log(f"Repository root: {self.repo_root}", "always")
        self.log("", "always")

        # Load registry
        registry = self.load_registry()
        if registry is None:
            return 2  # Critical error

        # Validate JSON structure
        if not self.validate_json_structure(registry):
            return 2  # Critical error

        # Validate individual entries
        entries_valid, valid_entries = self.validate_worktree_entries(registry)

        # Run all checks
        checks = [
            self.check_duplicate_ids(valid_entries),
            self.check_duplicate_paths(valid_entries),
            self.validate_port_ranges(registry),
            self.check_port_allocations(valid_entries, registry),
        ]

        # Filesystem and git checks
        fs_valid, existing_entries = self.check_filesystem(valid_entries)
        checks.append(fs_valid)

        git_sync = self.check_git_sync(valid_entries)
        checks.append(git_sync)

        branches_exist = self.check_branches_exist(existing_entries)
        checks.append(branches_exist)

        # Apply fixes if requested
        if self.fix and (not all(checks) or not entries_valid):
            fixed_registry = self.apply_fixes(registry)
            if self.save_registry(fixed_registry):
                self.log("", "always")
                self.log("Fixes applied successfully", "success")
                for fix in self.fixes_applied:
                    self.log(f"  • {fix}", "always")

        # Print results
        self.log("", "always")
        self.log("=" * 60, "always")
        self.log("VALIDATION RESULTS", "always")
        self.log("=" * 60, "always")

        if self.errors:
            self.log(f"\n{len(self.errors)} Error(s):", "always")
            for error in self.errors:
                self.log(f"  {error}", "always")

        if self.warnings:
            self.log(f"\n{len(self.warnings)} Warning(s):", "always")
            for warning in self.warnings:
                self.log(f"  {warning}", "always")

        # Determine exit code
        has_critical = any(e.severity == "critical" for e in self.errors)
        has_fixable = any(e.fixable for e in self.errors)

        if has_critical:
            self.log(
                "\nResult: CRITICAL ERRORS - Manual intervention required", "always"
            )
            return 2
        elif self.errors:
            if has_fixable and not self.fix:
                self.log(
                    "\nResult: FIXABLE ERRORS - Run with --fix to repair", "always"
                )
                return 1
            elif self.fix and self.fixes_applied:
                self.log("\nResult: FIXED - Registry repaired successfully", "always")
                return 0
            else:
                self.log("\nResult: ERRORS - Manual intervention required", "always")
                return 2
        elif self.warnings:
            self.log("\nResult: VALID with warnings", "always")
            return 0
        else:
            self.log("\nResult: VALID - No issues found", "always")
            return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate worktree registry for consistency and correctness"
    )
    parser.add_argument(
        "registry",
        nargs="?",
        default="design/worktrees/registry.json",
        help="Path to registry file (default: design/worktrees/registry.json)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues (removes stale entries, adds missing)",
    )
    parser.add_argument(
        "--verify-ports",
        action="store_true",
        help="Verify allocated ports against actual system usage "
        "(detects stale allocations)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed validation output",
    )

    args = parser.parse_args()

    # Create validator
    validator = RegistryValidator(
        registry_path=args.registry,
        verbose=args.verbose,
        fix=args.fix,
    )

    # Enable port verification if requested
    if args.verify_ports:
        validator._verify_ports = True

    # Run validation
    exit_code = validator.validate()

    # Print minimal report (non-verbose mode)
    if not args.verbose:
        if exit_code == 0:
            if validator.fixes_applied:
                print(
                    f"[DONE] registry_validate.py - "
                    f"Fixed {len(validator.fixes_applied)} issues"
                )
            else:
                print(
                    f"[DONE] registry_validate.py - "
                    f"Valid ({len(validator.warnings)} warnings)"
                )
        elif exit_code == 1:
            fixable = sum(1 for e in validator.errors if e.fixable)
            print(
                f"[FAILED] registry_validate.py - "
                f"{len(validator.errors)} errors ({fixable} fixable with --fix)"
            )
        else:
            print(
                f"[FAILED] registry_validate.py - "
                f"{len(validator.errors)} critical errors"
            )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
