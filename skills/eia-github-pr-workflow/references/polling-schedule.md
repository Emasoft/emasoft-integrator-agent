# Polling Schedule

## Table of Contents

- 7.1 Base polling frequency
- 7.2 What to check on each poll
- 7.3 Adaptive polling rules
- 7.4 Notification triggers

---

## 7.1 Base polling frequency

**Default interval**: Poll every 10-15 minutes during active work periods.

### Recommended intervals by context

| Context | Interval | Rationale |
|---------|----------|-----------|
| Normal operations | 10-15 minutes | Balance between responsiveness and overhead |
| Active PR work | 5 minutes | Faster feedback during implementation |
| Waiting for CI | 2-5 minutes | CI completion can unblock work |
| After hours | 30-60 minutes | Reduced activity expected |
| Urgent PR | 2-3 minutes | Time-sensitive work |

### Polling implementation

**Option 1: Manual polling**
The orchestrator explicitly runs the poll script:
```bash
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo
```

**Option 2: Background task**
Delegate polling to a monitoring subagent:
```
You are a PR monitoring subagent. Your task is:
Poll PR status every 10 minutes and report significant changes.

Actions:
1. Run poll script every 10 minutes
2. Compare results to previous poll
3. Report via AI Maestro message if significant change detected
```

**Option 3: Event-driven (preferred)**
Use GitHub webhooks or CLI notifications when available.

### Polling budget

**Maximum polls per hour**: 12 (every 5 minutes)
**Maximum polls per day**: 144 (12 per hour * 12 active hours)

**Why budget matters**:
- API rate limits
- Context consumption
- Orchestrator availability for other tasks

---

## 7.2 What to check on each poll

### Mandatory checks (every poll)

| Check | Command | Purpose |
|-------|---------|---------|
| PR state | `gh pr view --json state` | Detect close/merge |
| CI status | `gh pr checks` | Detect pass/fail |
| New comments | `gh api` comments endpoint | Detect activity |
| Merge eligibility | `gh pr view --json mergeable` | Detect blockers |

### Periodic checks (every 3rd poll)

| Check | Command | Purpose |
|-------|---------|---------|
| Full verification | `eia_verify_pr_completion.py` | Comprehensive status |
| Unresolved threads | GraphQL query | Detect missed items |
| Unpushed commits | `git log origin..HEAD` | Detect local work |

### On-demand checks (triggered by condition)

| Trigger | Check | Purpose |
|---------|-------|---------|
| CI was pending | CI status | Confirm completion |
| Commits were pushed | CI status | Verify new run |
| Review requested | Review status | Detect response |
| Conflict detected | Merge status | Confirm resolution |

### Poll result data structure

```json
{
  "poll_time": "2024-01-15T10:30:00Z",
  "prs_checked": 3,
  "results": [
    {
      "pr_number": 123,
      "state": "open",
      "mergeable": true,
      "ci_status": "passing",
      "new_comments": 0,
      "unresolved_threads": 0,
      "action_needed": "none",
      "changed_since_last_poll": false
    },
    {
      "pr_number": 456,
      "state": "open",
      "mergeable": false,
      "ci_status": "failing",
      "new_comments": 2,
      "unresolved_threads": 1,
      "action_needed": "fix_ci",
      "changed_since_last_poll": true
    }
  ]
}
```

---

## 7.3 Adaptive polling rules

Polling frequency should adapt based on PR state and recent activity.

### Frequency increase triggers

| Condition | Adjust To | Rationale |
|-----------|-----------|-----------|
| CI just started | 2 min | Know completion ASAP |
| Commits just pushed | 3 min | Await CI start |
| Active conversation | 5 min | Respond quickly |
| User is online | 5 min | More responsive |
| Approaching deadline | 3 min | Time-sensitive |

### Frequency decrease triggers

| Condition | Adjust To | Rationale |
|-----------|-----------|-----------|
| CI pending > 10 min | 5 min | Long-running, don't spam |
| No activity > 30 min | 15 min | Likely stalled |
| Outside work hours | 30 min | Low activity expected |
| Waiting for human | 15 min | Can't control timing |
| All PRs stable | 15 min | Nothing to action |

### State-based polling schedule

```
PR State Machine:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  DRAFT → READY_FOR_REVIEW → IN_REVIEW → CHANGES_REQUESTED   │
│    │           │                │              │             │
│  30min       10min            5min           5min            │
│                                │                             │
│                          APPROVED → CI_PENDING → READY       │
│                             │          │           │         │
│                           10min      2min        5min        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Adaptive algorithm pseudocode

```python
def get_poll_interval(pr_status, last_activity_time, current_time):
    """Determine next poll interval based on PR state."""

    minutes_since_activity = (current_time - last_activity_time).minutes

    # High frequency cases
    if pr_status.ci_status == "pending" and pr_status.ci_started_within(10):
        return 2  # minutes
    if pr_status.commits_pushed_within(5):
        return 3
    if pr_status.has_new_comments_within(10):
        return 5

    # Low frequency cases
    if minutes_since_activity > 60:
        return 15
    if pr_status.state == "draft":
        return 30
    if pr_status.waiting_for_human:
        return 15

    # Default
    return 10
```

---

## 7.4 Notification triggers

The orchestrator should notify the user when significant events occur.

### Immediate notification triggers

| Event | Notification | Priority |
|-------|--------------|----------|
| CI failed | "CI failed on PR #X: [reason]" | High |
| PR merged externally | "PR #X was merged" | Medium |
| PR closed externally | "PR #X was closed without merge" | Medium |
| Merge conflict detected | "PR #X has merge conflicts" | High |
| Human commented | "Human @Y commented on PR #X" | High |
| All criteria pass | "PR #X ready for merge" | Medium |

### Periodic summary triggers

| Condition | Summary | Frequency |
|-----------|---------|-----------|
| Start of work day | "PR status summary: [count] open, [count] need action" | Daily |
| Multiple PRs ready | "Batch: [count] PRs ready for merge" | As occurs |
| Stalled PRs | "[count] PRs have no activity for 24h" | Daily |

### Escalation triggers

| Condition | Escalation | Timing |
|-----------|------------|--------|
| CI pending > 30 min | "CI for PR #X stuck. Check status." | After 30 min |
| Same failure 3 times | "Repeated failure on PR #X: [criterion]" | After 3 attempts |
| Human waiting > 4 hours | "Human awaiting response on PR #X" | After 4 hours |
| Conflict unresolved > 1 hour | "Merge conflict on PR #X needs attention" | After 1 hour |

### Notification suppression

**Do not notify for**:
- Routine polling with no changes
- Expected CI runs
- Automated bot updates (unless failure)
- Intermediate states during active work

### Notification format

```
## [Priority] PR #[number] Notification

**Event**: [description]
**Time**: [timestamp]
**Action needed**: [what user should do]
**Details**: [link to PR or status file]
```

---

## Polling Script Usage

### Full poll

```bash
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo
```

### Filtered poll

```bash
# Only PRs needing action
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo --filter needs_action

# Only specific PR
python scripts/eia_orchestrator_pr_poll.py --repo owner/repo --pr 123
```

### Output example

```json
{
  "poll_time": "2024-01-15T10:30:00Z",
  "repo": "owner/repo",
  "prs": [
    {
      "number": 123,
      "title": "Add new feature",
      "state": "open",
      "author": "johndoe",
      "author_type": "human",
      "created_at": "2024-01-14T09:00:00Z",
      "updated_at": "2024-01-15T10:25:00Z",
      "status": "needs_review",
      "ci_status": "passing",
      "mergeable": true,
      "priority": 1,
      "action_needed": "delegate_review",
      "next_poll_interval": 10
    }
  ],
  "summary": {
    "total_open": 3,
    "needs_action": 1,
    "blocked": 0,
    "ready_to_merge": 2
  }
}
```

---

## Polling Best Practices

1. **Always check CI first**: CI status often determines next steps
2. **Compare to previous poll**: Only act on changes
3. **Respect rate limits**: Don't poll more than necessary
4. **Use adaptive intervals**: Adjust based on state
5. **Batch notifications**: Don't spam user with minor updates
6. **Log poll results**: Keep history for debugging
7. **Handle API failures gracefully**: Retry with backoff
