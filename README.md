# Integrator Agent (eia-)

**Version**: 1.0.0

## Overview

The Integrator Agent handles **quality gates, testing, merging, and release candidates**. It ensures code quality before integration into the main branch.

## Core Responsibilities

1. **Code Review**: Review PRs for quality and correctness
2. **Quality Gates**: Enforce TDD, tests, and standards
3. **Branch Protection**: Prevent direct pushes to protected branches
4. **Issue Closure Gates**: Verify requirements before closing issues
5. **GitHub Integration**: Manage PRs, issues, and projects

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `eia-main.md` | Main integrator agent |
| `eia-code-reviewer.md` | Reviews code for quality |
| `eia-pr-evaluator.md` | Evaluates PR readiness |
| `eia-integration-verifier.md` | Verifies integration success |
| `eia-bug-investigator.md` | Investigates reported bugs |
| `eia-github-sync.md` | Syncs GitHub state |

### Skills

| Skill | Description |
|-------|-------------|
| `eia-github-integration` | GitHub API integration |
| `eia-github-pr-workflow` | PR workflow patterns |
| `eia-github-pr-checks` | PR check patterns |
| `eia-github-pr-merge` | PR merge strategies |
| `eia-github-pr-context` | PR context management |
| `eia-github-issue-operations` | Issue CRUD operations |
| `eia-github-kanban-core` | Kanban board patterns |
| `eia-github-projects-sync` | Projects sync |
| `eia-github-project-workflow` | Project workflow |
| `eia-github-thread-management` | Thread management |
| `eia-code-review-patterns` | Code review patterns |
| `eia-multilanguage-pr-review` | Multi-language reviews |
| `eia-tdd-enforcement` | TDD enforcement |
| `eia-ci-failure-patterns` | CI failure patterns |
| `eia-worktree-management` | Git worktree management |
| `eia-git-worktree-operations` | Worktree operations |
| `eia-shared` | Shared utilities |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `eia-branch-protection` | PreToolUse | Block pushes to main/master |
| `eia-issue-closure-gate` | PreToolUse | Verify before issue closure |

## Quality Gates

1. **Branch Protection**: No direct pushes to main/master
2. **Issue Closure Gate**: Requires:
   - Merged PR linked to issue
   - All checkboxes checked
   - Evidence of testing
   - TDD compliance

## Workflow

1. Receives completion signal from Orchestrator
2. Reviews code changes
3. Runs quality gates
4. Verifies tests pass
5. Creates/reviews PR
6. Merges when approved
7. Reports to Assistant Manager

## Installation

```bash
claude --plugin-dir ./OUTPUT_SKILLS/integrator-agent
```

## Validation

```bash
cd OUTPUT_SKILLS/integrator-agent
uv run python scripts/eia_validate_plugin.py --verbose
```
