---
name: eia-github-integration
description: "Use when integrating GitHub Projects. Trigger with GitHub sync, label setup, or PR workflow requests."
license: Apache-2.0
compatibility: Requires GitHub CLI version 2.14 or higher, GitHub account with write permissions to target repositories, and basic Git knowledge. Requires AI Maestro installed.
metadata:
  author: Anthropic
  version: 1.0.0
agent: api-coordinator
context: fork
---

# GitHub Integration for Agent Orchestration

## Overview

This skill provides agents and orchestrators with complete GitHub integration capabilities for managing development workflows at scale. It covers GitHub Projects V2 bidirectional synchronization, a standardized 9-label classification system, pull request workflow management, and comprehensive issue tracking for orchestrator-driven development.

## Prerequisites

Before using this skill, ensure:
1. GitHub CLI version 2.14 or higher is installed (`gh --version`)
2. GitHub CLI is authenticated (`gh auth status`)
3. You have write permissions to the target repository
4. Basic familiarity with Git commands

## Instructions

1. Authenticate GitHub CLI using the [Prerequisites and Setup](#prerequisites-and-setup) reference
2. Create the 9-label system in your repository using [Core Concepts](#core-concepts)
3. Create and configure a Projects V2 board using [Projects V2 Operations](#projects-v2-operations)
4. Create issues with proper labels using [Issue Management](#issue-management)
5. Create and link pull requests to issues using [Pull Request Management](#pull-request-management)
6. Set up bidirectional synchronization using [Projects V2 Operations](#projects-v2-operations)
7. Automate workflows using scripts from [Automation Scripts](#automation-scripts)
8. Monitor and troubleshoot using [Error Handling](#error-handling)

### Checklist

Copy this checklist and track your progress:

- [ ] Authenticate GitHub CLI: `gh auth login`
- [ ] Verify authentication: `gh auth status`
- [ ] Create 9-label system in repository (feature, bug, refactor, test, docs, performance, security, dependencies, workflow)
- [ ] Create Projects V2 board: `gh project create --title "<name>" --owner "@username"`
- [ ] Configure project status columns (Backlog, Ready, In Progress, In Review, Done)
- [ ] Create issues with proper labels: `gh issue create --title "..." --body "..." --label "<label>" --project "<number>"`
- [ ] Create PRs linked to issues: `gh pr create --title "..." --body "Closes #<issue>" --head "<branch>"`
- [ ] Set up bidirectional synchronization scripts
- [ ] Configure automation rules (auto-add, auto-archive, status transitions)
- [ ] Test workflow: create issue → create PR → merge → verify issue closes
- [ ] Monitor sync health and troubleshoot any issues

## Output

| Output Type | Format | Location | Description |
|-------------|--------|----------|-------------|
| GitHub Issues | Web UI / JSON | `https://github.com/owner/repo/issues` | Created issues with labels and project assignments |
| Pull Requests | Web UI / JSON | `https://github.com/owner/repo/pulls` | PRs linked to issues with auto-close syntax |
| Projects V2 Board | Web UI / GraphQL | `https://github.com/users/username/projects/N` | Kanban board with bidirectional sync |
| Issue Numbers | CLI Output | stdout | `#123` issue number returned after creation |
| PR Numbers | CLI Output | stdout | `#456` PR number returned after creation |
| Sync Reports | JSON / Text | Agent logs or file | Synchronization status and conflicts |
| Automation Logs | Text / JSON | Script output files | Results from batch operations and automation scripts |
| Label List | CLI Output | stdout | List of configured labels with colors and descriptions |

## Quick Start

**First-time setup (5 minutes):**
1. Install GitHub CLI: `brew install gh` (macOS) or see [Prerequisites and Setup](#prerequisites-and-setup)
2. Authenticate: `gh auth login`
3. Create 9 labels in your repository (see [Core Concepts](#core-concepts))
4. Create Projects V2 board: `gh project create --title "Project Name" --owner "@username"`

**Daily workflow:**
1. Create issue: `gh issue create --title "..." --body "..." --label "feature" --project "1"`
2. Create PR: `gh pr create --title "..." --body "Closes #123" --head "feature/issue-123"`
3. Merge PR: `gh pr merge 123 --squash --delete-branch`

## Core Workflow Sequence

This skill teaches GitHub integration in the following order:

1. **Authentication** → Set up GitHub CLI access
2. **Labels** → Create and use the 9-label system
3. **Projects V2** → Create and configure project boards
4. **Issues** → Create, manage, and track issues
5. **Pull Requests** → Automate PR creation and linking
6. **Synchronization** → Bidirectionally sync with agent tasks
7. **Automation** → Use scripts for batch operations

## Reference Documentation Structure

Each reference document focuses on a specific aspect of GitHub integration. Read them in order for initial setup, or jump directly to the relevant section when you need specific information.

---

## Prerequisites and Setup

**Reference:** [references/prerequisites-and-setup.md](references/prerequisites-and-setup.md)

**Use-Case TOC:**
- When you need to authenticate GitHub CLI → GitHub CLI Authentication
- When you need to verify authentication status → Verify Authentication
- If authentication fails or is expired → Re-authentication
- When setting up a new machine or environment → Initial Setup Requirements

**What you'll learn:**
- Installing GitHub CLI on macOS, Linux, Windows
- Authenticating with web-based login, SSH, or personal access token
- Verifying authentication is working correctly
- Troubleshooting common authentication issues
- Security best practices for token management

---

## Multi-User Workflow

**Reference:** [references/multi-user-workflow.md](references/multi-user-workflow.md)

**Use-Case TOC:**
- When you need multiple GitHub identities on the same machine → Why Multiple Identities
- When setting up SSH keys for a secondary account → SSH Key Setup
- When configuring SSH host aliases → SSH Host Aliases
- When authenticating multiple accounts with gh CLI → GitHub CLI Multi-Account Setup
- When switching between GitHub identities → Identity Switching
- When configuring a repository for a specific identity → Repository Identity Configuration
- When running commands as a specific user → Per-Command Identity Override
- When adding collaborators to a repository → Collaborator Management
- When troubleshooting identity issues → Troubleshooting

**What you'll learn:**
- Why multiple identities are needed (owner/developer separation, agent orchestration)
- Setting up SSH keys for each GitHub account
- Configuring SSH host aliases in `~/.ssh/config`
- Authenticating multiple accounts with GitHub CLI
- Switching between identities quickly with shell helper functions
- Configuring repositories for specific identities (git config, remote URLs)
- Running single commands as a specific user without switching
- Managing collaborators and accepting invitations
- Troubleshooting common identity issues (wrong user, permission denied)

---

## Core Concepts

**Reference:** [references/core-concepts.md](references/core-concepts.md)

**Use-Case TOC:**
- When you need to understand GitHub Projects V2 → What is GitHub Projects V2
- When you need to understand the label system → The 9-Label System
- When you need to understand synchronization → Bidirectional Synchronization
- When choosing which label to use → Label Selection Guide

**What you'll learn:**
- What GitHub Projects V2 is and why it's better than legacy Projects
- The 9-label system: feature, bug, refactor, test, docs, performance, security, dependencies, workflow
- When to use each label (decision table included)
- How bidirectional synchronization works (agent ↔ GitHub)
- Conflict resolution rules when both systems update simultaneously

---

## Issue Management

**Reference:** [references/issue-management.md](references/issue-management.md)

**Use-Case TOC:**
- When you need to create a new issue → Creating Issues
- When you need to assign labels → Assigning Labels
- When you need to update issue status → Issue Lifecycle
- When you need to link issues to pull requests → Linking Issues to PRs
- When you need to close an issue → Closing Issues
- If you need to create multiple issues → Batch Issue Creation

**What you'll learn:**
- Creating issues with proper labels and descriptions
- Writing effective issue titles and acceptance criteria
- Assigning issues to team members
- Managing issue lifecycle (Backlog → Ready → In Progress → In Review → Done)
- Linking issues to pull requests with "Closes #123" syntax
- Closing issues manually or automatically via PR merge
- Batch issue creation from CSV or scripts

---

## Pull Request Management

**Reference:** [references/pull-request-management.md](references/pull-request-management.md)

**Use-Case TOC:**
- When you need to create a pull request → Creating Pull Requests
- When you need to link PR to an issue → Linking PRs to Issues
- When you need to monitor PR status → Monitoring PR Status
- When PR checks fail → Handling Failed Checks
- When you need to merge a PR → Merging Pull Requests
- When you need to automate PR workflow → PR Workflow Automation

**What you'll learn:**
- Creating pull requests with proper linking to issues
- Using "Closes #123" syntax to auto-close issues
- Monitoring PR status and CI/CD checks
- Handling failed checks and test failures
- Merge strategies: squash, merge commit, rebase
- Enabling auto-merge for approved PRs
- Automating PR creation from agent tasks

---

## Projects V2 Operations

**Reference:** [references/projects-v2-operations.md](references/projects-v2-operations.md)

**Use-Case TOC:**
- When you need to create a new project board → Creating Projects V2 Board
- When you need to add issues to a project → Adding Issues to Projects
- When you need to update issue status → Updating Issue Status
- When you need to configure project fields → Configuring Custom Fields
- When you need to set up automation → Setting Up Automation Rules
- When you need to sync agent tasks with GitHub → Bidirectional Sync Workflow

**What you'll learn:**
- Creating and configuring Projects V2 boards
- Adding issues and pull requests to projects
- Defining custom status columns (Backlog, Ready, In Progress, In Review, Done)
- Configuring custom fields (Priority, Due Date, Effort)
- Setting up automation rules (auto-add, auto-archive, status transitions)
- Bidirectional synchronization between agent tasks and GitHub
- Conflict resolution and sync health monitoring

---

## Batch Operations and Filtering

**Reference:** [references/batch-operations.md](references/batch-operations.md)

**Use-Case TOC:**
- When you need to filter issues by label → Filtering by Label
- When you need to update multiple issues → Batch Issue Updates
- When you need to change labels on many issues → Bulk Label Operations
- When you need to bulk close issues → Bulk Closing Issues
- When you need to verify changes before executing → Safe Batch Operations
- When you need to filter by multiple criteria → Advanced Filtering

**What you'll learn:**
- Filtering issues by label, status, assignee, date
- Combining filters for complex queries
- Updating labels on multiple issues simultaneously
- Bulk closing stale issues
- Previewing changes before executing (dry-run mode)
- Creating audit trails for batch operations
- Implementing rollback capabilities
- Best practices for safe batch operations

---

## Automation Scripts

**Reference:** [references/automation-scripts.md](references/automation-scripts.md)

**Use-Case TOC:**
- When you need to sync GitHub Projects V2 with agent tasks → Sync Projects V2 Script
- When you need to bulk assign labels → Bulk Label Assignment Script
- When you need to monitor PR status → Pull Request Monitor Script
- When you need to create issues from CSV → Bulk Issue Creation Script
- When you need to generate project reports → Project Reporting Script

**What you'll learn:**
- Using `sync-projects-v2.py` for bidirectional synchronization
- Using `bulk-label-assignment.py` to manage labels at scale
- Using `monitor-pull-requests.py` to track PR status and CI/CD failures
- Using `bulk-create-issues.py` to import issues from CSV/JSON
- Using `generate-project-report.py` for status reporting
- Installing and configuring scripts
- Scheduling automated sync with cron
- Script parameters and usage examples

---

## Multi-User Identity Script

**Reference:** [references/script-multi-user-identity.md](references/script-multi-user-identity.md)

**Use-Case TOC:**
- When you need to set up multiple GitHub identities → Installation and Setup
- When you need to generate SSH keys for an identity → Setup Command
- When you need to test SSH connections → Test Command
- When you need to switch between identities → Switch Command
- When you need to configure a repository → Repo Command
- When you need to configure multiple repositories → Bulk-Repo Command
- When you need to check current identity status → Status Command
- When you need to add a new identity → Add Command
- When you need to detect configuration issues → Diagnose Command
- When you need to automatically fix issues → Fix Command
- When troubleshooting identity issues → Troubleshooting

**What you'll learn:**
- Using `gh_multiuser.py` to manage multiple GitHub identities
- Configuring identities in `identities.json`
- Generating and testing SSH keys per identity
- Configuring repositories for specific identities
- Bulk configuring multiple repositories
- Running diagnostics to detect and auto-fix issues
- Integrating with agent orchestration systems

---

## Examples

### Example 1: Create an Issue with Labels and Link to Project

```bash
# Create a feature issue and add to project
gh issue create --title "Add OAuth support" --body "Implement OAuth2 flow" --label "feature" --project "1"

# Output: https://github.com/owner/repo/issues/124
```

### Example 2: Create PR That Closes an Issue

```bash
# Create branch and PR that auto-closes issue
git checkout -b feature/issue-124
# Make changes, commit
gh pr create --title "Add OAuth support" --body "Closes #124" --head "feature/issue-124"

# Merge with squash and delete branch
gh pr merge 124 --squash --delete-branch
```

## Error Handling

**Reference:** [references/troubleshooting.md](references/troubleshooting.md)

**Use-Case TOC:**
- If you get authentication errors → Authentication Issues
- If Projects V2 sync fails → Projects V2 Synchronization Issues
- If pull requests don't link to issues → Pull Request Linking Issues
- If labels are rejected → Label System Issues
- If GitHub CLI commands fail → GitHub CLI Issues
- If API rate limits are hit → Rate Limiting Issues
- If webhooks don't trigger → Webhook Issues

**What you'll learn:**
- Diagnosing and fixing authentication failures
- Resolving sync issues between agent and GitHub
- Fixing pull request linking problems
- Handling missing or rejected labels
- Troubleshooting GitHub CLI installation and PATH issues
- Managing API rate limits and secondary rate limits
- Debugging webhook delivery failures
- General troubleshooting workflow
- Where to get additional help

---

## Implementation Guide

**Reference:** [references/implementation-guide.md](references/implementation-guide.md)

**Use-Case TOC:**
- When you need to implement GitHub integration from scratch → Complete Implementation Checklist
- When you need to integrate with agent orchestrator → Agent Orchestrator Integration
- When you need next steps after setup → Next Steps After Implementation
- When you need to onboard your team → Team Onboarding
- When you need advanced features → Advanced Implementation Topics

**What you'll learn:**
- Complete step-by-step implementation checklist (8 phases)
- Phase 1: Prerequisites and authentication
- Phase 2: Label system setup
- Phase 3: Projects V2 configuration
- Phase 4: Issue workflow implementation
- Phase 5: Pull request workflow setup
- Phase 6: Automation scripts installation
- Phase 7: Team onboarding
- Phase 8: Continuous improvement
- Integration patterns for agent orchestrators
- Monitoring sync health and metrics
- Advanced topics: multi-repository projects, custom GitHub Actions, webhooks

---

## Quick Reference Commands

**Authentication:**
```bash
gh auth login                    # Authenticate GitHub CLI
gh auth status                   # Verify authentication
```

**Issues:**
```bash
gh issue create --title "..." --body "..." --label "feature" --project "1"
gh issue list --label "bug" --state open
gh issue close 123 --comment "Fixed by PR #456"
```

**Pull Requests:**
```bash
gh pr create --title "..." --body "Closes #123" --head "feature/issue-123"
gh pr status
gh pr merge 123 --squash --delete-branch
```

**Projects:**
```bash
gh project create --title "..." --owner "@username"
gh project list --owner "@me"
gh project item-add 1 --url "https://github.com/owner/repo/issues/123"
```

**Labels:**
```bash
gh label create "feature" --color "0e8a16" --description "New feature"
gh label list --limit 100
```

## The 9-Label System at a Glance

| Label | When to Use | Example |
|-------|------------|---------|
| `feature` | New functionality | "Add OAuth authentication" |
| `bug` | Fix defect | "Fix null pointer crash" |
| `refactor` | Improve code quality | "Extract service layer" |
| `test` | Add tests | "Add integration tests" |
| `docs` | Documentation | "Write API documentation" |
| `performance` | Optimize speed | "Reduce load time" |
| `security` | Security hardening | "Add CSRF protection" |
| `dependencies` | Update dependencies | "Upgrade React to v18" |
| `workflow` | CI/CD and tooling | "Add GitHub Actions" |

## Integration with Agent Orchestrators

This skill enables agent orchestrators to:

- **Automate Issue Creation**: Agents create GitHub issues directly from tasks
- **Track Progress**: Agents query Projects V2 for current status
- **Trigger Workflows**: Agents create pull requests and link them to issues
- **Monitor Health**: Agents track metrics (open issues, failing tests, deployment status)
- **Bidirectional Sync**: Changes in either system automatically propagate to the other

For detailed integration patterns, see [Implementation Guide → Agent Orchestrator Integration](references/implementation-guide.md#part-2-agent-orchestrator-integration).

## Advanced Topics (Future Reference)

For teams ready to go beyond basic implementation:

- **Multi-Repository Projects**: Managing issues across multiple repositories in a single project
- **Custom GitHub Actions**: Advanced automation with workflow files
- **GraphQL Queries**: Complex filtering and bulk operations
- **Webhook Configuration**: Real-time synchronization with webhook listeners
- **CI/CD Integration**: Linking deployments to issue tracking

These topics are covered in the [Implementation Guide → Advanced Implementation Topics](references/implementation-guide.md#part-3-advanced-implementation-topics).

## Resources

- [references/prerequisites-and-setup.md](references/prerequisites-and-setup.md) - GitHub CLI installation and authentication
- [references/multi-user-workflow.md](references/multi-user-workflow.md) - Managing multiple GitHub identities
- [references/core-concepts.md](references/core-concepts.md) - Projects V2 and 9-label system
- [references/issue-management.md](references/issue-management.md) - Creating and managing issues
- [references/pull-request-management.md](references/pull-request-management.md) - PR creation and merging
- [references/projects-v2-operations.md](references/projects-v2-operations.md) - Project board configuration
- [references/batch-operations.md](references/batch-operations.md) - Bulk operations and filtering
- [references/automation-scripts.md](references/automation-scripts.md) - Python automation scripts
- [references/script-multi-user-identity.md](references/script-multi-user-identity.md) - Multi-user identity script
- [references/troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
- [references/implementation-guide.md](references/implementation-guide.md) - Complete setup guide

---

**Skill Version:** 1.2.0
**Last Updated:** 2026-01-02
**Maintainer:** Skill Development Team
**Changelog:**
- 1.2.0: Added cross-platform `gh_multiuser.py` script with configuration-driven identity management
- 1.1.0: Added Multi-User Workflow reference for owner/developer identity separation
