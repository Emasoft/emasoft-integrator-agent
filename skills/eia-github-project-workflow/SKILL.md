---
name: eia-github-project-workflow
description: Use when tracking multi-developer work with GitHub Projects boards and Kanban workflows. Trigger with /setup-project-board or when creating team boards.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
agent: api-coordinator
context: fork
---

# GitHub Project Workflow Skill

## Overview

Patterns for tracking multi-developer work using **GitHub Projects** boards and issues.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- GitHub Projects V2 enabled on the repository
- Repository write access for issue and project management

## Output

| Output Type | Location/Format | Description |
|-------------|----------------|-------------|
| Task plan | `docs_dev/plan.md` | Breakdown of work into subtasks |
| Project board | GitHub Projects V2 | Kanban board with Todo/In Progress/Review/Done columns |
| GitHub issues | Repository issues | Issues with acceptance criteria, labels, and assignments |
| Issue comments | Issue threads | Progress updates, blockers, completion reports |
| PR links | Issue comments | Pull request links for code review |
| Merge authorization | Issue comments | Final approval to merge after verification |

## Instructions

1. Analyze the requirements and create a task breakdown plan
2. Create a GitHub Project board with standard columns (Todo, In Progress, Review, Done)
3. Create GitHub issues for each task with clear acceptance criteria
4. Assign issues to developers (one task per developer)
5. Track progress by monitoring issue comments and status updates
6. Review completion by checking linked PRs and running verification tests
7. Make integration decisions and authorize merges for completed, verified tasks

**Note**: This skill handles GitHub-side tracking only. AI Maestro messaging is orchestrator-only.

### Checklist

Copy this checklist and track your progress:

- [ ] Analyze the requirements and create a task breakdown plan
- [ ] Create a GitHub Project board with standard columns
- [ ] Create GitHub issues for each task with clear acceptance criteria
- [ ] Assign issues to developers (one task per developer)
- [ ] Track progress by monitoring issue comments and status updates
- [ ] Review completion by checking linked PRs
- [ ] Run verification tests on completed work
- [ ] Make integration decisions and authorize merges

---

## Table of Contents

### Procedure Steps
For the complete GitHub Projects workflow, see [procedure-steps.md](references/procedure-steps.md):
- 1. Step 1: Analyze Requirements
- 2. Step 2: Create Task Plan
- 3. Step 3: Create GitHub Project Board
- 4. Step 4: Create Issues with Acceptance Criteria
- 5. Step 5: Assign Issues to Developers
- 6. Step 6: Monitor Progress via Issue Updates
- 7. Step 7: Review Completion via PR Links
- 8. Step 8: Integration Decision Making

### Issue Templates
For GitHub issue templates, see [instruction-templates.md](references/instruction-templates.md):
- 1. Task Assignment Template
- 2. GitHub Issue Template for Subtasks
- 3. Integration Assignment Template
- 4. Conflict Resolution Assignment Template
- 5. Merge Authorization Template
- 6. Progress Check-In Template

### Failure Handling
For handling blocked or failed tasks, see [communication-patterns.md](references/communication-patterns.md):
- 1. Failure Scenarios
  - 1.1 Subtask Reports Failure After Others In Progress
  - 1.2 Integration Reports Failures
  - 1.3 Developer Becomes Unresponsive
- 2. Conflict Resolution Planning

---

## Quick Reference

### GitHub Project Board Columns

| Column | Tasks In This State |
|--------|---------------------|
| Todo | Not yet started |
| In Progress | Developer working on it |
| Review | PR created, awaiting review |
| Done | Verified complete |

### Standard Labels

| Label | Meaning |
|-------|---------|
| `subtask` | Individual work item |
| `integration` | Integration task |
| `blocker` | Blocking other tasks |
| `verification-needed` | Requires review |

### Workflow Summary

| Step | Action | GitHub Output |
|------|--------|---------------|
| 1 | Analyze requirements | - |
| 2 | Create task plan | docs_dev/plan.md |
| 3 | Create Project Board | Board with columns |
| 4 | Create Issues | Issues with criteria |
| 5 | Assign to developers | Issue assignments |
| 6 | Monitor progress | Read issue comments |
| 7 | Review completion | Check linked PRs |
| 8 | Integration decision | Merge authorization |

### Key Principles

1. **Tracking via GitHub Projects** - Use issues and boards for all work
2. **One task per developer** - No multitasking
3. **Clear acceptance criteria** - Every issue has success criteria
4. **TDD first** - Tests before integration approval

## Examples

### Example 1: Create a New Project Board

```bash
# Create project board with standard columns
gh project create --owner OWNER --title "Sprint 1" --body "Sprint tracking"

# Add standard columns: Todo, In Progress, Review, Done
gh project field-create PROJECT_NUMBER --owner OWNER --name "Status" --data-type "SINGLE_SELECT"
```

### Example 2: Create Issue with Acceptance Criteria

```bash
gh issue create --repo owner/repo \
  --title "Implement user authentication" \
  --body "## Acceptance Criteria
- [ ] User can log in with email/password
- [ ] JWT tokens are issued on successful login
- [ ] Invalid credentials return 401 error"
```

## Error Handling

### Issue: Project board not syncing

**Cause**: Project field IDs may have changed or permissions issue.

**Solution**: Re-fetch project field IDs and verify write access.

### Issue: Developer assignment fails

**Cause**: User may not have repository access.

**Solution**: Verify user has repository collaborator access before assignment.

## Resources

- [references/procedure-steps.md](references/procedure-steps.md) - Complete workflow steps
- [references/instruction-templates.md](references/instruction-templates.md) - Issue templates
- [references/communication-patterns.md](references/communication-patterns.md) - Failure handling patterns
