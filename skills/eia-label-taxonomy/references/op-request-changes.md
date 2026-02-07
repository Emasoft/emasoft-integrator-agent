---
name: op-request-changes
description: Operation procedure for requesting changes on a PR after review.
workflow-instruction: "support"
procedure: "support-skill"
---

# Operation: Request Changes

## Purpose

After finding issues during PR review, formally request changes by updating labels and leaving a review with specific feedback.

## When to Use

- When review finds issues that must be addressed
- When code doesn't meet quality standards
- When tests are missing or failing
- When documentation is incomplete

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- PR number being reviewed
- PR is in `review:in-progress` state
- Specific issues to address identified

## Procedure

### Step 1: Update Review Label

```bash
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:changes-requested"
```

### Step 2: Submit Review with Changes Requested

```bash
gh pr review $PR_NUMBER --request-changes --body "## Changes Requested

### Issues Found

1. **Issue 1**: Description of first issue
   - Location: \`path/to/file.py:42\`
   - Suggestion: How to fix

2. **Issue 2**: Description of second issue
   - Location: \`path/to/other.py:88\`
   - Suggestion: How to fix

### Before Re-review

Please address all issues above and:
- [ ] Update affected unit tests
- [ ] Verify CI passes
- [ ] Update documentation if needed"
```

### Step 3: Notify Author (via AI Maestro if agent)

Get the PR author:
```bash
AUTHOR=$(gh pr view $PR_NUMBER --json author --jq '.author.login')
```

If author is an agent, send a message using the `agent-messaging` skill with:
- **Recipient**: The PR author agent
- **Subject**: `Changes requested on PR #<PR_NUMBER>`
- **Priority**: `high`
- **Content**: `{"type": "review-feedback", "message": "Changes requested on your PR. Please review feedback and address issues.", "pr_number": <PR_NUMBER>}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Step 4: Verify Label Update

```bash
gh pr view $PR_NUMBER --json labels --jq '.labels[].name | select(startswith("review:"))'
# Expected: review:changes-requested
```

## Example

**Scenario:** Review of PR #45 found issues with error handling.

```bash
# Step 1: Update label
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:changes-requested"

# Step 2: Submit review
gh pr review 45 --request-changes --body "## Changes Requested

### Issues Found

1. **Missing error handling**: The API endpoint doesn't handle 404 cases
   - Location: \`src/api/users.py:42\`
   - Suggestion: Add try/except block with proper HTTP response

2. **No input validation**: User input is not validated before database query
   - Location: \`src/api/users.py:55\`
   - Suggestion: Add pydantic model for request validation

### Before Re-review

Please address all issues above and:
- [ ] Add unit tests for error cases
- [ ] Verify CI passes
- [ ] Update API documentation"

# Step 3: Verify
gh pr view 45 --json labels --jq '.labels[].name'
# Output includes: review:changes-requested
```

## Review Comment Templates

### Missing Tests

```markdown
## Changes Requested: Missing Test Coverage

The following changes lack test coverage:
- [ ] `function_name` in `file.py`
- [ ] Error handling paths

Please add unit tests before re-review.
```

### Code Quality Issues

```markdown
## Changes Requested: Code Quality

Issues found:
1. **Naming**: Variable `x` should have descriptive name
2. **Complexity**: Function exceeds cyclomatic complexity threshold
3. **Duplication**: Code duplicated from `other_file.py:23`

Please refactor and address above issues.
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Review already exists | Previous review not dismissed | Dismiss old review first |
| Label not found | Review label missing | Create with `gh label create` |
| Author unreachable | AI Maestro down | Leave detailed PR comment |

## Notes

- Be specific about what needs to change and why
- Provide suggestions, not just criticism
- Link to documentation or examples when helpful
- Changes requested blocks merge until resolved
