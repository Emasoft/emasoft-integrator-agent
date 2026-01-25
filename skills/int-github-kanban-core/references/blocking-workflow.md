# Blocking Workflow

## Table of Contents

- 6.1 [What constitutes a blocker](#61-what-is-a-blocker)
- 6.2 [How to mark an item as blocked](#62-marking-as-blocked)
- 6.3 [Required information when blocking](#63-required-information)
- 6.4 [Blocker escalation timeline](#64-escalation-timeline)
- 6.5 [Resolving blockers and resuming work](#65-resolving-blockers)
- 6.6 [Cross-issue blocking dependencies](#66-cross-issue-blocking)
- 6.7 [External blockers](#67-external-blockers)
- 6.8 [Blocker status reporting](#68-status-reporting)

---

## 6.1 What Is a Blocker

A blocker is an impediment that prevents work from continuing AND that the assigned agent cannot resolve independently.

### Is a Blocker

| Situation | Why It's a Blocker |
|-----------|-------------------|
| Missing credentials | Agent cannot provision access |
| Dependency issue not resolved | Must wait for other work |
| API/service is down | External factor, cannot control |
| Requirements unclear | Need clarification from human |
| Infrastructure not ready | DevOps/admin action needed |
| Review required before continuing | Waiting for human decision |

### Is NOT a Blocker

| Situation | Why It's NOT a Blocker |
|-----------|------------------------|
| Tests failing | Agent should fix tests |
| Code needs refactoring | Agent should refactor |
| Missing documentation | Agent should write it |
| Merge conflicts | Agent should resolve |
| Unclear how to implement | Agent should research |
| Takes longer than expected | Not a blocker, just slow |

### Decision Tree

```
Can agent resolve this independently?
  │
  ├─ YES → NOT a blocker. Keep working.
  │
  └─ NO → Is this preventing ALL progress?
           │
           ├─ YES → BLOCKER. Move to Blocked.
           │
           └─ NO → Continue other work. Note the issue.
```

---

## 6.2 Marking as Blocked

### Step 1: Update Board Status

Move the card to Blocked column via GraphQL:

```bash
# Get status field and option IDs
STATUS_INFO=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID")

FIELD_ID=$(echo "$STATUS_INFO" | jq -r '.data.node.field.id')
BLOCKED_ID=$(echo "$STATUS_INFO" | jq -r '.data.node.field.options[] | select(.name == "Blocked") | .id')

# Update status
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) { projectV2Item { id } }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$BLOCKED_ID"
```

### Step 2: Add Blocked Label

```bash
gh issue edit 42 --add-label "blocked"
```

### Step 3: Document the Blocker

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Blocked

**Previous Status:** In Progress
**Blocker:** Missing database credentials for staging environment
**Type:** Access
**Blocking Issue:** N/A
**What's Needed:** DBA to provide credentials in vault
**Impact:** Cannot test data layer implementation
**Discovered:** 2024-01-15 15:00 UTC

@orchestrator-master Please escalate to DBA team.
EOF
)"
```

### Step 4: Notify Orchestrator

```bash
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "orchestrator-master",
    "subject": "Issue #42 Blocked",
    "priority": "high",
    "content": {
      "type": "blocker",
      "message": "Issue #42 is blocked. Blocker: Missing database credentials. Need DBA action.",
      "data": {
        "issue_number": 42,
        "blocker_type": "access",
        "what_needed": "DBA to provide credentials"
      }
    }
  }'
```

---

## 6.3 Required Information

Every blocker MUST have this information documented:

### Blocker Template

```markdown
## Blocked

**Previous Status:** [Status before blocking]
**Blocker:** [One-line description]
**Type:** [Technical | Access | Clarification | External | Resource | Dependency]
**Blocking Issue:** #[number] or N/A
**What's Needed:** [Specific action to unblock]
**Impact:** [What work is prevented]
**Discovered:** YYYY-MM-DD HH:MM UTC
**Expected Resolution:** [If known]

[Additional context if needed]
```

### Field Descriptions

| Field | Description | Example |
|-------|-------------|---------|
| Previous Status | Where to return after unblocking | "In Progress" |
| Blocker | Clear, concise description | "Missing API key for payment service" |
| Type | Category for routing | "Access" |
| Blocking Issue | Related issue if dependency | "#35" |
| What's Needed | Actionable next step | "DevOps to add key to secrets manager" |
| Impact | What can't proceed | "Cannot implement payment flow" |
| Discovered | Timestamp for tracking | "2024-01-15 15:00 UTC" |
| Expected Resolution | ETA if known | "Tomorrow after DevOps standup" |

---

## 6.4 Escalation Timeline

Blockers have an escalation timeline. The longer a blocker persists, the higher it escalates.

### Timeline

| Duration | Action | Who |
|----------|--------|-----|
| 0-4 hours | Monitor, await resolution | Agent |
| 4-24 hours | Ping responsible party | Agent |
| 24-48 hours | Escalate to orchestrator | Agent/Orchestrator |
| 48-72 hours | Orchestrator escalates to human | Orchestrator |
| >72 hours | Human decides: resolve, defer, or cancel | Human |

### Escalation Actions

#### At 4 Hours

```markdown
**Blocker Update (4h)**

Still blocked. Pinging @responsible-party for resolution.
```

#### At 24 Hours

```markdown
**Blocker Escalation (24h)**

@orchestrator-master This issue has been blocked for 24 hours.
Blocker: [brief description]
Recommended action: [suggestion]
```

#### At 48 Hours

```markdown
**Blocker Escalation (48h)**

@orchestrator-master @human-owner This issue has been blocked for 48 hours.
Blocker: [brief description]
Impact: [affected work]
Options:
1. [Option 1]
2. [Option 2]
3. Defer to next sprint
```

---

## 6.5 Resolving Blockers

### Resolution Process

1. **Verify blocker is resolved** - Don't assume
2. **Document resolution** - Comment on issue
3. **Remove blocked label** - `gh issue edit 42 --remove-label "blocked"`
4. **Update status** - Move back to previous status
5. **Notify agent** - Via AI Maestro

### Resolution Comment Template

```markdown
## Unblocked

**Resolution:** DBA added credentials to vault
**Resolved By:** @dba-admin
**Resolved:** 2024-01-16 09:00 UTC
**Duration Blocked:** 18 hours

Agent @agent-1 can now continue work.
Returning to **In Progress**.
```

### CLI Commands

```bash
# Add resolution comment
gh issue comment 42 --body "$(cat <<'EOF'
## Unblocked
**Resolution:** Database credentials added to vault
**Resolved:** 2024-01-16 09:00 UTC
Returning to **In Progress**.
EOF
)"

# Remove blocked label
gh issue edit 42 --remove-label "blocked"

# Update status to In Progress
# [GraphQL mutation to set status]

# Notify agent
curl -X POST "http://localhost:23000/api/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "agent-1",
    "subject": "Issue #42 Unblocked",
    "priority": "high",
    "content": {
      "type": "unblocked",
      "message": "Issue #42 is unblocked. Credentials are now in vault. Please resume work."
    }
  }'
```

---

## 6.6 Cross-Issue Blocking

When one issue blocks another, use GitHub's dependency tracking.

### Marking Dependency

In the blocked issue, reference the blocking issue:

```markdown
## Blocked

**Blocker:** Depends on #35 (API client library)
**Type:** Dependency
**Blocking Issue:** #35
**What's Needed:** Issue #35 must be completed first
**Impact:** Cannot implement integration without client library
```

### Tracking Dependencies

```bash
# Find issues blocked by #35
gh issue list --search "Blocked Blocking Issue: #35" --json number,title
```

### Automatic Unblocking

When blocking issue is resolved, manually unblock dependent issues or set up automation to detect.

### Dependency Chain Example

```
#35 API Client Library
  └─ blocks #36 Payment Integration
       └─ blocks #37 Checkout Flow
            └─ blocks #38 Order Confirmation
```

---

## 6.7 External Blockers

External blockers are outside the project's control.

### Examples

- Third-party API outage
- Vendor not responding
- Regulatory approval pending
- External team dependency

### Handling External Blockers

```markdown
## Blocked (External)

**Blocker:** Payment gateway API is down
**Type:** External
**External Party:** Stripe
**Status Page:** https://status.stripe.com
**What's Needed:** Stripe to restore service
**Impact:** Cannot test or develop payment flow
**Workaround:** None available

**Monitoring:** Watching status page for updates.
```

### Escalation for External

External blockers may need human decision:

```markdown
**Blocker Escalation (External - 48h)**

@human-owner External blocker persists.

Blocker: Stripe API down
Duration: 48 hours
External status: "Investigating"

Options:
1. Continue waiting (risk: timeline slip)
2. Implement mock for development (risk: integration issues later)
3. Consider alternative provider (risk: significant rework)

Please advise.
```

---

## 6.8 Status Reporting

### Query Blocked Items

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                labels(first: 10) { nodes { name } }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == "Blocked"))
  | { issue: .content.number, title: .content.title }
'
```

### Blocker Summary Report

```markdown
## Blocker Report - 2024-01-15

| Issue | Title | Blocker Type | Duration | Status |
|-------|-------|--------------|----------|--------|
| #42 | Auth module | Access | 18h | Awaiting DBA |
| #45 | API client | Dependency | 4h | Waiting on #35 |
| #48 | Payments | External | 48h | Stripe outage |

**Total Blocked:** 3
**Escalated:** 1 (#48)
**Action Needed:** Human decision on #48
```
