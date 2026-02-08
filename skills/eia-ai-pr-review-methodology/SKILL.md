---
name: eia-ai-pr-review-methodology
description: "Use when performing deep evidence-based PR reviews. Trigger when reviewing complex PRs, investigating false-positive fixes, or validating system integration changes."
license: Apache-2.0
compatibility: Requires intermediate software development experience and familiarity with code review basics. Designed for reviewers performing deep, evidence-based pull request reviews using a 4-phase, 5-dimension evaluation framework. Requires access to the full codebase and ability to run verification commands.
triggers:
  - Perform a deep evidence-based PR review
  - Investigate whether a PR fix is a false positive
  - Validate system integration changes in a pull request
  - Review a complex PR with file path or environment changes
  - Check a bug fix PR for root cause verification
  - Assess a performance improvement PR with benchmark evidence
  - Review a dependency update PR for redundancy and security
  - Catch cargo cult programming or unverified assumptions in a PR
metadata:
  author: Emasoft
  version: 1.0.0
agent: eia-main
context: fork
workflow-instruction: "Step 21"
procedure: "proc-deep-pr-review"
user-invocable: false
---

# AI PR Review Methodology Skill

## Overview

This skill teaches a systematic, evidence-based approach to reviewing pull requests. It is organized into 4 sequential phases and 5 analysis dimensions. The methodology is designed to catch false positives (changes that appear to fix a problem but do not), redundant code, unverified assumptions, and cargo cult programming before they are merged into the main branch.

The 4 phases are:

1. **Context Gathering** -- Mandatory preparation before any analysis begins. Read complete files, search for duplicates, understand the problem, and verify claims.
2. **Structured Analysis** -- Apply 5 analysis dimensions systematically to evaluate the PR.
3. **Evidence Requirements** -- Determine what evidence is missing and must be provided by the author before the PR can be approved.
4. **Review Output** -- Synthesize findings into a structured, actionable review document.

The 5 analysis dimensions (applied in Phase 2) are:

1. **Problem Verification** -- Confirm the PR addresses the real root cause, not just symptoms.
2. **Redundancy Check** -- Ensure the change does not duplicate existing functionality.
3. **System Integration Validation** -- Verify paths, commands, and environment assumptions are correct on all target platforms.
4. **Senior Developer Review** -- Evaluate architecture, maintainability, performance, security, and backwards compatibility.
5. **False Positive Detection** -- Challenge assumptions, detect cargo cult programming, and apply the ultimate reversibility test.

### Key Principle

Every claim in a PR must be backed by evidence. "It works on my machine" is not evidence. "Here is the output of the verification command on three target platforms" is evidence.

---

## Prerequisites

Before using this skill, you should be familiar with:

- Basic pull request workflow (creating, reviewing, merging)
- Reading diffs and understanding file-level changes
- Running shell commands to verify paths, file existence, and tool availability
- The codebase under review (or have access to search and read it)

---

## Output

Applying this skill produces a structured review document containing:

- A summary of the PR and the reviewer's overall assessment
- A list of strengths identified in the PR
- Critical and non-critical questions for the author
- Blocking red flags (issues that must be resolved before merge)
- A checklist of required evidence the author must provide
- Non-blocking suggestions for improvement
- Testing feedback and recommendations
- A final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
- A confidence level: High, Medium, or Low

The template for this output is provided in [review-output-template.md](references/review-output-template.md).

---

## Instructions

Follow these steps in order. Do not skip phases.

### Step 1: Gather Context (Phase 1)

Read [phase-1-context-gathering.md](references/phase-1-context-gathering.md) and complete all 4 context gathering actions before proceeding.

**Table of Contents for phase-1-context-gathering.md:**
- 1.1 When to perform context gathering
- 1.2 Action 1: Read complete files, not just diffs
  - 1.2.1 How to read complete files during a PR review
  - 1.2.2 Example: Good vs bad context gathering
- 1.3 Action 2: Search for existing solutions and duplicates
  - 1.3.1 How to search for duplicates before analyzing a PR
  - 1.3.2 Example: Discovering an existing solution
- 1.4 Action 3: Understand the problem (root cause vs symptoms)
  - 1.4.1 How to distinguish root cause from symptoms
  - 1.4.2 Example: Symptom-level vs root-cause understanding
- 1.5 Action 4: Verify all claims made in the PR
  - 1.5.1 How to verify file path claims
  - 1.5.2 How to verify command availability claims
  - 1.5.3 Example: Verifying a claimed installation path
- 1.6 Completion checkpoint for Phase 1

### Step 2: Run Structured Analysis (Phase 2)

Read [phase-2-structured-analysis.md](references/phase-2-structured-analysis.md) for an overview of the 5 analysis dimensions, then read each dimension reference file in order.

**Table of Contents for phase-2-structured-analysis.md:**
- 2.1 When to use the structured analysis framework
- 2.2 Overview of the 5 analysis dimensions
- 2.3 How to apply the dimensions sequentially
- 2.4 How to flag items requiring author evidence
- 2.5 Cross-references to each dimension file

#### Step 2a: Dimension 1 -- Problem Verification

Read [dimension-1-problem-verification.md](references/dimension-1-problem-verification.md).

**Table of Contents for dimension-1-problem-verification.md:**
- D1.1 When to apply problem verification
- D1.2 Identifying the exact error message or unexpected behavior
- D1.3 Determining root cause vs treating symptoms
- D1.4 Verifying the fix addresses the root cause
- D1.5 Documenting assumptions about the system and environment
- D1.6 Testing methodology: before/after, multi-platform, edge cases, automated tests
- D1.7 Red flags that indicate problem verification failure
- D1.8 Example: A fix that treats symptoms vs one that addresses root cause

#### Step 2b: Dimension 2 -- Redundancy Check

Read [dimension-2-redundancy-check.md](references/dimension-2-redundancy-check.md).

**Table of Contents for dimension-2-redundancy-check.md:**
- D2.1 When to apply redundancy checking
- D2.2 Searching for similar patterns in the codebase
- D2.3 Identifying when existing code already handles the case
- D2.4 List and array addition analysis: priority order and placement justification
- D2.5 Configuration changes vs code changes
- D2.6 Red flags for redundancy
- D2.7 Example: Detecting a redundant path addition

#### Step 2c: Dimension 3 -- System Integration Validation

Read [dimension-3-system-integration.md](references/dimension-3-system-integration.md).

**Table of Contents for dimension-3-system-integration.md:**
- D3.1 When to apply system integration validation
- D3.2 File path verification on target systems (macOS, Linux, Windows)
- D3.3 Cross-referencing paths with official documentation
- D3.4 Path handling: home directory expansion, relative vs absolute, platform-specific
- D3.5 Installation location accuracy across package managers
- D3.6 Red flags for integration failures
- D3.7 Example: Validating a claimed binary installation path

#### Step 2d: Dimension 4 -- Senior Developer Review

Read [dimension-4-senior-review.md](references/dimension-4-senior-review.md).

**Table of Contents for dimension-4-senior-review.md:**
- D4.1 When to apply senior developer review criteria
- D4.2 Architectural layer assessment
- D4.3 Technical debt and maintainability evaluation
- D4.4 Performance and resource implications
- D4.5 Security implications analysis
- D4.6 Backwards compatibility assessment
- D4.7 Red flags for architectural concerns
- D4.8 Example: Evaluating a quick fix for long-term impact

#### Step 2e: Dimension 5 -- False Positive Detection

Read [dimension-5-false-positive-detection.md](references/dimension-5-false-positive-detection.md). This is the most critical dimension.

**Table of Contents for dimension-5-false-positive-detection.md:**
- D5.1 When to apply false positive detection
- D5.2 Assumption identification and verification
- D5.3 Alternative explanation analysis
- D5.4 Placebo effect check methodology
- D5.5 Cargo cult programming detection
- D5.6 Confirmation bias detection
- D5.7 The ultimate test: reversibility verification
- D5.8 Red flags for false positives
- D5.9 Example: A false-positive bug fix with before/after analysis

### Step 3: Determine Evidence Requirements (Phase 3)

Based on your analysis in Step 2, compile a list of evidence the author must provide. Use the evidence categories described in Phase 1 and the dimension-specific red flags. Every flagged item from Step 2 that lacks evidence becomes a required evidence item.

The minimum required evidence categories are:

1. **Problem Demonstration** -- Error message, stack trace, or screenshot; reproduction steps; root cause explanation.
2. **Solution Validation** -- Demonstration that the fix resolves the issue; test coverage; before/after comparison.
3. **Assumption Verification** -- For file paths: output of `ls` or equivalent. For commands: output showing availability. For system behavior: documentation links or code proof.
4. **Cross-Platform Testing** -- Results on all supported platforms; platform-specific edge cases handled.

### Step 4: Apply Scenario-Specific Protocols (if applicable)

If the PR matches one of these scenarios, read the corresponding reference file for scenario-specific review protocol:

**Path/File Changes:** Read [scenario-path-changes.md](references/scenario-path-changes.md).

**Table of Contents for scenario-path-changes.md:**
- S-PATH.1 When to use this scenario protocol
- S-PATH.2 Mandatory verification steps for path changes
- S-PATH.3 Verification commands to request from the author
- S-PATH.4 Evidence requirements specific to path changes
- S-PATH.5 Example: Reviewing a PR that adds a new binary search path

**Bug Fixes:** Read [scenario-bug-fixes.md](references/scenario-bug-fixes.md).

**Table of Contents for scenario-bug-fixes.md:**
- S-BUG.1 When to use this scenario protocol
- S-BUG.2 Original error identification
- S-BUG.3 Root cause identification requirements
- S-BUG.4 Reproduction before the fix
- S-BUG.5 Fix demonstration
- S-BUG.6 Regression test requirement
- S-BUG.7 Example: Reviewing a bug fix PR end-to-end

**Performance Improvements:** Read [scenario-performance.md](references/scenario-performance.md).

**Table of Contents for scenario-performance.md:**
- S-PERF.1 When to use this scenario protocol
- S-PERF.2 Benchmark requirements (before and after)
- S-PERF.3 Multiple test runs and statistical significance
- S-PERF.4 Verifying no functionality regressions
- S-PERF.5 Significance justification (complexity vs improvement tradeoff)
- S-PERF.6 Example: Reviewing a caching optimization PR

**Dependency Updates:** Read [scenario-dependency-updates.md](references/scenario-dependency-updates.md).

**Table of Contents for scenario-dependency-updates.md:**
- S-DEP.1 When to use this scenario protocol
- S-DEP.2 Justification requirements for new or updated dependencies
- S-DEP.3 Security vulnerability scanning
- S-DEP.4 License compatibility checking
- S-DEP.5 Bundle size and performance impact assessment
- S-DEP.6 Checking for alternatives using existing dependencies
- S-DEP.7 Example: Reviewing a PR that adds a new npm package

### Step 5: Generate the Review Output (Phase 4)

Read [review-output-template.md](references/review-output-template.md) and use the template to produce your final review document.

**Table of Contents for review-output-template.md:**
- T.1 When to generate the review output
- T.2 The complete review output template (copy-paste ready)
- T.3 How to fill each section of the template
- T.4 Choosing the final recommendation: APPROVE, REQUEST CHANGES, or COMMENT
- T.5 Setting the confidence level: High, Medium, or Low
- T.6 Writing the author note
- T.7 Example: A completed review output

### Step 6: Final Checklist

Before submitting your review, run through the quick reference checklist. Read [quick-reference-checklist.md](references/quick-reference-checklist.md).

**Table of Contents for quick-reference-checklist.md:**
- C.1 When to use this checklist
- C.2 The 12-item pre-approval checklist
- C.3 How to handle checklist failures
- C.4 Example: Walking through the checklist for a sample PR

---

## Checklist Summary

Use this abbreviated checklist as a quick sanity check. The full checklist with explanations is in [quick-reference-checklist.md](references/quick-reference-checklist.md).

1. Read complete files, not just the diff
2. Understood the actual problem and its root cause
3. Verified no duplicate or existing solution covers this case
4. Validated all referenced paths and commands exist on target systems
5. Checked cross-platform compatibility
6. Confirmed testing is adequate (before/after, edge cases, automated tests)
7. Reviewed for security implications
8. Assessed maintainability and long-term impact
9. Challenged assumptions with evidence
10. Applied the reversibility test ("remove the change -- does the problem return?")
11. Requested any missing evidence from the author
12. Provided constructive, specific, actionable feedback

---

## Troubleshooting

### The PR has too many file changes to review thoroughly

Break the review into logical groups of related files. Apply Phase 1 (context gathering) to each group separately. Focus the 5 dimensions on the files most likely to contain issues: files with path changes, configuration changes, or security-sensitive code. See [phase-1-context-gathering.md](references/phase-1-context-gathering.md) section 1.2 for guidance on prioritizing which files to read in full.

### The author cannot reproduce the reported bug

This is a red flag for false positive detection. See [dimension-5-false-positive-detection.md](references/dimension-5-false-positive-detection.md) section D5.4 (placebo effect check) and D5.7 (the ultimate reversibility test). If the bug cannot be reproduced, the fix cannot be validated. Request reproduction steps and evidence before proceeding.

### The PR modifies paths but the reviewer has no access to the target system

Request the author to provide terminal output (`ls -la`, `which`, `type`, or equivalent commands) showing the paths exist on each supported platform. See [scenario-path-changes.md](references/scenario-path-changes.md) section S-PATH.3 for the specific verification commands to request.

### The reviewer is unsure whether a change is redundant

See [dimension-2-redundancy-check.md](references/dimension-2-redundancy-check.md) section D2.2 for search strategies to find existing code that might already handle the case. If you find a potential duplicate, ask the author to explain why the existing solution is insufficient.

### The author becomes defensive when asked for evidence

Reiterate that evidence requirements are standard practice, not personal criticism. Frame questions as "help me understand" rather than "prove you are right." See [review-output-template.md](references/review-output-template.md) section T.6 for guidance on writing constructive author notes.

### The PR is a dependency update with no visible code changes

Even if the code diff is small, dependency updates require their own review protocol. See [scenario-dependency-updates.md](references/scenario-dependency-updates.md) for the full checklist including security scanning, license checking, and bundle size assessment.
