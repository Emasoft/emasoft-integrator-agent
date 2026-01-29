---
name: eia-git-worktree-operations
description: Teaches parallel PR processing using git worktrees for isolated, concurrent development across multiple pull requests without branch switching overhead.
license: Apache-2.0
metadata:
  version: 1.0.0
  author: integrator-agent
  tags:
    - git
    - worktree
    - parallel-development
    - pr-workflow
    - isolation
  requires:
    - git >= 2.15
    - python >= 3.9
context: fork
---

# Git Worktree Operations Skill

## Overview

This skill teaches you how to use git worktrees for parallel PR processing. Git worktrees allow you to work on multiple branches simultaneously in separate directories while sharing a single git repository database.

### When to Use This Skill

Use git worktrees when you need to:

1. **Work on multiple PRs concurrently** without switching branches
2. **Maintain complete isolation** between different changes
3. **Delegate PR tasks to subagents** where each operates in its own directory
4. **Review PRs locally** while continuing development on another branch
5. **Run long-running tests** on one branch while developing on another

### When NOT to Use This Skill

Do NOT use worktrees when:

1. You only work on one branch at a time
2. The repository is very large and disk space is limited
3. You need to share uncommitted changes between "checkouts"
4. You are working with submodules (additional complexity)

---

## CRITICAL Constraints for Worktree Usage

**CONSTRAINT 1: ABSOLUTE ISOLATION**
Every file write, edit, or creation MUST happen within the assigned worktree directory. Writing files outside your worktree corrupts the isolation model and causes merge conflicts.

**CONSTRAINT 2: NO CONCURRENT GIT OPERATIONS**
Never run git operations (commit, push, fetch, rebase) in multiple worktrees simultaneously. Git's lock mechanisms can deadlock or corrupt the shared repository database.

**CONSTRAINT 3: VERIFY BEFORE CLEANUP**
Before removing a worktree, ALWAYS verify:
- All changes are committed
- All commits are pushed to remote
- No files were accidentally written outside the worktree

**CONSTRAINT 4: ONE BRANCH PER WORKTREE**
A branch can only be checked out in ONE worktree at a time. Attempting to checkout a branch that exists in another worktree will fail.

**CONSTRAINT 5: WORKTREE PATH RULES**
- Worktree paths must be outside the main repository
- Use absolute paths when creating worktrees
- Never nest worktrees inside each other

---

## Decision Tree for Worktree Operations

```
START: Need to work on a PR?
│
├─► Is this PR already in a worktree?
│   ├─► YES: Navigate to existing worktree
│   └─► NO: Continue below
│
├─► Is another git operation running?
│   ├─► YES: WAIT until it completes
│   └─► NO: Continue below
│
├─► Create new worktree for PR
│   ├─► Fetch PR branch from remote
│   ├─► Create worktree at designated path
│   └─► Verify worktree creation succeeded
│
├─► Work ONLY within worktree directory
│   ├─► All file operations inside worktree
│   ├─► All script executions from worktree
│   └─► Verify isolation periodically
│
├─► Ready to commit/push?
│   ├─► Verify no other git ops running
│   ├─► Commit changes in worktree
│   └─► Push to remote
│
└─► PR merged/completed?
    ├─► Verify all changes pushed
    ├─► Verify no uncommitted files
    └─► Remove worktree safely
```

---

## Reference Documents

### 1. Worktree Fundamentals

For understanding what worktrees are and how they work, see [worktree-fundamentals.md](references/worktree-fundamentals.md):

**Contents:**
- 1.1 What is a git worktree and why it exists
- 1.2 Worktree vs clone vs checkout - choosing the right approach
- 1.3 The shared git directory model explained
- 1.4 When worktrees provide measurable benefits
- 1.5 Common misconceptions about worktrees
- 1.6 Prerequisites and git version requirements

### 2. Parallel PR Workflow

For implementing parallel PR processing with worktrees, see [parallel-pr-workflow.md](references/parallel-pr-workflow.md):

**Contents:**
- 2.1 Creating worktrees for multiple simultaneous PRs
- 2.2 Isolation requirements and enforcement rules
- 2.3 Working directory management for subagents
- 2.4 Path validation rules and common violations
- 2.5 Handling concurrent git operation limitations
- 2.6 Example workflow: Processing 3 PRs in parallel
- 2.7 Error recovery when isolation is violated

### 3. Worktree Cleanup

For safely removing worktrees after PR completion, see [worktree-cleanup.md](references/worktree-cleanup.md):

**Contents:**
- 3.1 When to clean up worktrees (timing and triggers)
- 3.2 Verifying no uncommitted changes exist
- 3.3 Safe removal procedure step-by-step
- 3.4 Handling stuck worktrees and lock files
- 3.5 Force removal scenarios and their risks
- 3.6 Pruning stale worktree entries
- 3.7 Disk space recovery after cleanup

### 4. Worktree Verification

For verifying worktree integrity and isolation, see [worktree-verification.md](references/worktree-verification.md):

**Contents:**
- 4.1 Pre-cleanup verification checklist
- 4.2 Detecting files written outside worktree boundaries
- 4.3 Branch state verification procedures
- 4.4 Remote sync verification steps
- 4.5 Automated verification script usage
- 4.6 Manual verification when scripts fail
- 4.7 Reporting isolation violations

---

## Scripts Reference

This skill includes Python scripts for common worktree operations:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `atlas_create_worktree.py` | Create worktree for a PR | Starting work on a new PR |
| `atlas_list_worktrees.py` | List all active worktrees | Before creating new worktree, status check |
| `atlas_cleanup_worktree.py` | Safely remove a worktree | After PR is merged/closed |
| `atlas_verify_worktree_isolation.py` | Check for isolation violations | Before committing, periodically |
| `atlas_worktree_commit_push.py` | Commit and push changes | Ready to update remote |

### Script Usage Examples

**Creating a worktree for PR #123:**
```bash
python scripts/atlas_create_worktree.py --pr 123 --base-path /tmp/worktrees
```

**Listing all worktrees:**
```bash
python scripts/atlas_list_worktrees.py --repo-path /path/to/main/repo
```

**Verifying isolation:**
```bash
python scripts/atlas_verify_worktree_isolation.py --worktree-path /tmp/worktrees/pr-123
```

**Committing and pushing:**
```bash
python scripts/atlas_worktree_commit_push.py --worktree-path /tmp/worktrees/pr-123 --message "Fix issue"
```

**Cleaning up a worktree:**
```bash
python scripts/atlas_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123
```

---

## Troubleshooting

### Problem: "fatal: branch is already checked out"

**Cause:** Attempting to checkout a branch that exists in another worktree.

**Solution:** See [worktree-fundamentals.md](references/worktree-fundamentals.md) section 1.5 for branch constraint details.

### Problem: "worktree is dirty, cannot remove"

**Cause:** Attempting to remove a worktree with uncommitted changes.

**Solution:** See [worktree-cleanup.md](references/worktree-cleanup.md) section 3.2 for handling uncommitted changes.

### Problem: Files appearing in main repo after worktree work

**Cause:** Isolation violation - files were written outside the worktree.

**Solution:** See [worktree-verification.md](references/worktree-verification.md) section 4.2 for detection and remediation.

### Problem: "fatal: unable to create new worktree"

**Cause:** Lock file exists or path already in use.

**Solution:** See [worktree-cleanup.md](references/worktree-cleanup.md) section 3.4 for handling stuck worktrees.

### Problem: Git operations hanging or failing

**Cause:** Concurrent git operations in multiple worktrees.

**Solution:** See [parallel-pr-workflow.md](references/parallel-pr-workflow.md) section 2.5 for serialization strategies.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GIT WORKTREE QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────────┤
│ CREATE:   git worktree add <path> <branch>                          │
│ LIST:     git worktree list                                         │
│ REMOVE:   git worktree remove <path>                                │
│ PRUNE:    git worktree prune                                        │
├─────────────────────────────────────────────────────────────────────┤
│ CRITICAL RULES:                                                      │
│ 1. ONE branch per worktree (enforced by git)                        │
│ 2. ALL file ops inside worktree only                                │
│ 3. NO concurrent git ops across worktrees                           │
│ 4. VERIFY before cleanup                                            │
└─────────────────────────────────────────────────────────────────────┘
```
