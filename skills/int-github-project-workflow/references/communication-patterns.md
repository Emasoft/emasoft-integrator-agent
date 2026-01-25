# Communication Patterns

Patterns for remote agent communication, failure handling, and conflict resolution.

---

## Table of Contents

- 1. Remote Agent Communication Patterns
- 2. Failure Scenarios
- 3. Conflict Resolution Planning

---

## 1. Remote Agent Communication Patterns

### 1.1 Sending Instructions

**Always use AI Maestro API format:**

```json
{
  "to": "full-agent-session-name",
  "subject": "Subject here",
  "priority": "high",
  "content": {
    "type": "assignment|request|approval|clarification",
    "message": "Detailed instruction text"
  }
}
```

**Message Types:**

| Type | Purpose |
|------|---------|
| `assignment` | New task assignment |
| `request` | Status update request |
| `approval` | Authorization to proceed |
| `clarification` | Request for more details |

### 1.2 Receiving Reports

**Check AI Maestro inbox regularly for:**
- Completion reports
- Status updates
- Blocker notifications
- Clarification requests

**Process each report:**
1. Review against acceptance criteria
2. Update GitHub issue
3. Update progress log
4. Send acknowledgment or follow-up

### 1.3 Progress Check-In Pattern

Use the progress check-in template from [instruction-templates.md](instruction-templates.md)

**When to send check-ins:**
- No update received after expected timeframe
- Before integration points
- When blockers affect dependent tasks
- Before major milestone decisions

---

## 2. Failure Scenarios

### 2.1 Subtask Reports Failure After Others In Progress

**Orchestrator Actions:**

| Step | Action |
|------|--------|
| 1 | Document failure in GitHub issue |
| 2 | Assess impact on other tasks |
| 3 | Determine if other tasks can continue |
| 4 | Update dependencies in affected issues |
| 5 | Re-plan integration sequence |
| 6 | Send updated instructions to affected agents |

### 2.2 Integration Reports Failures

**Orchestrator Actions:**

| Step | Action |
|------|--------|
| 1 | Review failure details in report |
| 2 | Identify root cause from logs |
| 3 | Create resolution assignment |
| 4 | Send to appropriate agent |
| 5 | Request re-integration after fix |
| 6 | Update rollback plan if needed |

### 2.3 Agent Becomes Unresponsive

**Orchestrator Actions:**

| Step | Action |
|------|--------|
| 1 | Document non-response in issue |
| 2 | Reassign task to different agent |
| 3 | Provide full context: issue, previous reports |
| 4 | Update GitHub Project assignments |
| 5 | Send assignment to new agent |
| 6 | Note: No work lost (all in git) |

---

## 3. Conflict Resolution Planning

If integration reports conflicts:

### 3.1 Orchestrator Actions (planning only)

1. Review conflict report from integration executor
2. Identify conflicting files and agents
3. Determine resolution strategy
4. Create resolution instructions
5. Assign resolution to appropriate agent
6. Monitor resolution progress
7. Approve re-integration

### 3.2 Resolution Strategy Considerations

| Factor | Resolution Approach |
|--------|---------------------|
| Feature A is critical | Prioritize Feature A changes |
| Feature B has more coverage | Prioritize Feature B implementation |
| Both features needed | Manual merge preserving both |
| One feature is refinement | Keep original, add refinement |

### 3.3 Post-Resolution Verification

- All tests passing
- Both feature sets preserved (or explain omissions)
- Documentation updated for final implementation
- No functionality lost from either branch

### 3.4 Conflict Resolution Workflow

```
Conflict Reported
       ↓
Review Conflict Details
       ↓
Determine Strategy
       ↓
Create Resolution Assignment
       ↓
Send to Appropriate Agent
       ↓
Receive Resolution Report
       ↓
Verify Resolution Complete
       ↓
Approve Re-Integration
```

Use the conflict resolution template from [instruction-templates.md](instruction-templates.md)
