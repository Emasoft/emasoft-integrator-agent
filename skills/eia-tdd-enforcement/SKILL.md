---
name: eia-tdd-enforcement
description: Enforces Test-Driven Development (TDD) discipline through the RED-GREEN-REFACTOR cycle. Implements the Iron Law - no production code can be written without a failing test that justifies its existence. The orchestrator ENFORCES TDD discipline on remote agents but NEVER writes tests or code itself. Orchestrator verifies remote agents follow TDD, reviews PRs to ensure TDD was followed, and rejects work that violates TDD principles. All actual test writing and code implementation is performed by Remote Developer Agents via AI Maestro.
license: Apache-2.0
compatibility: Requires understanding of TDD principles, RED-GREEN-REFACTOR cycle, test frameworks, and version control. Works with any programming language that supports automated testing.
metadata:
  author: Anthropic
  version: 2.0.0
agent: test-engineer
context: fork
---

# TDD Enforcement Skill

## Overview

This skill enforces Test-Driven Development (TDD) discipline through the RED-GREEN-REFACTOR cycle. It implements the Iron Law: **no production code can be written without a failing test that justifies its existence**.

### The Orchestrator's Role

**The orchestrator ENFORCES TDD discipline on remote agents. The orchestrator NEVER writes tests or code itself.**

**Orchestrator Responsibilities:**
- **VERIFY** remote agents follow TDD (tests before code)
- **REVIEW** PRs to ensure TDD was followed
- **REJECT** work that violates TDD principles
- **DELEGATE** all test writing and code implementation to Remote Developer Agents via AI Maestro

### The TDD Cycle

TDD operates through three phases in strict order:

1. **RED**: Write a failing test that documents intended behavior
2. **GREEN**: Write minimum code to make the test pass
3. **REFACTOR**: Improve code quality while maintaining behavior

After completing one cycle, return to RED for the next feature.

### How to Use This Skill

This SKILL.md is a **map** to detailed reference documents. Each section below shows **when to read** each reference file. Click the links to access the full content.

---

## Core Principles

### The Iron Law ([references/iron-law.md](references/iron-law.md))

- When you need to understand the fundamental TDD principle → The Iron Law
- If you're unsure whether to write code → Pre-Code Checklist
- When evaluating if a change violates TDD → Violation Detection
- If you need to enforce TDD on remote agents → Enforcement Role

---

## The TDD Cycle

### RED-GREEN-REFACTOR Cycle ([references/red-green-refactor-cycle.md](references/red-green-refactor-cycle.md))

- When starting a new feature → Phase 1: RED
- If you have a failing test and need to implement → Phase 2: GREEN
- When all tests pass and code needs improvement → Phase 3: REFACTOR
- If you need to understand the complete cycle flow → Cycle Flow
- When completing one cycle and starting the next → Cycle Completion

### Status Tracking ([references/status-tracking.md](references/status-tracking.md))

- When you need to track TDD cycle progress → Status States
- If you need to document current phase → Status Tracking Format
- When managing multiple features → Multi-Feature Tracking
- If you need to verify phase transitions → Phase Transition Rules

---

## Implementation Guidance

### Step-by-Step Implementation ([references/implementation-procedure.md](references/implementation-procedure.md))

- When starting to implement a new feature → Step 1: Understand the Requirement
- If you need to write a failing test → Step 2: Write the Failing Test
- When you have a failing test and need to implement → Step 3: Make the Test Pass
- If tests pass and code needs improvement → Step 4: Refactor
- When you need test structure guidance → Test Structure Pattern

### Common Patterns ([references/common-patterns.md](references/common-patterns.md))

- When you need to understand what to test → Testing Behavior Not Implementation
- If your test has multiple assertions → One Assertion Per Test
- When structuring test code → Arrange-Act-Assert Pattern
- If you need to test edge cases → Edge Case Testing
- When dealing with dependencies → Dependency Isolation

---

## Rules and Enforcement

### Strict Rules ([references/rules-and-constraints.md](references/rules-and-constraints.md))

- When you need absolute rules that cannot be broken → The Iron Law (Absolute)
- If you're in RED phase and unsure what's allowed → Red Phase Rules
- If you're in GREEN phase and unsure what's allowed → Green Phase Rules
- If you're in REFACTOR phase and unsure what's allowed → Refactor Phase Rules
- When you need to know what actions are forbidden → Forbidden Actions

---

## Problem Solving

### Troubleshooting ([references/troubleshooting.md](references/troubleshooting.md))

- If tests fail during refactoring → Test Fails During Refactoring
- When you can't write a failing test → Cannot Write a Failing Test
- If code passes test but seems wrong → Code Passes But Seems Wrong
- When refactoring takes too long → Refactoring Takes Too Long
- If test passes but code seems incomplete → Test Passes But Code Incomplete
- When test passes immediately → Test Passes on First Run
- If you're not sure what to test next → Unsure What to Test Next
- When tests become slow → Tests Are Too Slow

---

## Quick Reference

### Essential Checklist

**Before Writing ANY Production Code:**
- [ ] A failing test exists for this specific behavior
- [ ] The test has been run and actually fails
- [ ] The failure message is clear and measurable
- [ ] The test is committed with "RED: ..." message
- [ ] Status is marked as `RED`

**TDD Cycle Summary:**
1. **RED**: Write failing test → Commit → Mark as RED
2. **GREEN**: Write minimum code → All tests pass → Commit → Mark as GREEN
3. **REFACTOR**: Improve code → Tests still pass → Commit → Mark as REFACTOR
4. **Repeat**: Return to RED for next feature

**Git Commit Pattern:**
```
RED: test for [feature]
GREEN: implement [feature]
REFACTOR: improve [aspect] in [feature]
```

**Status States:**
- `pending` → Test being written
- `RED` → Test fails, needs implementation
- `GREEN` → Test passes, implementation complete
- `refactor` → Code improved, ready for next cycle

---

## Progressive Learning Path

**New to TDD? Read in this order:**

1. Start with [The Iron Law](references/iron-law.md) - understand the fundamental principle
2. Read [RED-GREEN-REFACTOR Cycle](references/red-green-refactor-cycle.md) - understand the three phases
3. Study [Implementation Procedure](references/implementation-procedure.md) - learn step-by-step process
4. Review [Common Patterns](references/common-patterns.md) - learn good practices
5. Memorize [Rules and Constraints](references/rules-and-constraints.md) - know what's allowed
6. Bookmark [Troubleshooting](references/troubleshooting.md) - for when things go wrong
7. Use [Status Tracking](references/status-tracking.md) - track your progress

**Enforcing TDD on Remote Agents?**

1. Read [Enforcement Role](references/iron-law.md#enforcement-role) - understand orchestrator vs. agent responsibilities
2. Review [Phase Transition Rules](references/status-tracking.md#phase-transition-rules) - verify agent work
3. Use [Violation Recovery Procedure](references/rules-and-constraints.md#violation-recovery-procedure) - handle violations

---

## Summary

TDD Enforcement ensures quality through discipline:

- **Tests document behavior** - Every test is executable specification
- **Tests drive design** - Write test first, code second
- **Tests enable refactoring** - Change code confidently
- **Tests prevent regressions** - Old features keep working

**The Iron Law is absolute:** No code without a failing test.

**The orchestrator enforces**, remote agents execute.

Follow the cycle: **RED → GREEN → REFACTOR → Repeat**

---

## RULE 14: User Requirements Are Immutable

### TDD and Requirement Compliance

TDD enforcement MUST align with RULE 14:

1. **Tests Must Match Requirements**
   - Tests verify user-specified behavior
   - Tests use user-specified technologies
   - Tests validate requirement compliance

2. **Forbidden TDD Pivots**
   - ❌ "Requirement too complex, testing simpler version"
   - ❌ "Technology X hard to test, using Y instead"
   - ❌ "Skipping test for user-requested feature"

3. **Correct TDD Approach**
   - ✅ Test exactly what user specified
   - ✅ If feature hard to test, escalate (don't skip)
   - ✅ Tests trace to specific requirements

### Test-Requirement Traceability

Every test file SHOULD include:

```python
# Tests for REQ-003: "User specified exact output format"
def test_output_format_matches_requirement():
    # Verifies: REQ-003
    ...
```

### When Tests Reveal Requirement Issues

If writing tests reveals a requirement problem:
1. STOP test writing
2. Document the issue
3. Generate Requirement Issue Report
4. WAIT for user decision
5. Resume with user's chosen direction

### TDD Phase Requirement Checks

| TDD Phase | Requirement Check |
|-----------|-------------------|
| RED | Is this testing what user actually asked for? |
| GREEN | Does implementation match user's specification? |
| REFACTOR | Does refactoring preserve user's requirements? |
