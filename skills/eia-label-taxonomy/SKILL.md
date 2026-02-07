---
name: eia-label-taxonomy
description: GitHub label taxonomy reference for the Integrator Agent. Use when managing PR reviews, updating PR status, or applying review labels. Trigger with review label requests.
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: eia-main
context: fork
workflow-instruction: "support"
procedure: "support-skill"
---

# EIA Label Taxonomy

## Overview

This skill provides the label taxonomy relevant to the Integrator Agent (EIA) role. Each role plugin has its own label-taxonomy skill covering the labels that role manages.

---

## Prerequisites

1. GitHub CLI (`gh`) installed and authenticated
2. Active PR or issue number to label
3. Understanding of EIA role responsibilities (see **AGENT_OPERATIONS.md**)
4. Knowledge of current PR review state

---

## Instructions

1. Identify current PR state (needs-review, in-progress, changes-requested, approved)
2. Check for priority labels to determine review urgency
3. Review type labels to adjust review depth
4. Update review labels using appropriate `gh pr edit` commands
5. After merge, update issue status labels
6. Remove assignment labels after completion

### Workflow Checklist

Copy this checklist and track your progress:

- [ ] Identify current PR state and existing labels
- [ ] Check priority labels (critical/high/normal/low)
- [ ] Check type labels to determine review depth
- [ ] Update review label to "review:in-progress" when starting
- [ ] Perform review according to type requirements
- [ ] Update review label to "review:approved" or "review:changes-requested"
- [ ] After merge: update issue status to "status:done"
- [ ] After merge: remove assignment labels
- [ ] Verify all label changes in GitHub PR timeline

---

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Label update confirmation | CLI stdout | `✓ Labels updated for #123` |
| Current labels | JSON | `gh pr view $PR --json labels` |
| Label history | GitHub timeline | View in PR web interface |

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `label not found` | Label doesn't exist in repo | Create label first via `gh label create` |
| `permission denied` | No write access to PR | Verify GitHub token scopes |
| `PR not found` | Invalid PR number | Verify PR number with `gh pr list` |
| `conflict` | Multiple agents editing labels | Retry after short delay |

---

## Labels EIA Manages

### Review Labels (`review:*`)

**EIA is the PRIMARY manager of review labels on PRs.**

| Label | Description | When EIA Sets It |
|-------|-------------|------------------|
| `review:needed` | PR needs review | Assigned by EOA or PR creator |
| `review:in-progress` | EIA reviewing | When starting review |
| `review:changes-requested` | Issues found | After review with issues |
| `review:approved` | Review passed | After successful review |
| `review:blocked` | Cannot review | When conflicts or missing info |

**EIA Review Workflow:**
```
PR created → review:needed → review:in-progress → review:approved OR review:changes-requested
                                                           ↓
                                              changes made → review:in-progress (repeat)
```

### Status Labels EIA Updates

| Label | When EIA Sets It |
|-------|------------------|
| `status:needs-review` | When PR is ready for review |
| `status:blocked` | When PR has conflicts or CI failures |
| `status:done` | After PR merged and verified |

---

## Labels EIA Reads (Set by Others)

### Assignment Labels (`assign:*`)

EIA checks assignment to know who created the PR:
- `assign:implementer-1`, `assign:implementer-2` - Implementation agents
- `assign:orchestrator` - EOA-created PRs

### Priority Labels (`priority:*`)

EIA uses priority to order review queue:
- `priority:critical` - Review immediately
- `priority:high` - Review soon
- `priority:normal` - Standard queue
- `priority:low` - Review when available

### Type Labels (`type:*`)

EIA adjusts review depth based on type:
- `type:security` - Deep security review
- `type:refactor` - Focus on behavior preservation
- `type:docs` - Light review
- `type:feature` - Full functionality review

---

## EIA Label Commands

### When Starting Review

```bash
# Mark review in progress
gh pr edit $PR_NUMBER --remove-label "review:needed" --add-label "review:in-progress"
```

### When Review Complete (Approved)

```bash
# Mark approved
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:approved"
```

### When Changes Requested

```bash
# Mark changes needed
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:changes-requested"
```

### When PR Merged

```bash
# Update issue status to done
gh issue edit $ISSUE_NUMBER --remove-label "status:needs-review" --add-label "status:done"
# Remove assignment
gh issue edit $ISSUE_NUMBER --remove-label "assign:$AGENT_NAME"
```

---

## Examples

### Example 1: Starting a PR Review

```bash
# Scenario: PR #45 is labeled review:needed, priority:high
# Action: Begin review
gh pr edit 45 --remove-label "review:needed" --add-label "review:in-progress"
# Result: PR now shows review is actively being conducted
```

### Example 2: Requesting Changes

```bash
# Scenario: Review found issues in PR #45
# Action: Request changes and leave review comment
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:changes-requested"
gh pr review 45 --request-changes --body "Please address the following issues: ..."
# Result: PR blocked from merge, developer notified
```

### Example 3: Approving and Merging

```bash
# Scenario: PR #45 passes all checks
# Action: Approve PR
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:approved"
gh pr review 45 --approve
# After merge: Update parent issue
gh issue edit 78 --remove-label "status:needs-review" --add-label "status:done"
```

### Example 4: Blocked PR

```bash
# Scenario: PR #45 has merge conflicts
# Action: Mark as blocked
gh pr edit 45 --add-label "review:blocked"
gh pr comment 45 --body "Cannot review: merge conflicts detected. Please resolve conflicts."
```

---

## Quick Reference

### EIA Label Responsibilities

| Action | Labels Involved |
|--------|-----------------|
| Start review | Remove `review:needed`, add `review:in-progress` |
| Approve PR | Remove `review:in-progress`, add `review:approved` |
| Request changes | Remove `review:in-progress`, add `review:changes-requested` |
| After merge | Issue: remove `status:*`, add `status:done` |
| Mark blocked | Add `status:blocked` or `review:blocked` |

### Labels EIA Never Sets

- `assign:*` - Set by EOA only
- `type:*` - Set at issue creation
- `effort:*` - Set during triage
- `component:*` - Set at issue creation

---

## Resources

- **AGENT_OPERATIONS.md** - EIA role definition and responsibilities
- **eia-github-pr-workflow** - Full PR workflow procedures
