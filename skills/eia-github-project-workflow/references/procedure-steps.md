# Procedure Steps

Step-by-step orchestration workflow for multi-developer coordination.

---

## Table of Contents

- 1. Step 1: Analyze Requirements
- 2. Step 2: Create Task Plan
- 3. Step 3: Create GitHub Project Board
- 4. Step 4: Prepare Agent Instructions
- 5. Step 5: Send Task Assignments via AI Maestro
- 6. Step 6: Monitor Progress Through Reports
- 7. Step 7: Review Completion Reports
- 8. Step 8: Integration Decision Making

---

## 1. Step 1: Analyze Requirements

**Actions:**
- Understand full scope
- Identify parallelizable components
- Estimate complexity and dependencies
- Document analysis in docs_dev/analysis.md

**Verification Checklist:**
- [ ] Analysis document exists in docs_dev/analysis.md
- [ ] All requirements listed
- [ ] Parallelizable components identified
- [ ] Dependencies mapped

---

## 2. Step 2: Create Task Plan

**Create `plan.md` in docs_dev/:**

```markdown
# Feature: [Name]

## Total Scope
[Overall objective]

## Parallelizable Subtasks
1. **Subtask 1** - [Description] - Depends on: [list] - Assign to: [agent-name]
2. **Subtask 2** - [Description] - Depends on: [list] - Assign to: [agent-name]
3. **Subtask 3** - [Description] - Depends on: [list] - Assign to: [agent-name]

## Integration Points
- [Point 1] after tasks 1, 2
- [Point 2] after tasks 2, 3

## Critical Path
Task sequence required for completion

## Rollback Plan
How to handle if integration fails
```

**Verification Checklist:**
- [ ] Plan document exists in docs_dev/plan.md
- [ ] All subtasks listed with dependencies
- [ ] Integration points defined
- [ ] Critical path identified
- [ ] Rollback plan documented

---

## 3. Step 3: Create GitHub Project Board

**Board Structure:**
- Project name: `Feature: [Name]`
- Columns: `Todo`, `In Progress`, `Review`, `Done`
- Issues created for each subtask
- Labels: `subtask`, `integration`, `blocker`, `verification-needed`

**Verification Checklist:**
- [ ] GitHub Project board created
- [ ] All issues created with complete templates
- [ ] Dependencies documented in each issue
- [ ] Success criteria defined for each task
- [ ] Labels applied correctly

---

## 4. Step 4: Prepare Agent Instructions

For each subtask, create detailed instructions to send via AI Maestro.

**Use template from**: [instruction-templates.md](instruction-templates.md)

**Verification Checklist:**
- [ ] Instructions prepared for each subtask
- [ ] All instructions use standard template
- [ ] Completion criteria clearly defined
- [ ] Reporting requirements specified
- [ ] GitHub issue numbers referenced correctly

---

## 5. Step 5: Send Task Assignments via AI Maestro

**Message Sending Pattern:**

```
For each remote agent:
1. Prepare instruction document
2. Send AI Maestro message:
   - To: [full-agent-session-name]
   - Subject: "ASSIGNMENT: GH-[number] - [task name]"
   - Priority: high/normal
   - Content: {"type": "assignment", "message": "[instruction text]"}
3. Update GitHub issue with assignment confirmation
4. Move issue to "In Progress" column
```

**DO NOT:**
- Execute the task yourself
- Run commands on behalf of the agent
- Check git status directly
- Run tests yourself

**Verification Checklist:**
- [ ] All AI Maestro messages sent successfully
- [ ] Full agent session names used
- [ ] GitHub issues updated with assignment notes
- [ ] Issues moved to "In Progress" column
- [ ] Progress log updated with assignments

---

## 6. Step 6: Monitor Progress Through Reports

**Monitoring Activities (ALL via reports, NO direct execution):**

1. Check AI Maestro inbox for messages
2. Review completion reports as they arrive
3. Check GitHub issue updates
4. Review GitHub Project board status
5. Maintain progress log in docs_dev/

**Progress Log Update Format:**
```
Updated: [timestamp]
Source: AI Maestro message from [agent-name]
Status: GH-[number] changed from in_progress to review
Progress: X/Y tasks completed
Next: [upcoming integration point]
Blockers: [list any reported blockers]
```

**Verification Checklist:**
- [ ] AI Maestro inbox checked regularly
- [ ] Progress log maintained in docs_dev/
- [ ] GitHub Project board reflects current status
- [ ] All reports reviewed and acknowledged
- [ ] Blockers documented and addressed

---

## 7. Step 7: Review Completion Reports

When a completion report is received:

**Review Checklist:**
1. Verify report format is complete
2. Check all success criteria met
3. Confirm tests passing (local + CI/CD)
4. Review detailed logs in GitHub issue
5. Verify no code coverage decrease
6. Check documentation updated
7. Request peer review if needed

**If verification PASSES:**
- Update GitHub issue status to "Done"
- Move to "Done" column
- Update progress log
- Send acknowledgment message to agent
- Plan next steps if applicable

**If verification FAILS:**
- Document missing criteria
- Send clarification request to agent
- Keep issue in "In Progress" or move to "Review"
- Update blocker list if needed

**Verification Checklist:**
- [ ] All completion reports reviewed against criteria
- [ ] GitHub issues updated with review results
- [ ] Acknowledgments sent to agents
- [ ] Progress log reflects completed tasks
- [ ] Integration readiness assessed

---

## 8. Step 8: Integration Decision Making

When all subtasks report completion:

### 8.1 Review Phase

- Verify all completion reports
- Check for reported conflicts
- Review integration test plans
- Identify integration executor agent

### 8.2 Integration Assignment

Send integration instructions using template from [instruction-templates.md](instruction-templates.md)

### 8.3 Assign Integration Executor

- Send instruction via AI Maestro
- Create GitHub issue for integration
- Track integration progress

### 8.4 Review Integration Report

- Verify all tests passing
- Review conflict resolutions
- Check integration logs

### 8.5 Approve or Reject Merge

- If approved: Send merge authorization
- If rejected: Document issues, request fixes

**Verification Checklist:**
- [ ] All subtasks verified complete
- [ ] Integration executor assigned
- [ ] Integration instructions sent
- [ ] Integration report reviewed
- [ ] Merge decision made and communicated
