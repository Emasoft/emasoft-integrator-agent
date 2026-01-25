# Integrator Agent (int-)

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
| `int-main.md` | Main integrator agent |
| `int-code-reviewer.md` | Reviews code for quality |
| `int-pr-evaluator.md` | Evaluates PR readiness |
| `int-integration-verifier.md` | Verifies integration success |
| `int-bug-investigator.md` | Investigates reported bugs |
| `int-github-sync.md` | Syncs GitHub state |

### Skills

| Skill | Description |
|-------|-------------|
| `int-github-integration` | GitHub API integration |
| `int-github-pr-workflow` | PR workflow patterns |
| `int-github-pr-checks` | PR check patterns |
| `int-github-pr-merge` | PR merge strategies |
| `int-github-pr-context` | PR context management |
| `int-github-issue-operations` | Issue CRUD operations |
| `int-github-kanban-core` | Kanban board patterns |
| `int-github-projects-sync` | Projects sync |
| `int-github-project-workflow` | Project workflow |
| `int-github-thread-management` | Thread management |
| `int-code-review-patterns` | Code review patterns |
| `int-multilanguage-pr-review` | Multi-language reviews |
| `int-tdd-enforcement` | TDD enforcement |
| `int-ci-failure-patterns` | CI failure patterns |
| `int-worktree-management` | Git worktree management |
| `int-git-worktree-operations` | Worktree operations |
| `int-shared` | Shared utilities |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `int-branch-protection` | PreToolUse | Block pushes to main/master |
| `int-issue-closure-gate` | PreToolUse | Verify before issue closure |

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
uv run python scripts/int_validate_plugin.py --verbose
```
