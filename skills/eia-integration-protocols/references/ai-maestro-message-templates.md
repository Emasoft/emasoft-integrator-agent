# AI Maestro Message Templates for EIA

This document contains all AI Maestro curl command templates for Emasoft Integrator Agent (EIA) communication patterns.

## Contents

- 1.0 Standard AI Maestro API Format
- 2.0 Receiving Messages from Orchestrator (EOA)
  - 2.1 Integration Request from EOA
  - 2.2 Handoff Document Rejection
- 3.0 Sending Messages to Sub-Agents
  - 3.1 Task Delegation to Sub-Agent
- 4.0 Reporting Results to Orchestrator (EOA)
  - 4.1 Integration Status Report (Success)
  - 4.2 Integration Status Report (In Progress)
  - 4.3 Integration Status Report (Failed)
  - 4.4 Blocker Escalation (Critical Issues)
- 5.0 Quality Gate Communication
  - 5.1 PR Review Complete (All Gates Passed)
  - 5.2 PR Review Complete (Tests Failed)
  - 5.3 Merge Approved
  - 5.4 Merge Rejected
  - 5.5 Release Ready Notification

---

## 1.0 Standard AI Maestro API Format

All AI Maestro messages follow this curl command structure:

```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "<target-agent>",
    "subject": "<subject line>",
    "priority": "urgent|high|normal|low",
    "content": {
      "type": "<message-type>",
      "message": "<message body>",
      "<additional_fields>": "<values>"
    }
  }'
```

**Environment Variable Alternative:**
```bash
curl -X POST "$AIMAESTRO_API/api/messages" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

Where `$AIMAESTRO_API` defaults to `http://localhost:23000`.

---

## 2.0 Receiving Messages from Orchestrator (EOA)

### 2.1 Integration Request from EOA

**Scenario**: EOA sends a PR review request, CI fix task, or integration verification task.

**Reading Unread Messages:**
```bash
curl -s "http://localhost:23000/api/messages?agent=emasoft-integrator&action=list&status=unread" \
  | jq '.messages[] | select(.content.type == "integration-request")'
```

**Expected Message Format from EOA:**
```json
{
  "from": "orchestrator-eoa",
  "to": "emasoft-integrator",
  "subject": "Integration Request: <brief description>",
  "priority": "urgent|high|normal|low",
  "content": {
    "type": "integration-request",
    "request_type": "PR_REVIEW|CI_FIX|CODE_REVIEW|TESTING|RELEASE|ISSUE_CLOSURE",
    "context": {
      "pr_number": 456,
      "issue_number": 123,
      "branch": "feature/add-auth",
      "description": "Review authentication module PR",
      "error_logs": "path/to/logs.txt (if applicable)",
      "priority": "high"
    },
    "success_criteria": "All tests pass, code review approved, no security issues"
  }
}
```

### 2.2 Handoff Document Rejection

**Scenario**: Received handoff document fails validation (missing UUID, invalid references, TBD placeholders).

**Command:**
```bash
curl -X POST "$AIMAESTRO_API/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "[HANDOFF REJECTED] Invalid handoff document",
    "priority": "high",
    "content": {
      "type": "handoff-rejected",
      "message": "Handoff rejected. Issues: Missing UUID, file path invalid (src/auth.py does not exist), TBD placeholder in success criteria. Please correct and resubmit.",
      "validation_errors": [
        "Missing UUID",
        "File path invalid: src/auth.py",
        "TBD placeholder in success criteria"
      ]
    }
  }'
```

---

## 3.0 Sending Messages to Sub-Agents

### 3.1 Task Delegation to Sub-Agent

**Scenario**: Routing a task (PR review, bug investigation, code review) to a specialized sub-agent.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "eia-code-reviewer",
    "subject": "Review PR #456: Add auth module",
    "priority": "high",
    "content": {
      "type": "task-delegation",
      "task": "review-pr",
      "context": {
        "pr_number": 456,
        "branch": "feature/add-auth",
        "files_affected": ["src/auth.py", "tests/test_auth.py"],
        "description": "New authentication module with JWT support",
        "focus_areas": ["security", "test coverage", "error handling"]
      },
      "success_criteria": "Code quality score > 8/10, no security vulnerabilities, test coverage > 90%",
      "priority": "high",
      "callback_agent": "emasoft-integrator"
    }
  }'
```

**Valid Sub-Agent Targets:**
- `eia-api-coordinator` - GitHub API operations
- `eia-code-reviewer` - Code quality assessment
- `eia-pr-evaluator` - PR readiness check
- `eia-integration-verifier` - Post-merge verification
- `eia-bug-investigator` - CI/test failures
- `eia-github-sync` - Repository state sync
- `eia-committer` - Creating commits
- `eia-screenshot-analyzer` - Visual verification
- `eia-debug-specialist` - Complex debugging
- `eia-test-engineer` - Test creation/analysis

---

## 4.0 Reporting Results to Orchestrator (EOA)

### 4.1 Integration Status Report (Success)

**Scenario**: PR review completed successfully, all quality gates passed, ready to merge.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Integration Status: PR #456 - COMPLETED",
    "priority": "normal",
    "content": {
      "type": "integration-status",
      "task_id": "pr-456-review",
      "status": "COMPLETED",
      "result": {
        "pr_number": 456,
        "quality_gates": ["code_review: PASS", "tests: PASS", "security: PASS"],
        "merge_status": "MERGED",
        "details_file": "docs_dev/integration/reports/pr-456-report.md"
      },
      "next_steps": "Issue #123 ready to close, all acceptance criteria met"
    }
  }'
```

### 4.2 Integration Status Report (In Progress)

**Scenario**: Integration task in progress, awaiting sub-agent completion.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Integration Status: PR #456 - IN PROGRESS",
    "priority": "normal",
    "content": {
      "type": "integration-status",
      "task_id": "pr-456-review",
      "status": "IN_PROGRESS",
      "result": {
        "pr_number": 456,
        "current_phase": "code-review",
        "assigned_to": "eia-code-reviewer",
        "estimated_completion": "2026-02-05 16:00"
      },
      "next_steps": "Awaiting code review completion"
    }
  }'
```

### 4.3 Integration Status Report (Failed)

**Scenario**: Integration task failed due to quality gate failure or technical issue.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Integration Status: PR #456 - FAILED",
    "priority": "high",
    "content": {
      "type": "integration-status",
      "task_id": "pr-456-review",
      "status": "FAILED",
      "result": {
        "pr_number": 456,
        "quality_gates": ["code_review: PASS", "tests: FAIL", "security: PASS"],
        "merge_status": "BLOCKED",
        "failure_reason": "Test coverage below 90% threshold (current: 78%)",
        "details_file": "docs_dev/integration/reports/pr-456-report.md"
      },
      "next_steps": "Request implementor add tests for uncovered code paths"
    }
  }'
```

### 4.4 Blocker Escalation (Critical Issues)

**Scenario**: Critical blocker prevents integration (security vulnerability, resource conflict, policy unclear).

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "[BLOCKER] PR #456 Security Issue",
    "priority": "urgent",
    "content": {
      "type": "blocker-escalation",
      "task_id": "pr-456-review",
      "blocker_type": "QUALITY_GATE_FAILED",
      "details": {
        "description": "PR #456 has security vulnerability (SQL injection in auth.py:42)",
        "severity": "critical",
        "blocking_gate": "security-scan",
        "recommendation": "Reject PR, request fix from implementor"
      },
      "requires_decision": true
    }
  }'
```

**Valid Blocker Types:**
- `QUALITY_GATE_FAILED` - Tests failed, coverage insufficient, security issue
- `RESOURCE_CONFLICT` - Multiple agents editing same file
- `POLICY_UNCLEAR` - Quality gate policy needs clarification
- `DEPENDENCY_MISSING` - Missing dependencies or external services

---

## 5.0 Quality Gate Communication

### 5.1 PR Review Complete (All Gates Passed)

**Scenario**: PR review finished, all quality gates passed, no issues found.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "PR Review Complete: PR #456 - ALL GATES PASSED",
    "priority": "normal",
    "content": {
      "type": "integration-status",
      "task_id": "pr-456-review",
      "status": "COMPLETED",
      "result": {
        "pr_number": 456,
        "quality_gates": [
          "code_review: PASS (9.2/10)",
          "tests: PASS (93% coverage)",
          "security: PASS (0 issues)",
          "ci_pipeline: PASS"
        ],
        "merge_status": "APPROVED",
        "reviewer": "eia-code-reviewer",
        "details_file": "docs_dev/integration/reports/pr-456-report.md"
      },
      "next_steps": "Ready to merge, issue #123 can close after merge"
    }
  }'
```

### 5.2 PR Review Complete (Tests Failed)

**Scenario**: PR review found test failures or insufficient test coverage.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "PR Review Complete: PR #456 - TESTS FAILED",
    "priority": "high",
    "content": {
      "type": "integration-status",
      "task_id": "pr-456-review",
      "status": "FAILED",
      "result": {
        "pr_number": 456,
        "quality_gates": [
          "code_review: PASS (8.5/10)",
          "tests: FAIL (78% coverage, threshold 90%)",
          "security: PASS (0 issues)",
          "ci_pipeline: FAIL (3 tests failing)"
        ],
        "merge_status": "BLOCKED",
        "failing_tests": [
          "test_auth.py::test_invalid_token",
          "test_auth.py::test_expired_token",
          "test_middleware.py::test_unauthorized_access"
        ],
        "details_file": "docs_dev/integration/reports/pr-456-report.md"
      },
      "next_steps": "Request implementor fix failing tests and add coverage for uncovered code paths"
    }
  }'
```

### 5.3 Merge Approved

**Scenario**: Quality gates passed, PR approved for merge into main branch.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Merge Approved: PR #456",
    "priority": "normal",
    "content": {
      "type": "merge-decision",
      "decision": "APPROVED",
      "pr_number": 456,
      "branch": "feature/add-auth",
      "target_branch": "main",
      "rationale": "All quality gates passed: code quality 9.2/10, test coverage 93%, no security issues, CI green",
      "merged_by": "emasoft-integrator",
      "merge_commit": "abc123def456",
      "linked_issues": [123]
    }
  }'
```

### 5.4 Merge Rejected

**Scenario**: Quality gates failed, PR rejected and cannot be merged.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Merge Rejected: PR #456",
    "priority": "high",
    "content": {
      "type": "merge-decision",
      "decision": "REJECTED",
      "pr_number": 456,
      "branch": "feature/add-auth",
      "target_branch": "main",
      "rationale": "Critical security vulnerability detected: SQL injection in auth.py:42",
      "blocking_issues": [
        {
          "type": "security",
          "severity": "critical",
          "description": "SQL injection vulnerability",
          "location": "auth.py:42"
        }
      ],
      "required_actions": [
        "Fix SQL injection by using parameterized queries",
        "Re-run security scan",
        "Request re-review"
      ]
    }
  }'
```

### 5.5 Release Ready Notification

**Scenario**: All PRs merged, tests passed, release candidate ready for tagging.

**Command:**
```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "emasoft-integrator",
    "to": "orchestrator-eoa",
    "subject": "Release Ready: v1.2.0",
    "priority": "high",
    "content": {
      "type": "release-ready",
      "version": "1.2.0",
      "release_branch": "release/1.2.0",
      "included_prs": [456, 457, 458],
      "closed_issues": [123, 124, 125],
      "quality_status": {
        "all_tests_passing": true,
        "security_scan": "PASS",
        "code_quality_avg": "9.1/10",
        "test_coverage": "94%"
      },
      "release_notes_file": "docs_dev/integration/release-notes-1.2.0.md",
      "next_steps": "Create git tag v1.2.0, push to main, create GitHub release"
    }
  }'
```

---

## Notes

- Always use `content.type` field to categorize message types for filtering
- Priority levels: `urgent` (critical blockers), `high` (failed gates), `normal` (status updates), `low` (informational)
- Always include `details_file` path for full reports (avoid verbose messages)
- Use `callback_agent` field when delegating to sub-agents to specify who should receive the response
- All file paths should be relative to project root or absolute paths
- Message content must be a JSON object with `type` and `message` fields, NOT a plain string
