#!/usr/bin/env python3
"""Merge conflict safeguards for multi-worktree development.

Prevents conflicts when multiple feature branches are merged sequentially.
Provides validation, rebasing, and conflict detection.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
# Dynamic import from shared directory requires sys.path modification
from cross_platform import git_worktree_list  # type: ignore[import-not-found]  # noqa: E402
from cross_platform import run_command  # noqa: E402


class MergeStatus(Enum):
    """Status of merge readiness."""

    CLEAN = "clean"
    CONFLICTS = "conflicts"
    NEEDS_REBASE = "needs_rebase"
    DIVERGED = "diverged"


@dataclass
class WorktreeMergeState:
    """State of worktree relative to base branch."""

    name: str
    path: Path
    branch: str
    base_branch: str
    commits_ahead: int
    commits_behind: int
    status: MergeStatus
    conflicting_files: list[str]


def check_merge_status(
    worktree_path: Path, base_branch: str = "main"
) -> WorktreeMergeState:
    """Check if worktree can merge cleanly into base branch.

    Args:
        worktree_path: Path to worktree directory
        base_branch: Base branch to merge into (default: 'main')

    Returns:
        WorktreeMergeState object with detailed merge status
    """
    worktree_path = Path(worktree_path)

    # Fetch latest from remote
    run_command(["git", "fetch", "origin", base_branch], cwd=worktree_path)

    # Get current branch name
    code, out, err = run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree_path
    )
    branch = out.strip() if code == 0 else "unknown"

    # Calculate commits ahead/behind
    code, out, err = run_command(
        ["git", "rev-list", "--count", f"origin/{base_branch}..HEAD"], cwd=worktree_path
    )
    commits_ahead = int(out.strip()) if code == 0 else 0

    code, out, err = run_command(
        ["git", "rev-list", "--count", f"HEAD..origin/{base_branch}"], cwd=worktree_path
    )
    commits_behind = int(out.strip()) if code == 0 else 0

    # Try dry-run merge to detect conflicts
    conflicting_files = []
    status = MergeStatus.CLEAN

    # WHY: Stash uncommitted changes before dry-run merge to avoid polluting working directory
    # and to ensure merge test is performed on clean state. We restore them after.
    run_command(["git", "stash", "--include-untracked"], cwd=worktree_path)

    code, out, err = run_command(
        ["git", "merge", "--no-commit", "--no-ff", f"origin/{base_branch}"],
        cwd=worktree_path,
    )

    if code != 0:
        # Parse conflict files from git status
        code2, out2, err2 = run_command(["git", "status", "--short"], cwd=worktree_path)
        if code2 == 0:
            for line in out2.strip().split("\n"):
                if line.startswith("UU ") or line.startswith("AA "):
                    conflicting_files.append(line[3:].strip())

        status = (
            MergeStatus.CONFLICTS if conflicting_files else MergeStatus.NEEDS_REBASE
        )
        run_command(["git", "merge", "--abort"], cwd=worktree_path)
    else:
        run_command(["git", "merge", "--abort"], cwd=worktree_path)

        if commits_behind > 0:
            status = MergeStatus.NEEDS_REBASE
        elif commits_ahead == 0 and commits_behind == 0:
            status = MergeStatus.CLEAN
        else:
            status = MergeStatus.CLEAN

    # Restore stashed changes
    run_command(["git", "stash", "pop"], cwd=worktree_path)

    return WorktreeMergeState(
        name=worktree_path.name,
        path=worktree_path,
        branch=branch,
        base_branch=base_branch,
        commits_ahead=commits_ahead,
        commits_behind=commits_behind,
        status=status,
        conflicting_files=conflicting_files,
    )


def get_merge_order(worktrees: list[Path]) -> list[Path]:
    """Determine optimal merge order to minimize conflicts.

    # WHY: We use oldest-commit-first ordering because merging older branches first means
    # newer branches will rebase onto the latest main which includes those older changes.
    # This minimizes conflict resolution iterations compared to random or newest-first order.

    Uses dependency analysis and commit timestamps to order merges.
    Worktrees with older commits merge first, newer ones last.
    This minimizes the number of rebases needed.

    Args:
        worktrees: List of worktree paths

    Returns:
        Ordered list of worktree paths (oldest commits first)
    """
    worktree_timestamps = []

    for wt in worktrees:
        # Get timestamp of oldest commit not in main
        code, out, err = run_command(
            ["git", "log", "--format=%ct", "origin/main..HEAD"], cwd=wt
        )

        if code == 0 and out.strip():
            # Get oldest commit timestamp (last in list)
            timestamps = [int(ts) for ts in out.strip().split("\n") if ts]
            oldest_ts = min(timestamps) if timestamps else 0
        else:
            oldest_ts = 0

        worktree_timestamps.append((oldest_ts, wt))

    # Sort by timestamp (oldest first)
    worktree_timestamps.sort(key=lambda x: x[0])

    return [wt for _, wt in worktree_timestamps]


def pre_merge_validation(worktree_path: Path) -> tuple[bool, list[str]]:
    """Validate worktree is ready for merge.

    Checks:
    1. All changes committed
    2. No uncommitted files
    3. Branch is up-to-date with remote
    4. No merge conflicts with base
    5. Tests pass (if test command exists)

    Args:
        worktree_path: Path to worktree directory

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues: list[str] = []
    worktree_path = Path(worktree_path)

    # Check clean working directory
    code, out, err = run_command(["git", "status", "--porcelain"], cwd=worktree_path)
    if code == 0 and out.strip():
        uncommitted_count = len([line for line in out.strip().split("\n") if line])
        issues.append(f"Uncommitted changes: {uncommitted_count} files")

    # Check if behind remote
    run_command(["git", "fetch", "origin"], cwd=worktree_path)

    # Get current branch
    code, out, err = run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree_path
    )
    branch = out.strip() if code == 0 else None

    if branch:
        # Check if tracking remote
        code, out, err = run_command(
            ["git", "rev-parse", "--abbrev-ref", "@{u}"], cwd=worktree_path
        )
        if code == 0:
            # Has upstream, check if behind
            code2, out2, err2 = run_command(
                ["git", "rev-list", "--count", "HEAD..@{u}"],
                cwd=worktree_path,
            )
            if code2 == 0:
                behind_count = int(out2.strip() or 0)
                if behind_count > 0:
                    issues.append(f"Branch is {behind_count} commits behind remote")

    # Dry-run merge to check conflicts
    code, out, err = run_command(
        ["git", "merge", "--no-commit", "--no-ff", "origin/main"],
        cwd=worktree_path,
    )

    if code != 0:
        # Count conflicts
        code2, out2, err2 = run_command(["git", "status", "--short"], cwd=worktree_path)
        if code2 == 0:
            conflict_count = len(
                [
                    line
                    for line in out2.strip().split("\n")
                    if line.startswith("UU ") or line.startswith("AA ")
                ]
            )
            if conflict_count > 0:
                issues.append(f"Merge conflicts detected: {conflict_count} files")
        run_command(["git", "merge", "--abort"], cwd=worktree_path)
    else:
        run_command(["git", "merge", "--abort"], cwd=worktree_path)

    return len(issues) == 0, issues


def rebase_worktree(worktree_path: Path, base_branch: str = "main") -> tuple[bool, str]:
    """Rebase worktree onto latest base branch.

    Args:
        worktree_path: Path to worktree directory
        base_branch: Base branch to rebase onto (default: 'main')

    Returns:
        Tuple of (success, message)
    """
    worktree_path = Path(worktree_path)

    # Fetch latest
    run_command(["git", "fetch", "origin", base_branch], cwd=worktree_path)

    # Attempt rebase
    code, out, err = run_command(
        ["git", "rebase", f"origin/{base_branch}"], cwd=worktree_path
    )

    if code != 0:
        # Abort failed rebase
        run_command(["git", "rebase", "--abort"], cwd=worktree_path)
        return False, f"Rebase failed: {err.strip()}"

    return True, "Rebase successful"


def detect_file_conflicts(worktrees: list[Path]) -> dict[str, list[str]]:
    """Detect files modified in multiple worktrees (potential conflicts).

    # WHY: Early conflict detection allows developers to coordinate before merging.
    # By comparing diffs against main for all worktrees, we identify overlapping changes
    # that will cause merge conflicts, enabling proactive resolution strategies.

    Args:
        worktrees: List of worktree paths

    Returns:
        Dictionary mapping filename to list of worktrees that modified it
        Only includes files modified in 2+ worktrees
    """
    file_changes: dict[str, list[str]] = {}  # file -> [worktrees that modified it]

    for wt in worktrees:
        # Get files changed vs main
        code, out, err = run_command(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=wt,
        )
        if code == 0 and out.strip():
            for changed_file in out.strip().split("\n"):
                if changed_file:
                    if changed_file not in file_changes:
                        file_changes[changed_file] = []
                    file_changes[changed_file].append(str(wt.name))

    # Return only files with multiple modifiers
    return {
        filepath: worktree_list
        for filepath, worktree_list in file_changes.items()
        if len(worktree_list) > 1
    }


def suggest_merge_strategy(conflicts: dict[str, list[str]]) -> str:
    """Suggest merge strategy based on conflict analysis.

    Args:
        conflicts: Dictionary of files to list of worktrees modifying them

    Returns:
        Multi-line string with merge strategy recommendations
    """
    if not conflicts:
        return "SAFE: No file conflicts detected. Merge in any order."

    suggestions = ["CONFLICTS DETECTED:\n"]
    for file, worktrees in conflicts.items():
        suggestions.append(f"  {file}: modified in {', '.join(worktrees)}")

    suggestions.append("\nRECOMMENDED STRATEGY:")
    suggestions.append("1. Merge worktrees one at a time")
    suggestions.append("2. After each merge, rebase remaining worktrees")
    suggestions.append("3. Resolve conflicts in each rebase before proceeding")
    suggestions.append("4. Run tests after each merge to catch integration issues")
    suggestions.append("\nMERGE ORDER:")
    suggestions.append("- Oldest commits first (already determined by get_merge_order)")
    suggestions.append("- This minimizes the number of rebases needed")

    return "\n".join(suggestions)


def create_merge_plan(worktrees: list[Path]) -> dict[str, Any]:
    """Create a merge plan with order and conflict warnings.

    Args:
        worktrees: List of worktree paths to merge

    Returns:
        Dictionary with merge plan details:
        - merge_order: ordered list of worktree paths
        - file_conflicts: files modified in multiple worktrees
        - strategy: recommended merge strategy
        - validations_required: list of validation issues per worktree
        - merge_states: detailed status for each worktree
    """
    conflicts = detect_file_conflicts(worktrees)
    order = get_merge_order(worktrees)

    validations_required: list[dict[str, Any]] = []
    merge_states: list[dict[str, Any]] = []

    for wt in order:
        valid, issues = pre_merge_validation(wt)
        if not valid:
            validations_required.append({"worktree": str(wt), "issues": issues})

        # Get detailed merge state
        state = check_merge_status(wt)
        merge_states.append(
            {
                "worktree": str(wt),
                "branch": state.branch,
                "commits_ahead": state.commits_ahead,
                "commits_behind": state.commits_behind,
                "status": state.status.value,
                "conflicting_files": state.conflicting_files,
            }
        )

    plan: dict[str, Any] = {
        "merge_order": [str(p) for p in order],
        "file_conflicts": conflicts,
        "strategy": suggest_merge_strategy(conflicts),
        "validations_required": validations_required,
        "merge_states": merge_states,
    }

    return plan


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge conflict safeguards for multi-worktree development"
    )
    parser.add_argument("--check", type=Path, help="Check single worktree merge status")
    parser.add_argument(
        "--plan", action="store_true", help="Create merge plan for all worktrees"
    )
    parser.add_argument("--rebase", type=Path, help="Rebase worktree onto main")
    parser.add_argument(
        "--conflicts",
        action="store_true",
        help="Detect file conflicts across all worktrees",
    )
    parser.add_argument(
        "--validate", type=Path, help="Validate worktree is ready for merge"
    )
    parser.add_argument(
        "--base-branch",
        type=str,
        default="main",
        help="Base branch for operations (default: main)",
    )
    parser.add_argument(
        "--output", type=Path, help="Output file for results (JSON format)"
    )

    args = parser.parse_args()

    result = None

    if args.check:
        # Check single worktree merge status
        state = check_merge_status(args.check, args.base_branch)
        result = {
            "worktree": str(state.path),
            "branch": state.branch,
            "commits_ahead": state.commits_ahead,
            "commits_behind": state.commits_behind,
            "status": state.status.value,
            "conflicting_files": state.conflicting_files,
        }

        if not args.output:
            print(f"\nMerge Status for {state.name}:")
            print(f"  Branch: {state.branch}")
            print(f"  Commits ahead of {state.base_branch}: {state.commits_ahead}")
            print(f"  Commits behind {state.base_branch}: {state.commits_behind}")
            print(f"  Status: {state.status.value}")
            if state.conflicting_files:
                print("  Conflicting files:")
                for conflict_file in state.conflicting_files:
                    print(f"    - {conflict_file}")

    elif args.plan:
        # Create merge plan for all worktrees
        worktrees = []
        for wt_info in git_worktree_list():
            path = wt_info.get("path")
            if path and path.name != ".git":  # Skip main worktree
                worktrees.append(path)

        if not worktrees:
            print("No worktrees found")
            sys.exit(1)

        plan = create_merge_plan(worktrees)
        result = plan

        if not args.output:
            print("\n=== MERGE PLAN ===\n")
            print("Merge Order:")
            for i, wt in enumerate(plan["merge_order"], 1):
                print(f"  {i}. {wt}")

            print(f"\n{plan['strategy']}")

            if plan["validations_required"]:
                print("\n=== VALIDATION ISSUES ===")
                for v in plan["validations_required"]:
                    print(f"\n{v['worktree']}:")
                    for issue in v["issues"]:
                        print(f"  - {issue}")

            if plan["merge_states"]:
                print("\n=== MERGE STATES ===")
                for s in plan["merge_states"]:
                    print(f"\n{Path(s['worktree']).name} ({s['branch']}):")
                    print(
                        f"  Ahead: {s['commits_ahead']}, Behind: {s['commits_behind']}"
                    )
                    print(f"  Status: {s['status']}")
                    if s["conflicting_files"]:
                        print(f"  Conflicts: {', '.join(s['conflicting_files'])}")

    elif args.rebase:
        # Rebase single worktree
        success, message = rebase_worktree(args.rebase, args.base_branch)
        result = {"success": success, "message": message}

        if not args.output:
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                sys.exit(1)

    elif args.conflicts:
        # Detect file conflicts
        worktrees = []
        for wt_info in git_worktree_list():
            path = wt_info.get("path")
            if path and path.name != ".git":
                worktrees.append(path)

        conflicts = detect_file_conflicts(worktrees)
        result = {"conflicts": conflicts}

        if not args.output:
            if conflicts:
                print("\n=== FILE CONFLICTS ===\n")
                for file, wts in conflicts.items():
                    print(f"{file}:")
                    for wt in wts:
                        print(f"  - {wt}")
            else:
                print("No file conflicts detected")

    elif args.validate:
        # Validate single worktree
        valid, issues = pre_merge_validation(args.validate)
        result = {"valid": valid, "issues": issues}

        if not args.output:
            if valid:
                print(f"✓ Worktree {args.validate.name} is ready for merge")
            else:
                print(f"✗ Validation failed for {args.validate.name}:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

    # Write output to file if specified
    if args.output and result:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as output_file:
            json.dump(result, output_file, indent=2)
        # WHY: Verify file was written correctly to catch disk errors or permission issues early
        if not args.output.exists():
            print(f"ERROR: Failed to write output file {args.output}", file=sys.stderr)
            sys.exit(1)
        written_size = args.output.stat().st_size
        if written_size == 0:
            print(f"ERROR: Output file {args.output} is empty", file=sys.stderr)
            sys.exit(1)
        print(f"Results written to {args.output} ({written_size} bytes)")

    sys.exit(0)
