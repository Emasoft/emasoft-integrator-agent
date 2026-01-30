---
name: eia-github-pr-workflow
description: >
  Use when coordinating PR review work as an orchestrator. Defines when and how
  the orchestrator coordinates PR review work, including delegation rules,
  verification workflows, and completion criteria.
license: Apache-2.0
metadata:
  version: 1.0.0
  author: Integrator Agent Team
  category: workflow
  tags:
    - pr-review
    - orchestration
    - delegation
    - verification
    - github
agent: api-coordinator
context: fork
---

# Orchestrator PR Workflow Skill

## Overview

This skill defines the orchestrator's role in coordinating Pull Request review work. The orchestrator is a **coordinator**, not a worker. It monitors PR status, delegates review tasks to specialized subagents, tracks completion, and reports to the user.

**Core Principle**: The orchestrator NEVER does direct work on PRs. It orchestrates, delegates, monitors, and reports.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for running automation scripts
- AI Maestro configured for inter-agent communication
- Access to spawn subagents for delegation

## Instructions

Follow the decision tree below to determine the appropriate action for any PR review request.

---

## Quick Reference: Decision Tree

```
PR Review Request Received
│
├─► Is PR from human or AI agent?
│   ├─► Human PR → Escalate to user for guidance
│   └─► AI/Bot PR → Direct delegation allowed
│
├─► What type of work is needed?
│   ├─► Code review → Delegate to review subagent
│   ├─► Code changes → Delegate to implementation subagent
│   ├─► CI verification → Delegate to CI monitor subagent
│   └─► Status check → Use polling script directly
│
├─► Should I block waiting?
│   └─► NEVER block. Always use background tasks or polling.
│
└─► Is PR ready to merge?
    ├─► Run completion verification script
    ├─► All criteria pass → Report to user, await merge decision
    └─► Criteria fail → Identify gaps, delegate fixes
```

---

## Table of Contents with Reference Maps

### 1. Orchestrator Responsibilities
**Reference**: [orchestrator-responsibilities.md](references/orchestrator-responsibilities.md)
- 1.1 What the orchestrator MUST do
  - 1.1.1 Monitor PR status periodically
  - 1.1.2 Delegate review work to subagents
  - 1.1.3 Track completion status
  - 1.1.4 Report to user
- 1.2 What the orchestrator MUST NOT do
  - 1.2.1 Write code directly
  - 1.2.2 Block on long operations
  - 1.2.3 Make unilateral merge decisions

### 2. Delegation Rules
**Reference**: [delegation-rules.md](references/delegation-rules.md)
- 2.1 When to spawn subagents
  - 2.1.1 Task complexity thresholds
  - 2.1.2 Time-based triggers
  - 2.1.3 Resource availability checks
- 2.2 How to structure subagent prompts
  - 2.2.1 Required prompt elements
  - 2.2.2 Context passing rules
  - 2.2.3 Output format requirements
- 2.3 Maximum concurrent agents
- 2.4 Task isolation requirements
- 2.5 Result aggregation patterns

### 3. Verification Workflow
**Reference**: [verification-workflow.md](references/verification-workflow.md)
- 3.1 Pre-review verification checklist
- 3.2 Post-review verification checklist
- 3.3 CI check verification
- 3.4 Thread resolution verification
- 3.5 Merge readiness verification
- 3.6 The 4-verification-loop protocol
  - 3.6.1 Loop structure and timing
  - 3.6.2 Exit conditions
  - 3.6.3 Escalation triggers

### 4. Worktree Coordination
**Reference**: [worktree-coordination.md](references/worktree-coordination.md)
- 4.1 When to use worktrees
- 4.2 Worktree assignment to subagents
- 4.3 Isolation enforcement rules
- 4.4 Cleanup coordination
- 4.5 Conflict handling procedures

### 5. Human vs AI PR Assignment
**Reference**: [human-vs-ai-assignment.md](references/human-vs-ai-assignment.md)
- 5.1 Identifying PR author type
  - 5.1.1 Human contributors
  - 5.1.2 AI agent PRs
  - 5.1.3 Bot categories
- 5.2 Communication style differences
- 5.3 Escalation rules for human PRs
- 5.4 Direct action rules for AI PRs

### 6. Completion Criteria
**Reference**: [completion-criteria.md](references/completion-criteria.md)
- 6.1 ALL criteria that must be true
  - 6.1.1 Review comments addressed
  - 6.1.2 PR comments acknowledged
  - 6.1.3 No new comments (45s wait)
  - 6.1.4 CI checks pass
  - 6.1.5 No unresolved threads
  - 6.1.6 Merge eligible
  - 6.1.7 PR not already merged
  - 6.1.8 Commits pushed
- 6.2 Failure handling by type

### 7. Polling Schedule
**Reference**: [polling-schedule.md](references/polling-schedule.md)
- 7.1 Base polling frequency
- 7.2 What to check on each poll
- 7.3 Adaptive polling rules
- 7.4 Notification triggers

---

## Scripts Reference

### eia_orchestrator_pr_poll.py
**Location**: `scripts/eia_orchestrator_pr_poll.py`
**Purpose**: Get all open PRs, check status, identify actions needed
**When to use**: On each polling interval to survey PR landscape
**Output**: JSON with prioritized action list

```bash
# Usage
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo

# Output format
{
  "prs": [
    {
      "number": 123,
      "title": "PR Title",
      "status": "needs_review|needs_changes|ready|blocked",
      "priority": 1,
      "action_needed": "delegate_review|delegate_fix|verify_completion|wait"
    }
  ]
}
```

### eia_verify_pr_completion.py
**Location**: `scripts/eia_verify_pr_completion.py`
**Purpose**: Verify all completion criteria for a specific PR
**When to use**: Before reporting PR ready, before merge
**Output**: JSON pass/fail with detailed reasons

```bash
# Usage
python scripts/eia_verify_pr_completion.py --repo owner/repo --pr 123

# Output format
{
  "pr_number": 123,
  "complete": true|false,
  "criteria": {
    "reviews_addressed": true,
    "comments_acknowledged": true,
    "no_new_comments": true,
    "ci_passing": true,
    "no_unresolved_threads": true,
    "merge_eligible": true,
    "not_merged": true,
    "commits_pushed": true
  },
  "failing_criteria": [],
  "recommendation": "ready_to_merge|needs_work|blocked"
}
```

---

## Critical Rules Summary

### Rule 1: Never Block
The orchestrator must NEVER execute blocking operations. All long-running tasks must be:
- Delegated to subagents
- Run as background tasks
- Monitored via polling

### Rule 2: Never Write Code
The orchestrator coordinates, it does not implement. Code writing is ALWAYS delegated to implementation subagents.

### Rule 3: Never Merge Without User
The orchestrator may verify merge readiness but NEVER executes merge without explicit user approval.

### Rule 4: Always Verify Before Reporting
Before reporting any status (ready, complete, blocked), always run the verification script to confirm.

### Rule 5: Human PRs Require Escalation
PRs from human contributors require different handling. Always escalate to user for guidance on communication and decisions.

---

## Examples

### Example 1: Standard PR Review Coordination

```bash
# Poll for open PRs requiring action
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo

# For each PR needing review, delegate to review subagent
# (orchestrator spawns subagent with appropriate prompt)

# Verify completion before reporting
python scripts/eia_verify_pr_completion.py --repo owner/repo --pr 123
```

### Example 2: Verify PR is Ready to Merge

```bash
python scripts/eia_verify_pr_completion.py --repo owner/repo --pr 123
# If complete: true, report to user for merge decision
# If complete: false, identify failing_criteria and delegate fixes
```

## Error Handling

### Issue: Subagent not returning results
**Cause**: Subagent may have crashed or timed out
**Solution**: Check subagent logs, re-delegate with increased timeout or simpler scope

### Issue: PR status appears stale
**Cause**: GitHub API rate limiting or cache
**Solution**: Wait 60 seconds, then re-poll. If persistent, check API rate limits.

### Issue: Completion verification fails intermittently
**Cause**: Race condition with GitHub webhook processing
**Solution**: Implement 45-second quiet period check before final verification

### Issue: Multiple subagents conflicting
**Cause**: Insufficient task isolation
**Solution**: Use worktrees for parallel work, enforce file-level isolation

### Issue: User not receiving status updates
**Cause**: Notification not triggered
**Solution**: Check notification triggers in polling schedule, ensure report step executes

## Resources

- [references/orchestrator-responsibilities.md](references/orchestrator-responsibilities.md) - Orchestrator role definition
- [references/delegation-rules.md](references/delegation-rules.md) - Subagent delegation patterns
- [references/verification-workflow.md](references/verification-workflow.md) - Verification procedures
- [references/completion-criteria.md](references/completion-criteria.md) - PR completion requirements
- [references/polling-schedule.md](references/polling-schedule.md) - Polling frequency configuration
