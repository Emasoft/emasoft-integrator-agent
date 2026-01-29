# Handoff Protocols Reference

## Purpose

This document defines the standard protocols for handing off tasks, documents, and communications between the orchestrator and remote agents in the ATLAS ecosystem.

---

## Contents

- [Document Delivery Protocol](#document-delivery-protocol)
- [Task Delegation Protocol](#task-delegation-protocol)
- [Acknowledgment Protocol](#acknowledgment-protocol)
- [Completion Reporting Protocol](#completion-reporting-protocol)
- [Blocker Escalation Protocol](#blocker-escalation-protocol)

---

## Document Delivery Protocol

All documents (.md files) shared between agents MUST follow this protocol:

### Delivery Rules

1. **NEVER embed full document content in AI Maestro messages**
2. Upload document to GitHub issue as comment attachment
3. Send AI Maestro message with document URL only
4. Recipient downloads and stores in `design/received/`

### Message Format

```json
{
  "to": "{{AGENT_SESSION}}",
  "subject": "document_delivery",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "message": "Document ready. View: {{GITHUB_ISSUE_URL}}"
  }
}
```

### Storage Structure

```
design/received/
  tasks/         # Task delegation documents
  reports/       # Completion and status reports
  acks/          # Acknowledgment documents
  specs/         # Specification documents
  plans/         # Planning documents
  sync/          # Synchronization documents
```

---

## Task Delegation Protocol

When orchestrator delegates a task to a remote agent:

1. **Compile task template** with all variables substituted
2. **Upload to GitHub issue** as comment
3. **Send AI Maestro message** with URL
4. **Wait for ACK** within timeout period
5. **Track in GitHub Project** board

### Template Reference

See: [TASK_DELEGATION_TEMPLATE.md](../../remote-agent-coordinator/templates/handoff/TASK_DELEGATION_TEMPLATE.md)

---

## Acknowledgment Protocol

Remote agents MUST acknowledge task receipt:

### ACK Format

```
[ACK] {{TASK_ID}} - {{STATUS}}
Understanding: {{ONE_LINE_SUMMARY}}
```

### Status Values

| Status | Meaning |
|--------|---------|
| RECEIVED | Task received, will begin work immediately |
| CLARIFICATION_NEEDED | Need more info (list questions) |
| REJECTED | Cannot accept task (explain why) |
| QUEUED | Have prior tasks, will start after them |

### Timeout Rules

- Default timeout: 5 minutes
- After timeout: Orchestrator sends reminder
- After 2 reminders: Mark agent as unresponsive

### Template Reference

See: [ACK_TEMPLATE.md](../../remote-agent-coordinator/templates/handoff/ACK_TEMPLATE.md)

---

## Completion Reporting Protocol

When agent completes a task:

1. **Create completion report** using template
2. **Upload to GitHub issue** as comment
3. **Update GitHub issue labels** (status:complete)
4. **Send AI Maestro message** with URL
5. **Wait for orchestrator sign-off**

### Template Reference

See: [COMPLETION_REPORT_TEMPLATE.md](../../remote-agent-coordinator/templates/handoff/COMPLETION_REPORT_TEMPLATE.md)

---

## Blocker Escalation Protocol

When agent encounters a blocker:

1. **Document blocker** with context and impact
2. **Upload to GitHub issue** as comment
3. **Update GitHub issue labels** (status:blocked)
4. **Send AI Maestro message** with URGENT priority
5. **Wait for orchestrator response**

### Blocker Categories

| Category | Example |
|----------|---------|
| Missing dependency | Required package not available |
| Auth failure | Cannot access required resource |
| Spec ambiguity | Requirements unclear |
| Technical block | API limit, rate limiting |
| Conflict | Merge conflict, resource contention |

### Template Reference

See: [BLOCKER_REPORT_TEMPLATE.md](../../remote-agent-coordinator/templates/handoff/BLOCKER_REPORT_TEMPLATE.md)

---

## Integration with Other Protocols

This protocol integrates with:

- **echo-acknowledgment-protocol.md** - ACK timing and retries
- **messaging-protocol.md** - AI Maestro message format
- **artifact-sharing-protocol.md** - Large file sharing
- **document-storage-protocol.md** - Local storage rules

---

## Troubleshooting

### Document Not Received

1. Check GitHub issue for uploaded document
2. Verify AI Maestro message was sent
3. Check recipient agent is online
4. Resend with explicit URL

### ACK Not Received

1. Wait for timeout period
2. Send explicit ACK reminder
3. If still no response, mark unresponsive
4. Consider reassigning task

### Document Corrupted

1. Re-download from GitHub URL
2. Verify SHA256 hash if available
3. Contact sender for re-upload if needed

---

**Version**: 1.0.0
**Last Updated**: 2026-01-15
