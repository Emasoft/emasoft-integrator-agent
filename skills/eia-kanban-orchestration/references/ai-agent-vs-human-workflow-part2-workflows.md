# AI Agent vs Human Workflow - Part 2: Workflows and Coordination

<a name="part-2-toc"></a>
## Table of Contents

- 9.5 [Review workflow differences](#95-review-workflow)
- 9.6 [Handoff protocols](#96-handoff)
- 9.7 [Mixed team coordination](#97-mixed-team)
- 9.8 [Escalation paths for AI blockers](#98-escalation)

---

## 9.5 Review Workflow

### AI Agent as Author

When AI agent creates PR:

1. AI creates PR with detailed description
2. PR assigned to reviewer (human or AI)
3. AI responds to review comments
4. AI updates code based on feedback
5. Human/AI approves
6. PR merged

### AI Agent as Reviewer

AI can review but CANNOT approve (policy):

```bash
# AI reviewer adds comments
gh pr review 123 --comment --body "$(cat <<'EOF'
## Review Notes

**Code Quality:** Good
**Test Coverage:** Adequate
**Concerns:**
- Line 42: Consider null check
- Line 78: Magic number, use constant

**Recommendation:** Address above, then ready for human approval
EOF
)"
```

### Human as Reviewer

Human reviewers can:
- Approve PRs
- Request changes
- Merge PRs
- Final authority on code quality

### Review Escalation

```
AI Review (suggestions) -> Human Review (approval) -> Merge

AI agents cannot merge without human approval on critical paths.
```

---

## 9.6 Handoff

### AI to AI Handoff

When one AI agent hands off to another:

```bash
# 1. Current agent documents state
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to Next Agent

**Previous Agent:** @implementer-1
**Work Done:**
- Feature branch created: feature/issue-42-auth
- Core logic implemented (src/auth/jwt.py)
- 3 commits pushed

**Work Remaining:**
- Write unit tests
- Add integration test
- Update documentation

**Notes:**
- Using PyJWT library for token handling
- See commit abc123 for token validation logic
- Test file started at tests/test_jwt.py (incomplete)

**Branch is clean and pushed.**
EOF
)"

# 2. Remove current assignee
gh issue edit 42 --remove-assignee implementer-1

# 3. Assign new agent
gh issue edit 42 --add-assignee implementer-2

# 4. Notify new agent using the agent-messaging skill
# Send a message with Recipient: implementer-2, Subject: Assignment handoff, Priority: high
```

### AI to Human Handoff

When AI hands off to human:

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to Human Developer

**AI Agent:** @implementer-1
**Human:** @human-dev

**What's Done:**
- Core implementation complete
- PR #123 created
- Tests written and passing

**What Needs Human Attention:**
- Code review approval
- Deployment configuration
- Final integration testing

**Ready for human takeover.**
EOF
)"
```

### Human to AI Handoff

When human hands off to AI:

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to AI Agent

**Human:** @human-dev
**AI Agent:** @implementer-2

**What I've Done:**
- Architecture design complete
- API spec finalized
- Core interfaces defined

**What AI Should Do:**
- Implement the interfaces
- Write comprehensive tests
- Follow the spec exactly

**Reference:**
- API spec: docs/api-spec.md
- Design doc: docs/auth-design.md
- Example: src/examples/auth_example.py

AI agent should have everything needed to proceed.
EOF
)"
```

---

## 9.7 Mixed Team

When AI agents and humans work together.

### Team Composition

| Role | Agent Type | Responsibilities |
|------|------------|------------------|
| Orchestrator | AI | Planning, assignment, tracking |
| Implementer | AI | Coding, testing |
| Reviewer | Human | Code approval, quality |
| Lead | Human | Architecture, decisions |

### Coordination Pattern

```
                    +---------------+
                    | Orchestrator  |
                    |     (AI)      |
                    +-------+-------+
                            |
            +---------------+---------------+
            v               v               v
      +---------+    +-------------+   +---------+
      |Implmtr 1|    | Implementer |   |Implmtr 3|
      |  (AI)   |    |   2 (AI)    |   |  (AI)   |
      +----+----+    +------+------+   +----+----+
           |                |               |
           +----------------+---------------+
                            |
                      +-----v-----+
                      |Code Review|
                      | (Human)   |
                      +-----+-----+
                            |
                      +-----v-----+
                      |Tech Lead  |
                      | (Human)   |
                      +-----------+
```

### Communication Flow

1. Orchestrator assigns via AI Maestro
2. AI agents report via AI Maestro + GitHub
3. Humans review via GitHub
4. Orchestrator aggregates status from board

---

## 9.8 Escalation

When AI agents cannot proceed.

### Escalation Triggers

| Trigger | Escalate To | Timeline |
|---------|-------------|----------|
| Technical blocker | Orchestrator | Immediate |
| Access issue | Orchestrator then Human | 4 hours |
| Design question | Human lead | Immediate |
| Test failure (persistent) | Human reviewer | After 3 attempts |
| External dependency | Human | 24 hours |

### Escalation Process

**Step 1: AI agent reports blocker.** Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-master`
- **Subject**: `Escalation: Issue #42 Blocked`
- **Priority**: `urgent`
- **Content**: `{"type": "escalation", "message": "Cannot proceed on #42. Need human decision.", "data": {"issue_number": 42, "blocker": "Design ambiguity in API spec", "question": "Should auth tokens be stateless or server-validated?", "impact": "Cannot proceed with implementation", "options": ["Stateless JWT", "Server-side session", "Hybrid"]}}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

```bash
# 2. Orchestrator escalates to human
gh issue comment 42 --body "$(cat <<'EOF'
## Escalation to Human Lead

@human-lead AI agent needs decision:

**Question:** Should auth tokens be stateless or server-validated?

**Options:**
1. Stateless JWT (simpler, but can't revoke)
2. Server-side session (can revoke, more complexity)
3. Hybrid approach

**Impact:** Implementation blocked until decision made.

Please advise.
EOF
)"
```

### Escalation Response Flow

```
AI Agent blocks -> Orchestrator notified
                         |
          +--------------+--------------+
          v                             v
    Can Orchestrator              Needs Human
    resolve?                      Decision
          |                             |
     YES  |                             |
          v                             v
    Resolve, notify              Escalate via
    agent to continue            GitHub comment
                                       |
                                       v
                                Human responds
                                       |
                                       v
                                Orchestrator
                                updates agent
                                       |
                                       v
                                Agent continues
```

---

## Previous: Part 1

Return to [ai-agent-vs-human-workflow-part1-fundamentals.md](ai-agent-vs-human-workflow-part1-fundamentals.md) for:
- Key differences in AI vs human workflow
- Assignment strategies for AI agents
- Assignment strategies for human developers
- Communication channels

## Index

Return to [ai-agent-vs-human-workflow.md](ai-agent-vs-human-workflow.md) for the complete table of contents.
