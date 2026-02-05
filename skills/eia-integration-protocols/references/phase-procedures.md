# Integration Phase Procedures

This document provides step-by-step procedures for each integration phase. Follow these procedures in order to ensure consistent and reliable integration operations.

---

## Phase 1: Request Reception

### 1. Check AI Maestro Inbox
- Read unread messages from EOA or other requestors
- Parse message content for request type and context
- **Verification**: Request format is valid and complete

### 2. Extract Request Details
- Identify: PR number, issue number, branch name, error logs
- Determine: request type, priority, success criteria
- **Verification**: All required context present

### 3. Log Request
- Append to `docs_dev/integration/routing-log.md`
- Format: `[timestamp] RECEIVE request_type from requestor`
- **Verification**: Log entry written

---

## Phase 2: Routing Decision

### 1. Analyze Request Type
- Match against routing table (see "Sub-Agent Routing")
- Apply "When to Use Judgment" rules
- **Verification**: Routing decision is justified

### 2. Check Sub-Agent Availability
- Verify target sub-agent is not busy
- Confirm sub-agent has necessary skills loaded
- **Verification**: Sub-agent can accept task

### 3. Prepare Context Package
- Use Glob to find affected files
- Read error logs if present
- Extract PR/issue descriptions
- **Verification**: Context is complete

### 4. Create Status Tracking File
- Write to `docs_dev/integration/status/[task-id].md`
- Include: request details, routing decision, status: DELEGATED
- **Verification**: Status file created

---

## Phase 3: Delegation

### 1. Draft Delegation Message
- Use appropriate AI Maestro template (see "AI Maestro Message Templates")
- Include: task, context, success criteria, callback agent
- **Verification**: Message is actionable

### 2. Send to Sub-Agent
- Execute curl POST to AI Maestro API
- Wait for acknowledgment (30 second timeout)
- **Verification**: Sub-agent acknowledged

### 3. Log Delegation
- Append to routing log: `[timestamp] ROUTE request_type -> sub-agent`
- Include rationale for routing decision
- **Verification**: Delegation logged

---

## Phase 4: Monitor Completion

### 1. Wait for Sub-Agent Response
- Poll AI Maestro inbox (or receive notification)
- Check for messages from delegated sub-agent
- **Verification**: Response received within expected time

### 2. Validate Response Format
- Confirm: `[DONE/FAILED] sub-agent - brief_result`
- Extract: result status, details file path
- **Verification**: Response format is correct

### 3. Read Result Details
- Access log/report file specified by sub-agent
- Verify: quality gates status, test results, findings
- **Verification**: Results are complete

### 4. Update Status File
- Change status to COMPLETED or FAILED
- Include: completion timestamp, result summary, quality gates status
- **Verification**: Status file updated

---

## Phase 5: Report to EOA

### 1. Prepare Status Report
- Use "Reporting Integration Status" template
- Include: result, quality gates, merge status, next steps
- **Verification**: Report is comprehensive

### 2. Send to EOA
- Execute curl POST to orchestrator-eoa
- Include link to detailed report file
- **Verification**: Message sent

### 3. Handle Blockers (If Any)
- If FAILED or BLOCKED, use "Escalating Blockers" template
- Include: blocker type, details, recommendation
- Mark as requiring decision
- **Verification**: Escalation sent with urgency

### 4. Final Logging
- Append to routing log: `[timestamp] COMPLETE task-id`
- Include: result, details file path
- **Verification**: Completion logged

---

## Verification Summary

Each phase includes verification checkpoints to ensure:
- **Completeness**: All required information is present
- **Correctness**: Data format and content are valid
- **Traceability**: Actions are logged for audit
- **Accountability**: Status updates are written
- **Communication**: Messages are sent and acknowledged
