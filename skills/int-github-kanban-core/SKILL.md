---
name: ao-github-kanban-core
description: "Positions GitHub Projects V2 Kanban as THE SINGLE SOURCE OF TRUTH for Atlas orchestration. Every module is an issue, every assignment is an assignee, every status is a column. The orchestrator NEVER tracks work outside the board."
license: Apache-2.0
compatibility: "Requires GitHub CLI authentication, GitHub Projects V2 enabled repository, GraphQL API access, Python 3.8+"
metadata:
  author: Anthropic
  version: 1.0.0
agent: api-coordinator
context: fork
---

# GitHub Kanban Core

## THE IRON RULE

**GitHub Projects Kanban IS the orchestration state. There is no other source of truth.**

- Every module = 1 GitHub Issue on the board
- Every agent assignment = 1 Issue assignee
- Every status change = 1 board column move
- The orchestrator NEVER tracks work in memory, files, or any other system

If it's not on the board, it doesn't exist. If the board says "In Progress", it IS in progress.

---

## Overview

This skill establishes GitHub Projects V2 as the absolute center of Atlas orchestration workflow. All planning, tracking, assignment, and completion verification flows through the Kanban board.

## When to Use This Skill

Read this skill when:
- Starting any orchestration session
- Planning new work (modules, features, tasks)
- Assigning work to agents or humans
- Checking work status or progress
- Verifying completion before exiting
- Handling blocked work items
- Integrating with stop hooks

---

## Quick Reference: Board Columns

| Column | Code | Meaning | Who Can Move Here |
|--------|------|---------|-------------------|
| **Backlog** | `backlog` | Not scheduled | Orchestrator only |
| **Todo** | `todo` | Ready to start | Orchestrator only |
| **In Progress** | `in_progress` | Active work | Assigned agent |
| **In Review** | `in_review` | PR awaiting review | Assigned agent |
| **Done** | `done` | Completed and merged | Auto (PR merge) |
| **Blocked** | `blocked` | Cannot proceed | Any (with reason) |

---

## Reference Documentation

All detailed operations are in reference files. Each section shows **WHEN to read** and the **full TOC**.

---

### Why Kanban Is the Single Source of Truth ([references/kanban-as-truth.md](references/kanban-as-truth.md))

Read this FIRST to understand the philosophical foundation.

**Contents:**
- 1.1 Why centralized truth matters for AI orchestration
- 1.2 The problems with distributed state tracking
- 1.3 Why GitHub Projects V2 is the ideal choice
- 1.4 The Iron Rules of Kanban-centric orchestration
- 1.5 What happens when you violate these rules
- 1.6 Comparison: Traditional vs Kanban-centric orchestration

---

### Board Column Semantics ([references/board-column-semantics.md](references/board-column-semantics.md))

Read this when you need to understand what each column means and its requirements.

**Contents:**
- 2.1 Overview of the 6-column workflow
- 2.2 Backlog column - items not yet scheduled
- 2.3 Todo column - ready for immediate work
- 2.4 In Progress column - active development
- 2.5 In Review column - PR created, awaiting review
- 2.6 Done column - completed and verified
- 2.7 Blocked column - cannot proceed
- 2.8 Column metadata and requirements table
- 2.9 Visual board layout example

---

### Issue-to-Module Mapping ([references/issue-to-module-mapping.md](references/issue-to-module-mapping.md))

Read this when creating issues for modules or understanding the 1:1 mapping.

**Contents:**
- 3.1 The 1:1 principle: every module is exactly one issue
- 3.2 Module issue template structure
- 3.3 Required fields for module issues
- 3.4 Naming conventions for module issues
- 3.5 Linking module issues to parent epics
- 3.6 Creating module issues from plan files
- 3.7 Bulk module issue creation workflow
- 3.8 Module issue lifecycle from creation to closure

---

### Agent Assignment via Board ([references/agent-assignment-via-board.md](references/agent-assignment-via-board.md))

Read this when assigning work to agents or checking assignments.

**Contents:**
- 4.1 Assignment principle: issue assignee = responsible agent
- 4.2 How to assign issues via CLI
- 4.3 How to assign issues via GraphQL
- 4.4 Agent naming conventions for GitHub
- 4.5 Verifying current assignments
- 4.6 Reassigning work between agents
- 4.7 Multi-agent collaboration on single issue
- 4.8 Assignment notifications via AI Maestro

---

### Status Transitions ([references/status-transitions.md](references/status-transitions.md))

Read this when moving cards between columns or validating transitions.

**Contents:**
- 5.1 Valid transition matrix (what moves are allowed)
- 5.2 Transition preconditions and postconditions
- 5.3 Who can move cards (orchestrator vs agent vs auto)
- 5.4 Backlog to Todo transition rules
- 5.5 Todo to In Progress transition rules
- 5.6 In Progress to In Review transition rules
- 5.7 In Review to Done transition rules
- 5.8 Any status to Blocked transition rules
- 5.9 Blocked to previous status transition rules
- 5.10 Invalid transitions and how to handle them

---

### Blocking Workflow ([references/blocking-workflow.md](references/blocking-workflow.md))

Read this when an item becomes blocked or when resolving blockers.

**Contents:**
- 6.1 What constitutes a blocker
- 6.2 How to mark an item as blocked
- 6.3 Required information when blocking
- 6.4 Blocker escalation timeline
- 6.5 Resolving blockers and resuming work
- 6.6 Cross-issue blocking dependencies
- 6.7 External blockers (outside GitHub)
- 6.8 Blocker status reporting

---

### Board Queries ([references/board-queries.md](references/board-queries.md))

Read this when you need GraphQL queries to inspect board state.

**Contents:**
- 7.1 Get full board state (all items, all columns)
- 7.2 Get items by status column
- 7.3 Get items assigned to specific agent
- 7.4 Get blocked items with blocker reasons
- 7.5 Get items in review awaiting merge
- 7.6 Count items per column (summary)
- 7.7 Get item history and transitions
- 7.8 Check if all items are Done

---

### Stop Hook Integration ([references/stop-hook-integration.md](references/stop-hook-integration.md))

Read this to understand how the stop hook uses board state for completion verification.

**Contents:**
- 8.1 The stop hook's role in orchestration
- 8.2 Board state queries performed by stop hook
- 8.3 Completion criteria: when can orchestrator exit
- 8.4 Handling incomplete work at exit time
- 8.5 Blocked items and exit policy
- 8.6 Stop hook configuration options
- 8.7 Manual override of stop hook
- 8.8 Stop hook error handling

---

### AI Agent vs Human Workflow ([references/ai-agent-vs-human-workflow.md](references/ai-agent-vs-human-workflow.md))

Read this when coordinating between AI agents and human developers.

**Contents:**
- 9.1 Key differences in AI vs human workflow
- 9.2 Assignment strategies for AI agents
- 9.3 Assignment strategies for human developers
- 9.4 Communication channels: AI Maestro vs GitHub comments
- 9.5 Review workflow differences
- 9.6 Handoff protocols between AI and human
- 9.7 Mixed team coordination patterns
- 9.8 Escalation paths for AI blockers

---

### Troubleshooting ([references/troubleshooting.md](references/troubleshooting.md))

Read this when encountering issues with board synchronization or operations.

**Contents:**
- 10.1 Issue not appearing on board after creation
- 10.2 Status change not reflecting on board
- 10.3 Assignment not showing correctly
- 10.4 GraphQL API errors and rate limiting
- 10.5 Permission denied errors
- 10.6 Board state out of sync with reality
- 10.7 Stop hook blocking exit incorrectly
- 10.8 Recovery procedures for corrupted state

---

## Command Integration: /create-issue-tasks

The `/create-issue-tasks` command creates Claude Tasks checklists for handling issues. See the full command documentation at:
`${CLAUDE_PLUGIN_ROOT}/commands/create-issue-tasks.md`

### Quick Usage

```
/create-issue-tasks <CATEGORY> <REPORTER> <MODULE> "<TITLE>" ["<DESCRIPTION>"]
```

**Categories:** BUG, BLOCKER, QUESTION, ENHANCEMENT, CONFIG, INVESTIGATION

**Example:**
```
/create-issue-tasks BUG implementer-1 auth-core "Login fails with OAuth" "401 error after token expiry"
```

---

## Python Scripts

### Get Board State ([scripts/kanban_get_board_state.py](scripts/kanban_get_board_state.py))

Get complete board state with all items grouped by column.

```bash
python3 scripts/kanban_get_board_state.py OWNER REPO PROJECT_NUMBER
```

**Output:** JSON with items grouped by status column.

---

### Move Card ([scripts/kanban_move_card.py](scripts/kanban_move_card.py))

Move a card to a different column with validation.

```bash
python3 scripts/kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]
```

**Validates:** Transition is allowed, preconditions met.

---

### Check Completion ([scripts/kanban_check_completion.py](scripts/kanban_check_completion.py))

Check if all board items are complete (for stop hook).

```bash
python3 scripts/kanban_check_completion.py OWNER REPO PROJECT_NUMBER
```

**Exit codes:**
- 0: All items Done
- 1: Items still in progress
- 2: Blocked items exist

---

## Integration Points

### Planning Phase

1. Orchestrator breaks work into modules
2. Each module becomes a GitHub Issue
3. Issues are added to project board in Backlog
4. Orchestrator moves ready issues to Todo
5. Board reflects complete work breakdown

### Orchestration Phase

1. Orchestrator assigns Todo issues to agents
2. Agent moves issue to In Progress when starting
3. Agent creates PR, moves to In Review
4. PR merge auto-moves to Done
5. Board reflects real-time progress

### Stop Hook Phase

1. Stop hook queries board state
2. Checks: all assigned items Done or explicitly deferred
3. If incomplete items exist, prevents exit
4. Orchestrator must resolve or defer before exit

### Assignment Flow

1. Orchestrator identifies next Todo item
2. Orchestrator assigns to available agent
3. Assignment appears as GitHub issue assignee
4. Agent receives notification via AI Maestro
5. Assignment visible on board

### PR Completion Flow

1. Agent creates PR linked to issue (Closes #N)
2. Agent moves issue to In Review
3. Review happens (AI or human)
4. PR merged triggers auto-move to Done
5. Issue closes automatically

---

## Skill Files

```
github-kanban-core/
├── SKILL.md                              # This file (map/TOC)
├── README.md                             # Skill overview
├── scripts/
│   ├── kanban_get_board_state.py         # Get full board state
│   ├── kanban_move_card.py               # Move card between columns
│   └── kanban_check_completion.py        # Check completion for stop hook
└── references/
    ├── kanban-as-truth.md                # Why Kanban is single source of truth
    ├── board-column-semantics.md         # Column meanings and requirements
    ├── issue-to-module-mapping.md        # Module-to-issue 1:1 mapping
    ├── agent-assignment-via-board.md     # Assignment via issue assignees
    ├── status-transitions.md             # Valid state transitions
    ├── blocking-workflow.md              # Handling blocked items
    ├── board-queries.md                  # GraphQL queries for board state
    ├── stop-hook-integration.md          # Stop hook completion checks
    ├── ai-agent-vs-human-workflow.md     # Different workflows for AI vs humans
    └── troubleshooting.md                # Common issues and solutions
```

---

## Related Skills

- **github-projects-sync** - Detailed GitHub Projects V2 operations and templates
- **remote-agent-coordinator** - Agent communication and task routing
- **orchestrator-stop-hook** - Stop hook behavior and configuration
