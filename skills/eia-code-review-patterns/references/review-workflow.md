---
name: "Code Review Workflow"
description: "Step-by-step workflow for conducting effective code reviews from initial scan to final approval"
---

# Code Review Workflow

## Table of Contents

- [Overview](#overview)
- [Workflow Phases](#workflow-phases)
- [Phase 1: Initial Scan (5-10 minutes)](#phase-1-initial-scan-5-10-minutes)
  - [1.1 Check Basic Requirements](#11-check-basic-requirements)
  - [1.2 Quick Size Assessment](#12-quick-size-assessment)
  - [1.3 Scope Verification](#13-scope-verification)
  - [1.4 Automated Check Review](#14-automated-check-review)
- [Phase 2: Deep Review (20-60 minutes)](#phase-2-deep-review-20-60-minutes)
  - [2.1 First Pass: High-Level Review](#21-first-pass-high-level-review)
  - [2.2 Second Pass: Code Quality](#22-second-pass-code-quality)
  - [2.3 Third Pass: Security Review](#23-third-pass-security-review)
  - [2.4 Fourth Pass: Testing Review](#24-fourth-pass-testing-review)
- [Phase 3: Feedback Compilation (5-15 minutes)](#phase-3-feedback-compilation-5-15-minutes)
  - [3.1 Categorize Issues](#31-categorize-issues)
  - [3.2 Structure Feedback](#32-structure-feedback)
  - [3.3 Add Code Suggestions](#33-add-code-suggestions)
- [Phase 4: Decision & Communication (5 minutes)](#phase-4-decision--communication-5-minutes)
  - [4.1 Make Review Decision](#41-make-review-decision)
  - [4.2 Write Review Summary](#42-write-review-summary)
  - [4.3 Submit Review](#43-submit-review)
- [Phase 5: Follow-up (as needed)](#phase-5-follow-up-as-needed)
  - [5.1 Re-Review Process](#51-re-review-process)
  - [5.2 Communication During Follow-up](#52-communication-during-follow-up)
  - [5.3 Final Approval](#53-final-approval)
- [Workflow Best Practices](#workflow-best-practices)
  - [Time Management](#time-management)
  - [Context Switching](#context-switching)
  - [Communication](#communication)
  - [Continuous Improvement](#continuous-improvement)
- [Common Review Patterns](#common-review-patterns)
  - [Pattern: Feature Addition](#pattern-feature-addition)
  - [Pattern: Bug Fix](#pattern-bug-fix)
  - [Pattern: Refactoring](#pattern-refactoring)
  - [Pattern: Performance Optimization](#pattern-performance-optimization)
- [Escalation](#escalation)
- [Review Metrics (Optional)](#review-metrics-optional)

This document outlines a systematic workflow for conducting code reviews, from initial assessment to final decision.

## Overview

A code review should be:
- **Systematic**: Follow a consistent process
- **Thorough**: Cover all evaluation criteria
- **Timely**: Complete within 24-48 hours
- **Constructive**: Focus on improvement, not criticism

## Workflow Phases

```
1. Initial Scan (5-10 min)
   ↓
2. Deep Review (20-60 min)
   ↓
3. Feedback Compilation (5-15 min)
   ↓
4. Decision & Communication (5 min)
   ↓
5. Follow-up (as needed)
```

---

## Phase 1: Initial Scan (5-10 minutes)

**Goal**: Get an overview and identify immediate blockers.

### 1.1 Check Basic Requirements

```bash
# Verify branch/PR metadata
- [ ] PR title is clear and descriptive
- [ ] PR description explains what/why
- [ ] Issue/ticket reference is included
- [ ] Target branch is correct
- [ ] No merge conflicts
- [ ] CI/CD checks pass
```

### 1.2 Quick Size Assessment

**File count and lines changed:**
- Small: <200 lines → Single-pass review
- Medium: 200-500 lines → Structured review with breaks
- Large: >500 lines → Request split into smaller PRs

**Example decision:**
```
Files changed: 3
Lines: +127, -45
Size: SMALL → Proceed with full review
```

### 1.3 Scope Verification

Ask:
- Does this PR do ONE thing?
- Are unrelated changes included?
- Should this be split into multiple PRs?

**Red flags:**
- Mixing refactoring with new features
- Including "drive-by" fixes unrelated to the PR objective
- Changing more files than necessary

### 1.4 Automated Check Review

Review CI/CD results:
- [ ] Tests pass
- [ ] Linting passes
- [ ] Type checking passes (if applicable)
- [ ] Security scans pass
- [ ] Code coverage meets threshold

**If automated checks fail:** Request fixes before continuing manual review.

---

## Phase 2: Deep Review (20-60 minutes)

**Goal**: Thoroughly evaluate code quality, correctness, and design.

### 2.1 First Pass: High-Level Review

Focus on architecture and design:

**Questions to ask:**
1. Does the solution fit the problem?
2. Is the approach sound?
3. Are there better alternatives?
4. Does it integrate well with existing code?

**Check:**
- [ ] Design patterns are appropriate
- [ ] Architecture is clean
- [ ] Dependencies are justified
- [ ] No circular dependencies

**Example review note:**
```
File: src/payment/processor.py
Line 45-80

The direct database access here breaks our repository pattern.
Consider injecting PaymentRepository instead.

Reason: Maintains separation of concerns and improves testability.
```

### 2.2 Second Pass: Code Quality

Review each file for quality:

**For each changed file:**

1. **Readability**
   - [ ] Names are clear and descriptive
   - [ ] Functions are focused and short
   - [ ] Complex logic has comments
   - [ ] Code follows project style

2. **Correctness**
   - [ ] Logic implements requirements
   - [ ] Edge cases are handled
   - [ ] Error handling is present
   - [ ] Type safety is maintained

3. **Performance**
   - [ ] No obvious inefficiencies
   - [ ] Database queries are optimized
   - [ ] Resource management is proper

**Example review note:**
```
File: src/utils/validator.py
Line 23

This loop iterates over all users (potentially 10,000+).
Consider paginating or filtering at the database level.

Performance impact: O(n) memory usage could cause issues at scale.
```

### 2.3 Third Pass: Security Review

Security-focused scan:

**Check for:**
- [ ] Input validation on all user inputs
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization
- [ ] Sensitive data is encrypted
- [ ] Dependencies have no known vulnerabilities

**Example review note:**
```
File: src/api/user_handler.py
Line 67

🚨 SECURITY: User input is concatenated directly into SQL query.

Current:
query = f"SELECT * FROM users WHERE name = '{username}'"

Fix:
query = "SELECT * FROM users WHERE name = ?"
db.execute(query, (username,))

Vulnerability: SQL injection attack possible.
Priority: P0 - MUST FIX before merge.
```

### 2.4 Fourth Pass: Testing Review

Review test coverage and quality:

**Check:**
- [ ] New code has tests
- [ ] Tests cover edge cases
- [ ] Tests are deterministic
- [ ] Tests are maintainable
- [ ] Integration tests verify interactions

**Example review note:**
```
File: tests/test_payment.py

Missing test cases:
1. What happens when payment gateway times out?
2. How is duplicate payment handled?
3. Edge case: amount = 0?

Please add tests for these scenarios before merge.
```

---

## Phase 3: Feedback Compilation (5-15 minutes)

**Goal**: Organize findings into clear, actionable feedback.

### 3.1 Categorize Issues

Group findings by priority:

**P0 - Critical (Must Fix)**
- Security vulnerabilities
- Data corruption risks
- Breaking changes

**P1 - High (Should Fix)**
- Performance issues
- Incorrect logic
- Missing critical tests

**P2 - Medium (Nice to Have)**
- Style issues
- Minor refactoring
- Documentation improvements

**P3 - Low (Optional)**
- Nitpicks
- Personal preferences

### 3.2 Structure Feedback

**Template:**
```markdown
## Summary
[Overall assessment: what's good, what needs work]

## Critical Issues (P0) - Must Fix
1. [Issue with file:line reference]
   - Problem: [What's wrong]
   - Impact: [Why it matters]
   - Fix: [Suggested solution]

## High Priority (P1) - Should Fix
[Same structure]

## Medium Priority (P2) - Nice to Have
[Same structure]

## Positive Feedback
[What the author did well]

## Next Steps
[Clear action items]
```

### 3.3 Add Code Suggestions

Use inline code suggestions where possible:

**Example:**
```diff
- def process(data):
+ def process_user_data(user_data: UserData) -> ProcessedData:
+     """Process user data and return normalized result."""
      # ... implementation
```

---

## Phase 4: Decision & Communication (5 minutes)

**Goal**: Make a clear decision and communicate it effectively.

### 4.1 Make Review Decision

**Decision matrix:**

| Condition | Decision |
|-----------|----------|
| No P0/P1 issues | **Approve** |
| Only P2/P3 issues | **Approve with Comments** |
| P1 issues, but minor | **Approve with Comments** + request follow-up |
| P0 issues OR multiple P1 issues | **Request Changes** |

### 4.2 Write Review Summary

**Approval example:**
```
## ✅ Approved

Nice work! The implementation is clean and well-tested.

Minor suggestions (P2):
- Consider extracting the validation logic to a separate function
- Add docstring to public methods

These can be addressed in a follow-up PR if preferred.
```

**Request changes example:**
```
## 🔄 Changes Requested

Thanks for the PR! Before we can merge, please address:

**Must Fix (P0):**
1. SQL injection vulnerability in user_handler.py:67
2. Missing authorization check in delete_user()

**Should Fix (P1):**
1. Add tests for error scenarios
2. Fix performance issue in get_all_users()

Please update and request re-review when ready.
```

### 4.3 Submit Review

**Before submitting:**
- [ ] Re-read your feedback for tone
- [ ] Ensure all comments are constructive
- [ ] Verify code suggestions are correct
- [ ] Check that action items are clear

---

## Phase 5: Follow-up (as needed)

**Goal**: Ensure issues are resolved and PR is merged smoothly.

### 5.1 Re-Review Process

When author updates the PR:

1. **Check resolution of P0/P1 issues**
   - Verify each critical issue is addressed
   - Test suggested changes if needed

2. **Spot-check unchanged files**
   - Ensure no new issues introduced

3. **Review new commits**
   - Apply same review standards to updates

**Re-review decision:**
- All P0/P1 resolved → Approve
- New issues introduced → Request changes again
- Partial resolution → Comment with remaining items

### 5.2 Communication During Follow-up

**Respond to author questions promptly:**
```
Q: "Can we defer the performance optimization to a follow-up PR?"
A: "The query currently times out with 1000+ users. Let's fix the N+1
   problem now, but the caching optimization can be deferred."
```

**Acknowledge good fixes:**
```
Great fix on the SQL injection issue! The parameterized query looks good.
```

### 5.3 Final Approval

When all critical issues are resolved:

```
## ✅ Approved - Ready to Merge

All concerns addressed. Nice work on:
- Fixing the security vulnerabilities
- Adding comprehensive tests
- Improving error handling

Follow-up items for future PRs (P2):
- Refactor duplicate logic in handlers
- Add performance monitoring

Merging now.
```

---

## Workflow Best Practices

### Time Management

**Don't rush:**
- Small PR: 15-30 min
- Medium PR: 30-60 min
- Large PR: Request split

**Take breaks:**
- For PRs >500 lines, review in multiple sessions
- Fresh eyes catch more issues

### Context Switching

**Before starting:**
```bash
# Pull latest changes
git fetch origin
git checkout feature-branch

# Run tests locally
npm test  # or pytest, etc.

# Review diff locally (optional but recommended)
git diff main...feature-branch
```

**After review:**
- Clear mental context
- Update tracking board
- Set reminder for re-review (if needed)

### Communication

**Be specific:**
- ❌ "This is confusing"
- ✅ "The variable name `x` doesn't indicate it's a user ID. Consider `user_id`."

**Be constructive:**
- ❌ "This is wrong"
- ✅ "This approach works, but using X would improve performance because Y"

**Ask questions:**
- "Why did you choose approach X over Y?"
- "Have you considered Z?"
- "What happens if input is null?"

### Continuous Improvement

**After each review:**
- Note patterns of issues
- Update team guidelines
- Share learning with team
- Add to review checklist

---

## Common Review Patterns

### Pattern: Feature Addition

1. Verify requirements understanding
2. Check integration with existing features
3. Validate test coverage
4. Review error handling
5. Check backward compatibility

### Pattern: Bug Fix

1. Understand root cause
2. Verify fix addresses root cause (not symptom)
3. Check for similar issues elsewhere
4. Ensure regression tests added
5. Validate fix doesn't introduce new issues

### Pattern: Refactoring

1. Verify behavior unchanged
2. Check tests still pass
3. Validate improved maintainability
4. Ensure no new dependencies
5. Review performance impact

### Pattern: Performance Optimization

1. Verify profiling data supports optimization
2. Check trade-offs (readability vs speed)
3. Validate benchmarks
4. Ensure optimization is measurable
5. Review edge case performance

---

## Escalation

**When to escalate to senior reviewer:**

- Complex architectural decisions
- Security concerns beyond your expertise
- Disagreement with author on fundamental approach
- Performance optimization requiring domain expertise
- Breaking changes affecting multiple teams

**How to escalate:**
```
@senior-reviewer I'd like your input on the database schema changes
in migration_v2.py. The proposed denormalization improves read
performance but may impact write consistency. Could you review?
```

---

## Review Metrics (Optional)

**Track these for continuous improvement:**

- Average review time
- Issues found per review
- P0 issues that reached production
- Author satisfaction with feedback
- Time to re-review

**Use metrics to:**
- Identify training needs
- Improve review process
- Balance thoroughness with speed
