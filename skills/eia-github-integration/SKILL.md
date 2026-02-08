---
name: eia-github-integration
description: "Use when integrating GitHub Projects. Trigger with GitHub sync, label setup, or PR workflow requests."
license: Apache-2.0
compatibility: Requires GitHub CLI version 2.14 or higher, GitHub account with write permissions to target repositories, and basic Git knowledge. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
workflow-instruction: "support"
procedure: "support-skill"
user-invocable: false
---

# GitHub Integration Dispatcher

## Overview

This skill is the **entry point** for all GitHub integration tasks in agent orchestration workflows. It routes you to specialized skills based on your task type. Use this skill to determine which specialized GitHub skill to invoke.

## Prerequisites

Before using any GitHub integration skill, ensure:
1. GitHub CLI version 2.14 or higher is installed (`gh --version`)
2. GitHub CLI is authenticated (`gh auth status`)
3. You have write permissions to the target repository
4. Basic familiarity with Git commands

**First-time setup:**
```bash
# Install GitHub CLI
brew install gh   # macOS
# or see https://cli.github.com/manual/installation for other platforms

# Authenticate
gh auth login

# Verify authentication
gh auth status
```

**For detailed setup instructions**, see [references/prerequisites-and-setup.md](references/prerequisites-and-setup.md).

## Decision Tree: Which Skill to Use?

Use this decision tree to route to the appropriate specialized skill:

### I need to work with Pull Requests

**→ Use `eia-github-pr-workflow`**

This skill covers:
- Creating pull requests linked to issues
- PR status monitoring and CI/CD integration
- Merge strategies (squash, merge commit, rebase)
- Auto-merge configuration
- PR workflow automation

### I need to sync with GitHub Projects V2

**→ Use `eia-github-projects-sync`**

This skill covers:
- Bidirectional synchronization between agent tasks and GitHub Projects V2
- Creating and configuring project boards
- Status column management (Backlog, Ready, In Progress, In Review, Done)
- Custom field configuration (Priority, Due Date, Effort)
- Automation rules (auto-add, auto-archive, status transitions)
- Conflict resolution and sync health monitoring

### I need to orchestrate Kanban board operations

**→ Use `eia-kanban-orchestration`**

This skill covers:
- Managing the 9-label classification system (feature, bug, refactor, test, docs, performance, security, dependencies, workflow)
- Issue lifecycle management across Kanban columns
- Label-based filtering and reporting
- Kanban-specific automation patterns

### I need to use Git worktrees for parallel work

**→ Use `eia-git-worktree-operations`**

This skill covers:
- Creating and managing Git worktrees for parallel feature development
- Worktree-based PR workflows
- Cleanup and maintenance of worktrees

### I need to perform GitHub API operations

**→ See [references/api-operations.md](references/api-operations.md)**

This reference covers:
- Direct GitHub API calls (REST and GraphQL)
- Authentication methods (token, app, OAuth)
- Rate limiting and pagination
- Webhook configuration
- Advanced query patterns

### I need to manage multiple GitHub identities

**→ See [references/multi-user-workflow.md](references/multi-user-workflow.md)**

This reference covers:
- SSH key setup for multiple accounts
- SSH host aliases configuration
- GitHub CLI multi-account authentication
- Identity switching and repository configuration
- Using the `gh_multiuser.py` script for automated identity management

## Batch Operations (Unique to This Skill)

When you need to perform operations that span multiple GitHub areas (e.g., bulk label changes across issues AND PRs, or cross-project synchronization):

### Batch Label Operations

**Reference:** [references/batch-operations.md](references/batch-operations.md)

Use when:
- Updating labels on multiple issues simultaneously
- Bulk closing stale issues
- Filtering by multiple criteria (label + status + assignee + date)
- Previewing changes before executing (dry-run mode)
- Creating audit trails for batch operations

**Quick example:**
```bash
# Bulk add label to all open issues with "feature" label
gh issue list --label "feature" --state open --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "priority:high"
```

### Automation Scripts

**Reference:** [references/automation-scripts.md](references/automation-scripts.md)

Use when:
- Syncing GitHub Projects V2 with agent tasks (`sync-projects-v2.py`)
- Bulk assigning labels at scale (`bulk-label-assignment.py`)
- Monitoring PR status and CI/CD failures (`monitor-pull-requests.py`)
- Importing issues from CSV/JSON (`bulk-create-issues.py`)
- Generating project status reports (`generate-project-report.py`)

## Troubleshooting

If you encounter issues with any GitHub integration task, see [references/troubleshooting.md](references/troubleshooting.md) for:
- Authentication failures and re-authentication
- Projects V2 synchronization issues
- Pull request linking problems
- Label system issues
- GitHub CLI installation and PATH issues
- API rate limiting
- Webhook delivery failures

## Resources

**Core References:**
- [references/prerequisites-and-setup.md](references/prerequisites-and-setup.md) - GitHub CLI installation and authentication
- [references/multi-user-workflow.md](references/multi-user-workflow.md) - Managing multiple GitHub identities
- [references/api-operations.md](references/api-operations.md) - Direct API operations
- [references/batch-operations.md](references/batch-operations.md) - Bulk operations and filtering
- [references/automation-scripts.md](references/automation-scripts.md) - Python automation scripts
- [references/troubleshooting.md](references/troubleshooting.md) - Common issues and solutions

**Specialized Skills:**
- `eia-github-pr-workflow` - Pull request operations
- `eia-github-projects-sync` - Projects V2 bidirectional synchronization
- `eia-kanban-orchestration` - Kanban board and 9-label system management
- `eia-git-worktree-operations` - Git worktree management

---

**Skill Version:** 2.0.0
**Last Updated:** 2026-02-05
**Maintainer:** Skill Development Team
**Changelog:**
- 2.0.0: Refactored as thin dispatcher to specialized skills, removed duplicated content
- 1.2.0: Added cross-platform `gh_multiuser.py` script with configuration-driven identity management
- 1.1.0: Added Multi-User Workflow reference for owner/developer identity separation
