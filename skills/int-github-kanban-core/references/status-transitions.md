# Status Transitions

## Table of Contents

- 5.1 [Valid transition matrix](#51-transition-matrix)
- 5.2 [Transition preconditions and postconditions](#52-preconditions-and-postconditions)
- 5.3 [Who can move cards](#53-who-can-move)
- 5.4 [Backlog to Todo transition rules](#54-backlog-to-todo)
- 5.5 [Todo to In Progress transition rules](#55-todo-to-in-progress)
- 5.6 [In Progress to In Review transition rules](#56-in-progress-to-in-review)
- 5.7 [In Review to Done transition rules](#57-in-review-to-done)
- 5.8 [Any status to Blocked transition rules](#58-any-to-blocked)
- 5.9 [Blocked to previous status transition rules](#59-blocked-to-previous)
- 5.10 [Invalid transitions and handling](#510-invalid-transitions)

---

## 5.1 Transition Matrix

```
FROM ↓ / TO →    │ Backlog │ Todo │ In Progress │ In Review │ Done │ Blocked │
─────────────────┼─────────┼──────┼─────────────┼───────────┼──────┼─────────┤
Backlog          │    -    │  ✓   │      ✗      │     ✗     │  ✗   │    ✗    │
Todo             │    ✓    │  -   │      ✓      │     ✗     │  ✗   │    ✓    │
In Progress      │    ✗    │  ✓   │      -      │     ✓     │  ✗   │    ✓    │
In Review        │    ✗    │  ✗   │      ✓      │     -     │  ✓   │    ✓    │
Done             │    ✗    │  ✗   │      ✗      │     ✗     │  -   │    ✗    │
Blocked          │    ✗    │  ✓   │      ✓      │     ✗     │  ✗   │    -    │
```

**Legend:**
- ✓ = Valid transition
- ✗ = Invalid transition
- `-` = Same status (no transition)

---

## 5.2 Preconditions and Postconditions

### Preconditions

Conditions that MUST be true BEFORE a transition can occur:

| Transition | Preconditions |
|------------|---------------|
| Backlog → Todo | Acceptance criteria defined, dependencies identified |
| Todo → In Progress | Assignee set, no blocking dependencies |
| In Progress → In Review | PR created, tests passing, PR linked to issue |
| In Review → Done | PR merged, CI passed |
| Any → Blocked | Blocker documented with reason |
| Blocked → Previous | Blocker resolved, documented in comment |

### Postconditions

Actions that MUST happen AFTER a transition:

| Transition | Postconditions |
|------------|----------------|
| Backlog → Todo | Notify assignee if set |
| Todo → In Progress | Feature branch created, start time recorded |
| In Progress → In Review | Reviewers notified |
| In Review → Done | Issue closed, parent progress updated |
| Any → Blocked | Escalation timer started |
| Blocked → Previous | Blocker resolution documented |

---

## 5.3 Who Can Move

### Permission Matrix

| Transition | Orchestrator | Assigned Agent | Any Agent | Automatic |
|------------|--------------|----------------|-----------|-----------|
| Backlog → Todo | ✓ | ✗ | ✗ | ✗ |
| Todo → Backlog | ✓ | ✗ | ✗ | ✗ |
| Todo → In Progress | ✓ | ✓ | ✗ | ✗ |
| In Progress → Todo | ✓ | ✓ | ✗ | ✗ |
| In Progress → In Review | ✓ | ✓ | ✗ | ✗ |
| In Review → In Progress | ✓ | ✓ | ✗ | ✗ |
| In Review → Done | ✗ | ✗ | ✗ | ✓ (PR merge) |
| Any → Blocked | ✓ | ✓ | ✓ | ✗ |
| Blocked → Previous | ✓ | ✓ | ✗ | ✗ |

### Key Rules

1. **Only orchestrator moves from Backlog** - Prioritization control
2. **Only orchestrator or assigned agent moves mid-workflow** - Ownership
3. **Anyone can block** - Safety first
4. **Done is automatic** - PR merge triggers

---

## 5.4 Backlog to Todo

### When to Transition

Move from Backlog to Todo when:
- Item is prioritized for current or next sprint
- All prerequisites are satisfied
- Capacity exists to work on it

### Preconditions Checklist

- [ ] Clear title and description
- [ ] Acceptance criteria defined
- [ ] Dependencies identified (and not blocking)
- [ ] Effort estimated (recommended)
- [ ] Assignee identified (recommended)

### CLI Command

```bash
# Get project and field IDs first, then:
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$STATUS_FIELD_ID" -f optionId="$TODO_OPTION_ID"
```

### Comment Template

```markdown
Moved to **Todo** for Sprint 3.
Priority: High
Assigned to: @agent-1
```

---

## 5.5 Todo to In Progress

### When to Transition

Move from Todo to In Progress when:
- Agent starts working on the issue
- Feature branch is created (or about to be)

### Preconditions Checklist

- [ ] Assignee is set
- [ ] Agent is ready to start
- [ ] No blocking dependencies
- [ ] Sprint/iteration allows starting

### Postconditions

After moving to In Progress:
1. Create feature branch: `git checkout -b feature/issue-42-auth-core`
2. Record start timestamp in comment
3. Notify orchestrator (optional)

### Comment Template

```markdown
Started work.
Branch: `feature/issue-42-auth-core`
Started: 2024-01-15 14:30 UTC
```

---

## 5.6 In Progress to In Review

### When to Transition

Move from In Progress to In Review when:
- Implementation is complete (from author's perspective)
- PR is created and linked to issue
- All local tests pass

### Preconditions Checklist

- [ ] Code complete for acceptance criteria
- [ ] PR created with "Closes #N" in body
- [ ] Tests written and passing locally
- [ ] PR description explains changes
- [ ] No obvious issues remaining

### PR Body Template

```markdown
## Summary

[Brief description of changes]

Closes #42

## Changes

- [Change 1]
- [Change 2]

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Checklist

- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
```

### Comment on Issue

```markdown
Ready for review.
PR: #123
All tests passing locally.
```

---

## 5.7 In Review to Done

### When to Transition

Move from In Review to Done when:
- PR is merged (not just approved)
- This transition should be AUTOMATIC via GitHub

### Automatic Trigger

When PR body contains "Closes #N" and PR is merged:
1. GitHub closes issue #N automatically
2. Board should reflect Done status

### Manual Transition (Exceptional)

If automatic transition fails:

```bash
# Check PR is actually merged
gh pr view 123 --json merged

# If merged but issue not closed, close manually
gh issue close 42

# Update board status
# [GraphQL mutation to set status to Done]
```

### Verification

Before marking Done, verify:
- [ ] PR is actually merged (not just closed)
- [ ] CI checks passed
- [ ] No follow-up issues created

---

## 5.8 Any to Blocked

### When to Transition

Move to Blocked when:
- External dependency is preventing progress
- Agent cannot proceed without intervention
- Resource or access is unavailable

### What Constitutes a Blocker

| Blocker Type | Example |
|--------------|---------|
| Technical | Dependency not available |
| Access | Missing permissions |
| Clarification | Requirements unclear |
| External | Third-party API down |
| Resource | Server not provisioned |

### Required Information

When moving to Blocked, MUST provide:

```markdown
## Blocked

**Blocker:** [description]
**Type:** Technical / Access / Clarification / External / Resource
**Blocking Issue:** #XX (if applicable)
**What's Needed:** [specific action to unblock]
**Impact:** [what can't proceed]
**Discovered:** YYYY-MM-DD HH:MM UTC
```

### CLI Commands

```bash
# Update status to Blocked
# [GraphQL mutation]

# Add blocked label
gh issue edit 42 --add-label "blocked"

# Comment with blocker details
gh issue comment 42 --body "## Blocked
**Blocker:** Missing database credentials
**Type:** Access
**What's Needed:** DBA to provide staging DB credentials
**Discovered:** 2024-01-15 15:00 UTC"
```

---

## 5.9 Blocked to Previous

### When to Transition

Move from Blocked back to previous status when:
- Blocker is resolved
- Agent can continue work
- Resolution is verified

### Determining Previous Status

Track the status before blocking in the blocker comment:

```markdown
## Blocked

**Previous Status:** In Progress
[... blocker details ...]
```

### Resolution Process

1. Verify blocker is actually resolved
2. Document resolution in comment
3. Remove "blocked" label
4. Update status to previous (usually In Progress)
5. Notify agent to resume

### Resolution Comment Template

```markdown
## Unblocked

**Resolution:** Database credentials received from DBA
**Resolved:** 2024-01-15 18:00 UTC
**Next Action:** Resume implementation

Returning to **In Progress**.
```

---

## 5.10 Invalid Transitions

### Invalid Transition Attempts

| Attempted | Why Invalid | What to Do |
|-----------|-------------|------------|
| Backlog → In Progress | Skips Todo | Move to Todo first, then In Progress |
| Todo → In Review | Skips In Progress | Move to In Progress first, then In Review |
| In Review → Backlog | Backwards too far | If abandoning, move to In Progress then Todo then Backlog |
| Done → Any | Done is terminal | If needs more work, create new issue |
| In Progress → Done | Skips review | Must create PR, go through review |

### Handling Invalid Requests

If an agent requests an invalid transition:

1. **Reject the request**
2. **Explain why it's invalid**
3. **Suggest correct path**

Example response:
```
Cannot move directly from Todo to In Review.
The correct path is:
1. Todo → In Progress (start work, create branch)
2. In Progress → In Review (create PR)

Please move to In Progress first.
```

### Script: Validate Transition

```python
VALID_TRANSITIONS = {
    "Backlog": ["Todo"],
    "Todo": ["Backlog", "In Progress", "Blocked"],
    "In Progress": ["Todo", "In Review", "Blocked"],
    "In Review": ["In Progress", "Done", "Blocked"],
    "Done": [],  # Terminal
    "Blocked": ["Todo", "In Progress"]
}

def is_valid_transition(from_status, to_status):
    return to_status in VALID_TRANSITIONS.get(from_status, [])
```
