---
name: int-github-pr-merge
description: >
  PR merge operations including merge execution, auto-merge configuration,
  merge readiness verification, and merge state checking using GraphQL as
  the authoritative source of truth.
license: Apache-2.0
metadata:
  version: "1.0.0"
  author: integrator-agent
  category: github-workflow
  tags:
    - github
    - pull-request
    - merge
    - graphql
    - automation
  triggers:
    - merge PR
    - check if merged
    - auto-merge
    - merge readiness
    - squash merge
    - rebase merge
agent: api-coordinator
context: fork
---

# GitHub PR Merge Operations

This skill provides comprehensive guidance for merging pull requests, checking merge status, verifying merge readiness, and configuring auto-merge using the GitHub API.

## CRITICAL: GraphQL is the Source of Truth

**NEVER trust `gh pr view --json state` for merge state verification.**

The REST API and `gh pr view` can return stale data. GraphQL queries against the GitHub API provide the authoritative, real-time merge state. Always use GraphQL for:

- Checking if a PR is already merged
- Verifying merge eligibility (MergeStateStatus)
- Confirming merge completion

## Overview of Operations

| Operation | Script | Purpose |
|-----------|--------|---------|
| Check if merged | `atlas_test_pr_merged.py` | Verify PR merge status via GraphQL |
| Check readiness | `atlas_test_pr_merge_ready.py` | Verify all merge requirements met |
| Execute merge | `atlas_merge_pr.py` | Merge with specified strategy |
| Auto-merge | `atlas_set_auto_merge.py` | Enable/disable auto-merge |

## Decision Tree for PR Merge Operations

```
START: Need to merge a PR
    │
    ├─► Is PR already merged?
    │   Run: atlas_test_pr_merged.py --pr <number> --repo <owner/repo>
    │       │
    │       ├─► Exit 1 (merged) → STOP: PR already merged
    │       │
    │       └─► Exit 0 (not merged) → Continue
    │
    ├─► Is PR ready to merge?
    │   Run: atlas_test_pr_merge_ready.py --pr <number> --repo <owner/repo>
    │       │
    │       ├─► Exit 0 (ready) → Proceed to merge
    │       │
    │       ├─► Exit 1 (CI failing) → Fix CI or use --ignore-ci
    │       │
    │       ├─► Exit 2 (conflicts) → Resolve conflicts first
    │       │
    │       ├─► Exit 3 (threads) → Resolve threads or use --ignore-threads
    │       │
    │       └─► Exit 4 (reviews) → Get required approvals
    │
    ├─► Should merge now or auto-merge?
    │       │
    │       ├─► Merge now:
    │       │   Run: atlas_merge_pr.py --pr <number> --repo <owner/repo> \
    │       │        --strategy <merge|squash|rebase> [--delete-branch]
    │       │
    │       └─► Auto-merge when ready:
    │           Run: atlas_set_auto_merge.py --pr <number> --repo <owner/repo> \
    │                --enable --merge-method <MERGE|SQUASH|REBASE>
    │
    └─► Verify merge completed:
        Run: atlas_test_pr_merged.py --pr <number> --repo <owner/repo>
```

## When to Use Each Script

### atlas_test_pr_merged.py

Use BEFORE attempting any merge operation to avoid:
- Duplicate merge attempts
- Confusing error messages
- Wasted API calls

```bash
# Check if PR #123 in owner/repo is merged
python scripts/atlas_test_pr_merged.py --pr 123 --repo owner/repo
```

### atlas_test_pr_merge_ready.py

Use to understand WHY a PR cannot be merged:

```bash
# Full readiness check
python scripts/atlas_test_pr_merge_ready.py --pr 123 --repo owner/repo

# Skip CI check (emergency merge)
python scripts/atlas_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-ci

# Skip unresolved threads check
python scripts/atlas_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-threads
```

### atlas_merge_pr.py

Use to execute the actual merge:

```bash
# Squash merge and delete branch
python scripts/atlas_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch

# Regular merge commit
python scripts/atlas_merge_pr.py --pr 123 --repo owner/repo --strategy merge

# Rebase merge
python scripts/atlas_merge_pr.py --pr 123 --repo owner/repo --strategy rebase
```

### atlas_set_auto_merge.py

Use when PR needs to wait for CI or reviews:

```bash
# Enable auto-merge with squash
python scripts/atlas_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH

# Disable auto-merge
python scripts/atlas_set_auto_merge.py --pr 123 --repo owner/repo --disable
```

## Reference Documents

### Merge State Verification

See [references/merge-state-verification.md](references/merge-state-verification.md):

- 1.1 Why `gh pr view --json state` can be stale
  - 1.1.1 REST API caching behavior
  - 1.1.2 Race conditions in merge state
- 1.2 GraphQL as the source of truth
  - 1.2.1 GraphQL query for merge state
  - 1.2.2 Interpreting MergeStateStatus values
- 1.3 MergeStateStatus values explained
  - 1.3.1 MERGEABLE - safe to merge
  - 1.3.2 CONFLICTING - conflicts exist
  - 1.3.3 UNKNOWN - state being computed
  - 1.3.4 BLOCKED - branch protection rules blocking
  - 1.3.5 BEHIND - branch needs update
  - 1.3.6 DIRTY - merge commit cannot be cleanly created
  - 1.3.7 UNSTABLE - failing required status checks
- 1.4 Pre-merge verification checklist
  - 1.4.1 Required checks before merge
  - 1.4.2 Verification script usage

### Merge Strategies

See [references/merge-strategies.md](references/merge-strategies.md):

- 2.1 Merge commit strategy
  - 2.1.1 When to use merge commits
  - 2.1.2 Commit history implications
- 2.2 Squash merge strategy
  - 2.2.1 When to use squash merge
  - 2.2.2 Commit message handling
- 2.3 Rebase merge strategy
  - 2.3.1 When to use rebase merge
  - 2.3.2 Linear history benefits
- 2.4 Branch protection implications
  - 2.4.1 Required status checks
  - 2.4.2 Required reviewers
  - 2.4.3 Allowed merge methods
- 2.5 Delete branch after merge
  - 2.5.1 Automatic branch deletion
  - 2.5.2 Manual branch deletion

### Auto-Merge Configuration

See [references/auto-merge.md](references/auto-merge.md):

- 3.1 Setting up auto-merge via GraphQL API
  - 3.1.1 EnablePullRequestAutoMerge mutation
  - 3.1.2 Required permissions
- 3.2 Requirements for auto-merge
  - 3.2.1 Repository settings
  - 3.2.2 Branch protection rules
  - 3.2.3 Required status checks
- 3.3 Canceling auto-merge
  - 3.3.1 DisablePullRequestAutoMerge mutation
  - 3.3.2 When auto-merge is automatically canceled
- 3.4 Auto-merge with required reviewers
  - 3.4.1 Approval requirements
  - 3.4.2 Review dismissal handling

## Common Workflows

### Workflow 1: Standard PR Merge

```bash
# 1. Verify not already merged
python scripts/atlas_test_pr_merged.py --pr 123 --repo owner/repo
# Exit 0 means not merged, continue

# 2. Check readiness
python scripts/atlas_test_pr_merge_ready.py --pr 123 --repo owner/repo
# Exit 0 means ready

# 3. Merge with squash
python scripts/atlas_merge_pr.py --pr 123 --repo owner/repo --strategy squash --delete-branch

# 4. Verify merge completed
python scripts/atlas_test_pr_merged.py --pr 123 --repo owner/repo
# Exit 1 confirms merged
```

### Workflow 2: Auto-Merge Setup

```bash
# 1. Enable auto-merge (will merge when CI passes and reviews approved)
python scripts/atlas_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH

# 2. Later, check if merged
python scripts/atlas_test_pr_merged.py --pr 123 --repo owner/repo
```

### Workflow 3: Emergency Merge (Skip CI)

```bash
# 1. Check readiness ignoring CI
python scripts/atlas_test_pr_merge_ready.py --pr 123 --repo owner/repo --ignore-ci

# 2. If ready (exit 0), merge
python scripts/atlas_merge_pr.py --pr 123 --repo owner/repo --strategy merge
```

## Exit Codes (Standardized)

All scripts use standardized exit codes for consistent error handling:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Invalid parameters | Bad PR number, bad repo format |
| 2 | Resource not found | PR does not exist |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | PR already merged (no action needed) |
| 6 | Not mergeable | PR closed, conflicts, CI failing, reviews needed |

### Per-Script Exit Code Details

| Script | Exit 5 (Idempotency) | Exit 6 (Not Mergeable) |
|--------|---------------------|------------------------|
| atlas_test_pr_merged.py | PR already merged | N/A |
| atlas_test_pr_merge_ready.py | N/A | Any blocking condition (see JSON for details) |
| atlas_merge_pr.py | PR already merged | Conflicts, closed, not approved |
| atlas_set_auto_merge.py | PR already merged | Cannot enable auto-merge |

## Troubleshooting

### PR shows as not merged but merge failed

1. Run `atlas_test_pr_merged.py` to get authoritative state
2. Check GraphQL output for actual merge state
3. If truly not merged, check `atlas_test_pr_merge_ready.py` for blockers

### Auto-merge not triggering

1. Verify repository has auto-merge enabled in settings
2. Check branch protection rules allow auto-merge
3. Verify required status checks are configured
4. Use `atlas_test_pr_merge_ready.py` to see blocking reasons

### Merge state showing UNKNOWN

This is temporary - GitHub is computing the merge state. Wait 5-10 seconds and retry. The scripts handle this with automatic retries.

### Protected branch preventing merge

Check:
1. Required status checks passing
2. Required number of approvals met
3. Allowed merge methods in branch protection
4. No CODEOWNERS blocking reviews

## Script Locations

All scripts are in the `scripts/` directory of this skill:

```
scripts/
├── atlas_test_pr_merged.py      # Check if PR is merged
├── atlas_test_pr_merge_ready.py # Check merge eligibility
├── atlas_merge_pr.py            # Execute merge
└── atlas_set_auto_merge.py      # Enable/disable auto-merge
```

Each script outputs JSON to stdout for easy parsing by automation tools.
