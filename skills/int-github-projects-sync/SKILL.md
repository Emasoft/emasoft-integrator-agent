---
name: ao-github-projects-sync
description: Manages team tasks through GitHub Projects V2, enabling ATLAS-ORCHESTRATOR to track features, bugs, PRs, and issues with automatic CI integration. Provides GraphQL API operations for issue creation, status updates, and project synchronization across remote developer agents.
license: Apache-2.0
compatibility: "Requires GitHub CLI authentication, GitHub Projects V2 enabled repository, GraphQL API access, Python 3.8+, and AI Maestro integration for notifications"
metadata:
  author: Anthropic
  version: 1.0.0
agent: api-coordinator
context: fork
---

# GitHub Projects Sync

## Overview

The GitHub Projects Sync skill enables the ATLAS-ORCHESTRATOR to manage team tasks through GitHub Projects V2. This is the OFFICIAL task management interface for coordinating work across remote developer agents.

**Critical Distinction**:
- **GitHub Projects** = Team/Project tasks (features, bugs, PRs, issues)
- **Claude Tasks** = Orchestrator personal tasks ONLY (reading docs, planning, reviewing)

## When to Use

Invoke this skill when:
- Assigning GitHub issues to remote agents
- Tracking feature implementation progress
- Synchronizing PR status with project boards
- Managing sprint/iteration planning
- Generating project status reports
- Coordinating multi-agent work on features

## Iron Rules Compliance

This skill is **READ + STATUS UPDATE ONLY**:
- Query project state via GraphQL API
- Update card status (Todo -> In Progress -> Done)
- Add comments and labels to issues
- Link PRs to project items
- **NEVER**: Execute code, run tests, modify source files

## Quick Start

### Authentication

```bash
# Verify gh CLI is authenticated
gh auth status
```

### Find Your Project

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectsV2(first: 10) {
        nodes { id title number }
      }
    }
  }
'
```

## Reference Documentation

All detailed operations, templates, and scripts are organized in reference files below. Each section shows WHEN to read that reference and its contents.

---

### Core Operations ([references/core-operations.md](references/core-operations.md))

Read this when performing day-to-day GitHub Projects operations.

**Contents:**
- 1.1 When starting with GitHub Projects operations
- 1.2 When creating issues with project items
- 1.3 When updating project item status
- 1.4 When querying all project items
- 1.5 When linking PRs to issues
- 1.6 When adding comments to issues
- 1.7 When managing assignees

---

### GraphQL API Queries ([references/graphql-queries.md](references/graphql-queries.md))

Read this when you need complete GraphQL query/mutation syntax.

**Index File Contents:**
- Links to read operations (project discovery, fields, items, issues, PRs)
- Links to mutations (create, update, archive items)

**Sub-Files:**
- [graphql-queries-part1-read-operations.md](references/graphql-queries-part1-read-operations.md) - All read queries
- [graphql-queries-part2-mutations.md](references/graphql-queries-part2-mutations.md) - All mutations

---

### Status Management ([references/status-management.md](references/status-management.md))

Read this when managing issue/item status transitions.

**Contents:**
- 3.1 When starting with status management
- 3.2 When you need to understand status meanings and metadata
- 3.3 When moving issues between statuses (transition rules)
- 3.4 When syncing GitHub state with project board
- 3.5 When updating status via API or scripts
- 3.6 When generating status reports or summaries
- 3.7 When issues need attention or escalation
- 3.8 When deciding whether to close inactive issues (NO STALE policy)
- 3.9 When following status management best practices

**Standard Columns:** Backlog -> Todo -> In Progress -> In Review -> Done (+ Blocked)

---

### Label Taxonomy ([references/label-taxonomy.md](references/label-taxonomy.md))

Read this when classifying or filtering issues by labels.

**Contents:**
- 4.1 When starting with the label system
- 4.2 When you need to know available label categories
- 4.3 When creating or managing labels via CLI
- 4.4 When applying labels automatically or manually
- 4.5 When searching or filtering issues by labels
- 4.6 When generating label statistics and counts
- 4.7 When following label usage best practices
- 4.8 When choosing label colors

**Label Categories:** type:*, priority:*, status:*, component:*, effort:*, agent:*, review:*

---

### Issue Templates ([references/issue-templates.md](references/issue-templates.md))

Read this when creating issues or setting up repository templates.

**Contents:**
- 5.1 When starting with issue templates
- 5.2 When setting up template file structure
- 5.3 When configuring template options
- 5.4 When creating feature request issues
- 5.5 When reporting bugs
- 5.6 When creating large multi-issue features (epics)
- 5.7 When proposing code refactoring
- 5.8 When requesting documentation improvements
- 5.9 When opening pull requests
- 5.10 When defining code ownership (CODEOWNERS)
- 5.11 When creating issues via GitHub CLI

---

### Sub-Issue Tracking ([references/sub-issue-tracking.md](references/sub-issue-tracking.md))

Read this when breaking down large features into smaller tasks.

**Contents:**
- 6.1 When breaking down large features into sub-issues
- 6.2 When creating parent/child issue relationships
- 6.3 When tracking progress across sub-issues
- 6.4 When automating progress updates
- 6.5 When using task lists for tracking
- 6.6 When querying sub-issue status

---

### Skill Integrations ([references/skill-integrations.md](references/skill-integrations.md))

Read this when coordinating GitHub Projects with other ATLAS skills.

**Contents:**
- 7.1 When integrating GitHub Projects with other ATLAS skills
- 7.2 When coordinating with Remote Agent Coordinator
- 7.3 When working with Code Reviewer skill
- 7.4 When generating reports
- 7.5 When using AI Maestro messaging
- 7.6 When syncing with Claude Tasks

---

### CI Notification Setup ([references/ci-notification-setup.md](references/ci-notification-setup.md))

Read this when configuring webhooks for CI/project sync.

**Contents:**
- 8.1 When understanding CI notification system
- 8.2 When configuring GitHub webhooks
- 8.3 When understanding event types and notifications
- 8.4 When customizing notification configuration
- 8.5 If webhook delivery or notification issues occur
- 8.6 When ensuring webhook security
- 8.7 When handling multiple repositories
- 8.8 When integrating CI events with project sync

---

### Error Handling ([references/error-handling.md](references/error-handling.md))

Read this when encountering API errors or failures.

**Contents:**
- 9.1 When encountering GitHub API errors
- 9.2 When hitting rate limits
- 9.3 When project or item is not found
- 9.4 When item updates fail
- 9.5 When authentication fails
- 9.6 When webhook delivery fails
- 9.7 When implementing retry logic

---

### Best Practices ([references/best-practices.md](references/best-practices.md))

Read this before starting work and when unsure about procedures.

**Contents:**
- 10.1 When following GitHub Projects best practices
- 10.2 When managing project board state (DO)
- 10.3 When handling issues and PRs (DO)
- 10.4 When avoiding common mistakes (DON'T)
- 10.5 When handling inactive issues (lifecycle reminders)
- 10.6 When documenting changes

---

### Automation Scripts ([references/automation-scripts.md](references/automation-scripts.md))

Read this when using the included Python automation scripts.

**Contents:**
- 11.1 When using skill automation scripts
- 11.2 When bulk creating issues from task lists (sync_tasks.py)
- 11.3 When receiving GitHub webhook events (ci_webhook_handler.py)
- 11.4 When synchronizing project with CI status (kanban_sync.py)
- 11.5 When configuring shared thresholds

---

### Planning & Iteration ([references/planning-phase-mapping.md](references/planning-phase-mapping.md))

Read this when mapping planning phases to GitHub status.

**Contents:**
- Phase-to-Status Mapping
- Automatic Transitions
- Manual Override Rules

See also: [references/iteration-cycle-rules.md](references/iteration-cycle-rules.md) for sprint/iteration management.

---

### Review & Plan Files

- [references/review-worktree-workflow.md](references/review-worktree-workflow.md) - Isolated review environment setup
- [references/plan-file-linking.md](references/plan-file-linking.md) - GitHub issue to plan file linking

---

## Issue Lifecycle Policy (NO STALE)

**IRON RULE**: Issues are NEVER automatically closed due to inactivity.

| Issue Type | Closure Conditions |
|------------|-------------------|
| Feature | Implemented + merged, OR explicitly declined with reason |
| Bug | Fixed + verified, OR 3 documented reproduction attempts failed |
| Chore | Completed and verified |

For inactive issues, use labels (`needs-attention`, `awaiting-response`, `low-priority`) instead of closing.

See [references/status-management.md](references/status-management.md#issue-lifecycle-policy-no-stale) for complete policy.

---

## AI Maestro Integration

For all inter-agent messaging, refer to the official AI Maestro skill:
```
~/.claude/skills/agent-messaging/SKILL.md
```

Use official CLI scripts for notifications:
```bash
send-aimaestro-message.sh orchestrator-master "Subject" '{"type":"TYPE","message":"MSG"}' priority type
```

---

## Threshold Configuration

The `../shared/thresholds.py` module defines automation thresholds:

| Threshold | Value | Purpose |
|-----------|-------|---------|
| MAX_CONSECUTIVE_FAILURES | 3 | CI failures before escalation |
| INACTIVE_HOURS | 24 | Hours before flagging inactive items |
| LONG_REVIEW_HOURS | 48 | Hours before review escalation |
| BLOCKED_ESCALATION_HOURS | 72 | Hours before user escalation |

See [references/automation-scripts.md](references/automation-scripts.md#thresholds-configuration) for usage.

---

## Skill Files

```
github-projects-sync/
├── SKILL.md                          # This file (map/TOC)
├── scripts/
│   ├── sync_tasks.py                 # Bulk issue creation
│   ├── ci_webhook_handler.py         # Webhook receiver
│   └── kanban_sync.py                # CI status sync
├── references/
│   ├── core-operations.md            # Day-to-day operations
│   ├── graphql-queries-index.md      # GraphQL library index
│   ├── graphql-queries-part1-*.md    # Read operations
│   ├── graphql-queries-part2-*.md    # Mutations
│   ├── status-management.md          # Status transitions & lifecycle
│   ├── label-taxonomy.md             # Label system
│   ├── issue-templates.md            # Issue/PR templates
│   ├── sub-issue-tracking.md         # Epic/sub-issue management
│   ├── skill-integrations.md         # ATLAS skill integration
│   ├── ci-notification-setup.md      # Webhook configuration
│   ├── error-handling.md             # Error handling patterns
│   ├── best-practices.md             # Best practices guide
│   ├── automation-scripts.md         # Script documentation
│   ├── planning-phase-mapping.md     # Planning phase mapping
│   ├── iteration-cycle-rules.md      # Sprint/iteration rules
│   ├── review-worktree-workflow.md   # Review environment
│   └── plan-file-linking.md          # Plan file linking
└── ../shared/
    ├── thresholds.py                 # Automation thresholds
    └── aimaestro_notify.py           # AI Maestro CLI wrapper
```

---

## Troubleshooting

### Issue: Cannot find GitHub Project

**Cause**: Project ID incorrect or insufficient permissions.

**Solution**:
1. Verify project ID format: `PVT_kwDO...` for Projects V2
2. Check token has `project` scope
3. Use `gh project list --owner OWNER` to find correct ID
4. Ensure project is not archived

### Issue: Issue not appearing on project board

**Cause**: Issue not added to project or field values not set.

**Solution**:
1. Verify issue is added to project: `gh project item-list PROJECT_ID`
2. Check required fields (Status, Priority) have values
3. Add issue manually: `gh project item-add PROJECT_ID --url ISSUE_URL`
4. Set field values: `gh project item-edit --id ITEM_ID --field-id FIELD_ID --value VALUE`

### Issue: Column/status sync fails

**Cause**: Field IDs changed or column names don't match.

**Solution**:
1. Get current field IDs: `gh project field-list PROJECT_ID`
2. Update local configuration with correct field IDs
3. Ensure status values match exactly (case-sensitive)
4. Check for renamed or deleted columns

### Issue: Rate limiting from GitHub API

**Cause**: Too many API calls in short period.

**Solution**:
1. Check rate limit status: `gh api rate_limit`
2. Implement caching for frequently accessed data
3. Batch operations where possible
4. Wait for rate limit reset (shown in API response)

### Issue: Claude Tasks and GitHub Project out of sync

**Cause**: Manual changes on one side not reflected on other.

**Solution**:
1. Run sync script to reconcile differences
2. Claude Tasks are for personal/local tasks, GitHub for shared tasks
3. Prioritize GitHub as source of truth for team visibility
4. Use `/orchestration-status` to see unified view
