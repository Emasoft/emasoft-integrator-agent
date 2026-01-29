---
name: eia-github-issue-operations
description: Comprehensive GitHub Issue management including creation, labels, milestones, assignees, and comments using gh CLI
license: Apache-2.0
metadata:
  version: "1.0.0"
  author: Integrator Agent Team
  category: github
  tags:
    - github
    - issues
    - labels
    - milestones
    - project-management
  requires_tools:
    - gh
    - jq
agent: api-coordinator
context: fork
---

# GitHub Issue Operations Skill

## Overview

This skill provides complete GitHub Issue management capabilities for orchestrator agents. It enables programmatic issue creation, labeling, milestone tracking, assignee management, and comment posting using the `gh` CLI tool.

**When to use this skill:**
- Creating issues from automated workflows
- Managing issue labels and categorization
- Tracking progress via milestones
- Posting automated comments or status updates
- Querying issue metadata and context

## Prerequisites

Before using this skill, ensure:
1. `gh` CLI is installed and authenticated (`gh auth status`)
2. You have write access to the target repository
3. `jq` is available for JSON processing

## Decision Tree: Which Operation Do I Need?

```
Need to work with GitHub Issues?
│
├─► Need issue information?
│   └─► Use: atlas_get_issue_context.py
│       Returns: title, body, state, labels, assignees, milestone, comments count, linked PRs
│
├─► Need to create a new issue?
│   └─► Use: atlas_create_issue.py
│       Requires: --title, optional: --body, --labels, --assignee
│       Returns: issue number and URL
│
├─► Need to manage labels?
│   ├─► Adding labels? → atlas_set_issue_labels.py --add "label1,label2"
│   ├─► Removing labels? → atlas_set_issue_labels.py --remove "label1"
│   └─► Setting exact labels? → atlas_set_issue_labels.py --set "label1,label2"
│       Note: Auto-creates missing labels if they don't exist
│
├─► Need to assign to milestone?
│   └─► Use: atlas_set_issue_milestone.py
│       Option: --create-if-missing to auto-create milestone
│
└─► Need to post a comment?
    └─► Use: atlas_post_issue_comment.py
        Option: --marker for idempotent comments (won't duplicate)
```

## Reference Documents

### Label Management
**File:** [references/label-management.md](references/label-management.md)

**Contents:**
- 1.1 Creating labels via GitHub API
  - 1.1.1 Using gh CLI to create labels
  - 1.1.2 Specifying label colors
  - 1.1.3 Adding label descriptions
- 1.2 Label naming conventions
  - 1.2.1 Kebab-case standard
  - 1.2.2 Category prefixes
- 1.3 Priority labels (P0-P4)
  - 1.3.1 Priority definitions
  - 1.3.2 Color scheme for priorities
  - 1.3.3 When to use each priority
- 1.4 Category labels
  - 1.4.1 Type labels (bug, feature, task, docs)
  - 1.4.2 Status labels (in-progress, blocked, review)
  - 1.4.3 Component labels
- 1.5 Auto-creating missing labels
  - 1.5.1 Detection logic
  - 1.5.2 Default colors and descriptions

### Issue Templates
**File:** [references/issue-templates.md](references/issue-templates.md)

**Contents:**
- 2.1 Bug report template
  - 2.1.1 Required sections
  - 2.1.2 Environment information
  - 2.1.3 Reproduction steps format
- 2.2 Feature request template
  - 2.2.1 Problem statement
  - 2.2.2 Proposed solution
  - 2.2.3 Acceptance criteria
- 2.3 Task template
  - 2.3.1 Task description format
  - 2.3.2 Checklist syntax
  - 2.3.3 Dependencies section
- 2.4 Populating templates programmatically
  - 2.4.1 Variable substitution
  - 2.4.2 Dynamic content injection
  - 2.4.3 Template selection logic

### Milestone Tracking
**File:** [references/milestone-tracking.md](references/milestone-tracking.md)

**Contents:**
- 3.1 Creating milestones
  - 3.1.1 Milestone title conventions
  - 3.1.2 Setting due dates
  - 3.1.3 Milestone descriptions
- 3.2 Assigning issues to milestones
  - 3.2.1 Single issue assignment
  - 3.2.2 Bulk assignment
  - 3.2.3 Moving between milestones
- 3.3 Milestone progress tracking
  - 3.3.1 Querying completion percentage
  - 3.3.2 Open vs closed issues count
  - 3.3.3 Overdue detection
- 3.4 Closing milestones
  - 3.4.1 When to close
  - 3.4.2 Handling incomplete issues
  - 3.4.3 Archive vs delete

## Script Reference Table

| Script | Purpose | Required Args | Optional Args | Output |
|--------|---------|---------------|---------------|--------|
| `atlas_get_issue_context.py` | Get issue metadata | `--repo`, `--issue` | `--include-comments` | JSON with issue details |
| `atlas_create_issue.py` | Create new issue | `--repo`, `--title` | `--body`, `--labels`, `--assignee`, `--milestone` | JSON with number, URL |
| `atlas_set_issue_labels.py` | Manage labels | `--repo`, `--issue` | `--add`, `--remove`, `--set`, `--auto-create` | JSON with updated labels |
| `atlas_set_issue_milestone.py` | Assign milestone | `--repo`, `--issue`, `--milestone` | `--create-if-missing` | JSON with milestone info |
| `atlas_post_issue_comment.py` | Post comment | `--repo`, `--issue`, `--body` | `--marker` | JSON with comment ID, URL |

## Usage Examples

### Get Issue Context

```bash
# Get full issue context
./scripts/atlas_get_issue_context.py --repo owner/repo --issue 123

# Output:
{
  "number": 123,
  "title": "Bug: Application crashes on startup",
  "state": "open",
  "labels": ["bug", "P1"],
  "assignees": ["developer1"],
  "milestone": "v2.0",
  "comments_count": 5,
  "linked_prs": [456, 789]
}
```

### Create Issue

```bash
# Create issue with labels and assignee
./scripts/atlas_create_issue.py \
  --repo owner/repo \
  --title "Implement new feature X" \
  --body "## Description\nFeature details here" \
  --labels "feature,P2" \
  --assignee "developer1"

# Output:
{
  "number": 124,
  "url": "https://github.com/owner/repo/issues/124"
}
```

### Manage Labels

```bash
# Add labels (auto-creates if missing)
./scripts/atlas_set_issue_labels.py \
  --repo owner/repo \
  --issue 123 \
  --add "in-progress,needs-review" \
  --auto-create

# Remove labels
./scripts/atlas_set_issue_labels.py \
  --repo owner/repo \
  --issue 123 \
  --remove "needs-triage"
```

### Assign Milestone

```bash
# Assign to existing milestone
./scripts/atlas_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v2.0"

# Create milestone if it doesn't exist
./scripts/atlas_set_issue_milestone.py \
  --repo owner/repo \
  --issue 123 \
  --milestone "v3.0" \
  --create-if-missing
```

### Post Idempotent Comment

```bash
# Post comment with marker (won't duplicate if marker exists)
./scripts/atlas_post_issue_comment.py \
  --repo owner/repo \
  --issue 123 \
  --body "## Status Update\nTask completed successfully." \
  --marker "status-update-2024-01-15"

# Output:
{
  "comment_id": 12345,
  "url": "https://github.com/owner/repo/issues/123#issuecomment-12345",
  "created": true  # false if marker already existed
}
```

## Error Handling

All scripts return JSON with an `error` field on failure:

```json
{
  "error": true,
  "message": "Issue not found: 999",
  "code": "ISSUE_NOT_FOUND"
}
```

Common error codes:
- `AUTH_REQUIRED`: gh CLI not authenticated
- `REPO_NOT_FOUND`: Repository doesn't exist or no access
- `ISSUE_NOT_FOUND`: Issue number doesn't exist
- `LABEL_CREATE_FAILED`: Failed to create label
- `MILESTONE_NOT_FOUND`: Milestone doesn't exist (without --create-if-missing)
- `PERMISSION_DENIED`: Insufficient permissions

## Exit Codes (Standardized)

All scripts use standardized exit codes for consistent error handling:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Invalid parameters | Missing required args, bad format |
| 2 | Resource not found | Issue, repo, milestone, or labels not found |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | Comment with marker already exists |
| 6 | Not mergeable | N/A for these scripts |

**Note:** `atlas_post_issue_comment.py` returns exit code 5 when a comment with the specified `--marker` already exists. The JSON output will have `"created": false`.

## Troubleshooting

### Issue: "gh: command not found"

**Solution:** Install gh CLI:
```bash
# macOS
brew install gh

# Linux
sudo apt install gh  # Debian/Ubuntu
sudo dnf install gh  # Fedora
```

### Issue: "not logged into any GitHub hosts"

**Solution:** Authenticate with gh:
```bash
gh auth login
```

### Issue: Labels not being created

**Solution:** Ensure you have write access to the repository. Label creation requires at least "triage" permission level.

### Issue: Milestone assignment fails silently

**Solution:** Check that the milestone exists. Use `--create-if-missing` flag or create the milestone first via GitHub UI or API.

### Issue: Duplicate comments being posted

**Solution:** Use the `--marker` flag with a unique identifier. The script checks for existing comments containing the marker before posting.

## Integration with Integrator Agent

This skill integrates with the Integrator Agent workflow:

1. **Task Creation:** When orchestrator receives a new task, use `atlas_create_issue.py` to create a tracking issue
2. **Progress Updates:** Use `atlas_post_issue_comment.py` with markers to post status updates
3. **Completion:** Use `atlas_set_issue_labels.py` to mark issues as completed
4. **Milestone Tracking:** Use `atlas_set_issue_milestone.py` to organize work into releases

See the main Integrator Agent documentation for workflow integration details.
