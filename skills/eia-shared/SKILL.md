---
name: eia-shared
description: >
  Use when you need shared utilities, protocols, or patterns across Integrator Agent skills.
  Provides shared reference documents used across multiple Integrator Agent skills.
license: Apache-2.0
metadata:
  author: Anthropic
  version: 1.0.0
context: fork
---

# Shared References

## Overview

This skill provides shared reference documents that are used across multiple Integrator Agent skills. It contains common patterns, protocols, and utilities that enable consistent behavior across the skill set.

## Prerequisites

None required. This is a reference skill with no external dependencies.

## Instructions

Reference this skill when you need to:
- Transfer context between agents during handoff
- Document session state for continuity
- Coordinate multi-agent workflows

## Reference Documents

### Handoff Protocols ([references/handoff-protocols.md](references/handoff-protocols.md))

Standard protocols for handing off work between agents:

- When you need to transfer context between agents → Handoff Format
- If you need to document session state → Session State Schema
- When coordinating multi-agent workflows → Coordination Patterns

## Examples

### Example 1: Agent Handoff Format

```json
{
  "handoff_type": "task_delegation",
  "from_agent": "orchestrator",
  "to_agent": "code-reviewer",
  "context": {
    "pr_number": 123,
    "repository": "owner/repo",
    "task": "Review code changes"
  },
  "session_state": {
    "files_reviewed": [],
    "comments_made": []
  }
}
```

### Example 2: Session State Schema

```json
{
  "session_id": "sess_abc123",
  "started_at": "2025-01-30T10:00:00Z",
  "current_phase": "review",
  "completed_tasks": ["fetch_pr", "analyze_diff"],
  "pending_tasks": ["post_review"]
}
```

## Error Handling

### Issue: Handoff context incomplete

**Cause**: Required fields missing from handoff payload.

**Solution**: Validate handoff against schema before sending. Required fields: `handoff_type`, `from_agent`, `to_agent`, `context`.

### Issue: Session state deserialization fails

**Cause**: Invalid JSON or schema mismatch.

**Solution**: Validate JSON structure and ensure all datetime fields use ISO 8601 format.

## Resources

- [references/handoff-protocols.md](references/handoff-protocols.md) - Complete handoff protocol reference
