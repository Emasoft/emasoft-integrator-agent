---
name: op-quick-scan
description: Execute Stage 1 Quick Scan for surface-level PR assessment
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Quick Scan (Stage 1)

## Purpose

Perform a surface-level assessment of the PR to identify obvious issues and determine if a full deep dive review is warranted. This is a time-efficient first pass.

## When to Use

- After Gate 0 compliance check passes
- As the first stage of the two-stage review process
- When you need to quickly assess PR quality before investing in deep analysis

## Prerequisites

- Gate 0 compliance check completed
- PR context retrieved (metadata, files, diff)
- Access to repository for file inspection

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pr_number | integer | Yes | The PR number to scan |
| pr_context | object | Yes | Context from eia_get_pr_context.py |
| files_list | array | Yes | Files from eia_get_pr_files.py |

## Output

| Field | Type | Description |
|-------|------|-------------|
| initial_confidence | integer | Confidence score 0-100% |
| obvious_issues | array | List of immediately visible problems |
| red_flags | array | Critical issues requiring immediate attention |
| go_decision | boolean | Whether to proceed to Deep Dive |
| scope_category | string | small/medium/large based on file count |

## Steps

### Step 1: Assess File Structure

Categorize the PR by size:
- **Small**: 1-10 files changed
- **Medium**: 11-30 files changed
- **Large**: 30+ files changed

```bash
python3 eia_get_pr_files.py --pr <PR_NUMBER>
```

### Step 2: Review Diff Magnitude

```bash
python3 eia_get_pr_diff.py --pr <PR_NUMBER> --stat
```

Assess:
- Total lines added/deleted
- Ratio of additions to deletions
- Files with disproportionate changes

### Step 3: Obvious Issue Scan

Scan for immediately visible problems:
- [ ] Syntax errors visible in diff
- [ ] Debugging code left in (console.log, print statements)
- [ ] Commented-out code blocks
- [ ] TODO/FIXME comments without resolution
- [ ] Obvious security issues (hardcoded secrets, SQL strings)
- [ ] Missing imports or references

### Step 4: Immediate Red Flags Detection

Check for critical issues:
- [ ] Large binary files added
- [ ] Configuration files with secrets
- [ ] Test files deleted without replacement
- [ ] Breaking changes to public APIs
- [ ] License violations

### Step 5: Calculate Initial Confidence

Score based on:
- File structure clarity: 0-20 points
- Diff reasonableness: 0-20 points
- Absence of obvious issues: 0-30 points
- Absence of red flags: 0-30 points

**Total: 0-100%**

### Step 6: Make Go/No-Go Decision

| Score | Decision |
|-------|----------|
| >= 70% | GO - Proceed to Stage 2 Deep Dive |
| 60-69% | CONDITIONAL - Proceed with caution, flag concerns |
| < 60% | NO-GO - Request changes before continuing review |

## Quick Scan Output Template

```markdown
## Quick Scan Report: PR #<NUMBER>

**Date**: <TIMESTAMP>
**Reviewer**: <AGENT_NAME>

### File Structure Assessment
- Files changed: <COUNT>
- Scope category: <small/medium/large>

### Diff Magnitude
- Lines added: <COUNT>
- Lines deleted: <COUNT>
- Net change: <COUNT>

### Obvious Issues
<LIST_OR_NONE>

### Red Flags
<LIST_OR_NONE>

### Initial Confidence Score
**Score**: <PERCENTAGE>%

### Decision
**Go/No-Go**: <GO/NO-GO>
**Rationale**: <EXPLANATION>
```

## Example

```bash
# Get files and diff statistics
python3 eia_get_pr_files.py --pr 123
python3 eia_get_pr_diff.py --pr 123 --stat

# Generate quick scan report
python3 scripts/quick_scan_template.py --pr 123
```

## Error Handling

| Error | Action |
|-------|--------|
| Diff too large | Focus on file list, sample key files |
| Binary files present | Flag for manual inspection |
| API rate limit | Retry with exponential backoff |

## Related Operations

- [op-gate0-compliance-check.md](op-gate0-compliance-check.md) - Previous step
- [op-deep-dive-analysis.md](op-deep-dive-analysis.md) - Next step if GO decision
- [stage-one-quick-scan.md](stage-one-quick-scan.md) - Detailed reference
