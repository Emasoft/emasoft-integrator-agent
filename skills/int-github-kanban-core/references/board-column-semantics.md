# Board Column Semantics

## Table of Contents

- 2.1 [Overview of the 6-column workflow](#21-overview)
- 2.2 [Backlog column - items not yet scheduled](#22-backlog)
- 2.3 [Todo column - ready for immediate work](#23-todo)
- 2.4 [In Progress column - active development](#24-in-progress)
- 2.5 [In Review column - PR created, awaiting review](#25-in-review)
- 2.6 [Done column - completed and verified](#26-done)
- 2.7 [Blocked column - cannot proceed](#27-blocked)
- 2.8 [Column metadata and requirements table](#28-metadata-table)
- 2.9 [Visual board layout example](#29-visual-layout)

---

## 2.1 Overview

The Atlas orchestration workflow uses exactly 6 columns. Each column has a precise meaning, requirements, and rules about who can move items into it.

```
┌──────────┬──────────┬────────────┬───────────┬──────────┬──────────┐
│ Backlog  │   Todo   │In Progress │ In Review │   Done   │ Blocked  │
├──────────┼──────────┼────────────┼───────────┼──────────┼──────────┤
│ Not yet  │ Ready to │  Active    │ PR open   │ Merged   │ Cannot   │
│scheduled │  start   │   work     │           │          │ proceed  │
└──────────┴──────────┴────────────┴───────────┴──────────┴──────────┘
```

**Flow:** Backlog -> Todo -> In Progress -> In Review -> Done

**Special:** Any status can move to Blocked (and back)

---

## 2.2 Backlog

### Meaning

Items in Backlog are:
- Identified and defined
- Not yet scheduled for work
- Waiting for prioritization or capacity

### Requirements to Enter Backlog

- Issue exists with clear title and description
- Acceptance criteria defined (what "done" means)
- No duplicate of existing issue

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| New issue | Automatic (creation) |
| Todo | Orchestrator only |
| Cancelled | Orchestrator only |

### Example Items

- Features identified during planning but not yet prioritized
- Bugs that are low priority
- Improvements for future iterations

### Orchestrator Actions

When reviewing Backlog:
1. Prioritize items
2. Move high-priority items to Todo
3. Add missing details to items
4. Remove or cancel invalid items

---

## 2.3 Todo

### Meaning

Items in Todo are:
- Scheduled for the current or next sprint/iteration
- Ready to be assigned and started
- Have all prerequisites met

### Requirements to Enter Todo

- Clear acceptance criteria
- Dependencies identified (and satisfied or in progress)
- Effort estimated (optional but recommended)
- Assigned to sprint/iteration (if using iterations)

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Backlog | Orchestrator only |
| In Progress | Assigned agent (pausing) |
| Blocked | Orchestrator (after unblock) |

### Example Items

- Next module to implement
- Bug assigned for current sprint
- Refactoring scheduled for this iteration

### Orchestrator Actions

When working with Todo:
1. Assign items to agents
2. Ensure items are ready to start
3. Monitor for items stuck too long

---

## 2.4 In Progress

### Meaning

Items in In Progress are:
- Currently being worked on
- Have an assigned agent actively coding
- Have a feature branch created

### Requirements to Enter In Progress

- Assigned to an agent
- Agent has started work
- Feature branch exists (or will be created immediately)

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Todo | Assigned agent |
| In Review | Assigned agent (changes requested) |
| Blocked | Assigned agent (after unblock) |

### Expected Duration

- Should not exceed a few days
- Long items should be broken down
- Orchestrator should check items stuck > 24 hours

### Agent Responsibilities

When item is In Progress:
1. Work on the feature branch
2. Update issue with progress comments
3. Move to In Review when PR is created
4. Move to Blocked if cannot proceed

---

## 2.5 In Review

### Meaning

Items in In Review are:
- Have a Pull Request created
- PR is open and awaiting review
- Code is ready for merge (from author's perspective)

### Requirements to Enter In Review

- PR created and linked to issue
- All local tests pass
- PR description explains changes
- Ready for reviewer examination

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| In Progress | Assigned agent |

### Expected Duration

- Should not exceed 48 hours
- Escalate if review is delayed
- Ping reviewers if no activity

### Exit Conditions

| Next Status | Condition |
|-------------|-----------|
| Done | PR merged |
| In Progress | Changes requested |
| Blocked | Blocker discovered during review |

---

## 2.6 Done

### Meaning

Items in Done are:
- Code merged to main branch
- Issue closed
- Work is complete and verified

### Requirements to Enter Done

- PR merged (not just approved)
- All CI checks passed
- Issue automatically closed (via "Closes #N")

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| In Review | Automatic (PR merge) |
| Manual | Orchestrator (exceptional cases) |

### Terminal Status

Done is a terminal status. Items in Done:
- Do not move to other columns
- Are considered complete
- Can be archived

### Verification

Orchestrator should verify Done items:
- PR is actually merged
- CI passed
- No follow-up issues created

---

## 2.7 Blocked

### Meaning

Items in Blocked are:
- Cannot proceed due to external factor
- Waiting for resolution of blocker
- Need orchestrator or human attention

### Requirements to Enter Blocked

- Blocker identified and documented
- Blocker is outside agent's control
- Comment explains the blocker

### Who Can Move Items Here

| From | Who Can Move |
|------|--------------|
| Any non-terminal | Any agent or orchestrator |

### Required Documentation

When moving to Blocked, MUST provide:
- Description of the blocker
- Link to blocking issue (if applicable)
- What is needed to unblock
- When it was discovered

### Escalation Timeline

| Duration | Action |
|----------|--------|
| 0-24h | Monitor, await resolution |
| 24-48h | Ping responsible parties |
| 48-72h | Escalate to orchestrator |
| >72h | Escalate to human |

---

## 2.8 Metadata Table

| Column | Code | Is Terminal | Requires Assignment | Requires Branch | Requires PR |
|--------|------|-------------|---------------------|-----------------|-------------|
| Backlog | `backlog` | No | No | No | No |
| Todo | `todo` | No | Yes (to start) | No | No |
| In Progress | `in_progress` | No | Yes | Yes | No |
| In Review | `in_review` | No | Yes | Yes | Yes |
| Done | `done` | Yes | No | No | No |
| Blocked | `blocked` | No | Yes | - | - |

---

## 2.9 Visual Layout

```
GitHub Project Board: "Project Alpha - Sprint 3"
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Backlog (3)   │ Todo (2)      │ In Progress (2) │ In Review (1) │ Done (5) │ Blocked (1) ┃
┣━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━┫
┃ ┌───────────┐ │ ┌───────────┐ │ ┌─────────────┐ │ ┌───────────┐ │          │ ┌─────────┐ ┃
┃ │ #12       │ │ │ #8        │ │ │ #5          │ │ │ #7        │ │          │ │ #9      │ ┃
┃ │ User prefs│ │ │ Auth API  │ │ │ Data model  │ │ │ UI tests  │ │          │ │ CI setup│ ┃
┃ │           │ │ │ @agent-1  │ │ │ @agent-1    │ │ │ @agent-2  │ │          │ │ @agent-3│ ┃
┃ └───────────┘ │ └───────────┘ │ └─────────────┘ │ └───────────┘ │          │ └─────────┘ ┃
┃ ┌───────────┐ │ ┌───────────┐ │ ┌─────────────┐ │               │          │             ┃
┃ │ #13       │ │ │ #10       │ │ │ #6          │ │               │          │             ┃
┃ │ Export    │ │ │ Logging   │ │ │ Validation  │ │               │          │             ┃
┃ │           │ │ │ @agent-2  │ │ │ @agent-2    │ │               │          │             ┃
┃ └───────────┘ │ └───────────┘ │ └─────────────┘ │               │          │             ┃
┃ ┌───────────┐ │               │                 │               │          │             ┃
┃ │ #14       │ │               │                 │               │          │             ┃
┃ │ Analytics │ │               │                 │               │          │             ┃
┃ └───────────┘ │               │                 │               │          │             ┃
┗━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┷━━━━━━━━━━┷━━━━━━━━━━━━━┛
```

**Reading the Board:**
- Numbers in parentheses = item count
- `@agent-X` = assigned agent
- Issue number and title shown
- Unassigned items have no `@`
