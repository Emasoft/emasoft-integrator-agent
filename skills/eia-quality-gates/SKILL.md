---
name: eia-quality-gates
description: "Quality gate enforcement for PR integration. Use when verifying code through pre-review, review, pre-merge, or post-merge checkpoints. Trigger with /eia-enforce-gates."
version: 1.0.0
license: Apache-2.0
compatibility: Requires familiarity with CI/CD pipelines, code review processes, and GitHub workflows. Designed for the Integrator Agent role enforcing quality standards. Requires AI Maestro installed.
triggers:
  - Enforce quality gates on a PR
  - Check if code passes pre-review gate
  - Validate PR before merge
  - Run post-merge verification
  - Determine if gate failure should block or warn
  - Escalate a blocked PR
  - Apply quality gate labels
metadata:
  author: Emasoft
  version: 1.0.0
agent: eia-main
context: fork
---

# EIA Quality Gates

## Overview

Quality gates are **mandatory checkpoints** that code must pass before advancing through the integration pipeline. Each gate defines specific criteria, blocking conditions, and escalation paths.

## Prerequisites

Before using this skill, ensure:
- Repository has CI/CD pipeline configured
- GitHub labels from **eia-label-taxonomy** are applied
- Review checklist from **eia-code-review-patterns** is available
- GitHub CLI (`gh`) is installed and authenticated
- Access to repository permissions for label management
- Understanding of the four-gate pipeline model

## Instructions

1. Identify the current gate by checking PR labels (no gate label = Pre-Review Gate)
2. Execute gate-specific checks (Pre-Review: tests/lints, Review: 8-dimension review, Pre-Merge: CI/conflicts, Post-Merge: main branch health)
3. Apply gate decision label (passed/failed/warning) based on check results
4. If checks pass, advance PR to next gate
5. If checks fail, apply "failed" label and follow escalation path (A, B, C, or D)
6. Document failure reasons in PR comments
7. Notify responsible parties per escalation order

**Step 5: Process Overrides (if applicable)**
- Verify override authority per Override Authority Matrix
- Document override justification in PR
- Apply `gate:override-applied` label
- Proceed with next gate

### Workflow Checklist

Copy this checklist and track your progress:

- [ ] Identify current gate by checking PR labels
- [ ] Execute gate-specific checks for current gate
- [ ] Evaluate check results against gate criteria
- [ ] Apply appropriate gate decision label (passed/failed/warning)
- [ ] If PASSED: advance PR to next gate
- [ ] If FAILED: apply failure label and identify escalation path
- [ ] Document failure reasons in PR comments
- [ ] Notify responsible parties per escalation order
- [ ] If override requested: verify authority per Override Authority Matrix
- [ ] If override approved: document justification and apply override label
- [ ] Update gate status in PR labels
- [ ] Verify next steps are clear to all parties

## Output

When executing quality gates, provide:
- **Gate Status**: Current gate name and pass/fail decision
- **Check Results**: List of all checks performed with outcomes
- **Labels Applied**: All labels added or removed
- **Escalation Actions**: Any notifications sent or escalations triggered
- **Next Steps**: What should happen next in the pipeline

**Example Output Format**:
```
Gate: Pre-Review Gate
Status: FAILED
Checks:
  - Tests: FAILED (3 failing tests in auth module)
  - Linting: PASSED
  - Build: PASSED
  - Description: PASSED

Labels Applied:
  - gate:pre-review-failed
  - gate:flaky-test

Escalation:
  - Commented on PR with test failure details
  - Notified @author

Next Steps:
  - Author must fix failing tests
  - Re-run pre-review gate after fixes
```

## Error Handling

**Common Errors and Solutions**:

1. **CI Pipeline Not Running**
   - Check GitHub Actions are enabled
   - Verify workflow files exist in `.github/workflows/`
   - Ensure branch protection rules allow CI execution

2. **Labels Not Applying**
   - Verify GitHub token has label permissions
   - Check label exists in repository (create from taxonomy if missing)
   - Use `gh pr edit $PR_NUMBER --add-label "label-name"` manually if automation fails

3. **Escalation Notification Failure**
   - Verify notification channels (email, Slack, etc.) are configured
   - Check user handles are correct (@mentions)
   - Fallback to manual notification if automation fails

4. **Gate Stuck in Pending State**
   - Check all required status checks are reporting
   - Verify no infrastructure outages
   - Manually re-trigger CI if needed
   - Document stuck state and escalate to EOA

5. **Override Authority Unavailable**
   - Follow alternate escalation path
   - Document urgency in PR
   - NEVER bypass security gates
   - Escalate to project maintainer if critical

## Examples

See [references/gate-examples.md](references/gate-examples.md) for complete examples including:
- Pre-Review Gate success and failure scenarios
- Review Gate failure with low confidence score
- Pre-Merge Gate failure with merge conflicts
- Post-Merge Gate failure with main branch broken
- Gate override application procedures

**Purpose of Quality Gates:**
- Prevent defective code from reaching production
- Ensure consistent quality standards across all contributions
- Provide clear, objective criteria for advancement
- Enable systematic escalation when gates fail

**Key Principle:** Quality gates use **state-based triggers**, not time-based values. Gates advance or block based on conditions being met, not elapsed time.

---

## Gate Types and Pipeline Position

The integration pipeline has four sequential gates. See [references/gate-pipeline.md](references/gate-pipeline.md) for the complete flow diagram.

## Gate 1: Pre-Review Gate

See [references/pre-review-gate.md](references/pre-review-gate.md) for:
- Required checks
- Warning conditions
- Gate pass criteria
- Label integration commands

## Gate 2: Review Gate

See [references/review-gate.md](references/review-gate.md) for:
- Required checks (8 dimensions, 80% confidence)
- Blocking conditions
- Warning conditions
- Gate pass/fail procedures

## Gate 3: Pre-Merge Gate

See [references/pre-merge-gate.md](references/pre-merge-gate.md) for:
- Required checks (CI, conflicts, approval validity)
- Blocking and warning conditions
- Label integration commands

## Gate 4: Post-Merge Gate

See [references/post-merge-gate.md](references/post-merge-gate.md) for:
- Required checks (main branch health)
- Blocking conditions
- Issue closure procedures

---

## Escalation Paths

See [references/escalation-paths.md](references/escalation-paths.md) for complete escalation procedures including:
- Escalation Path A: Pre-Review Gate Failure
- Escalation Path B: Review Gate Failure (with Override Authority matrix)
- Escalation Path C: Pre-Merge Gate Failure
- Escalation Path D: Post-Merge Gate Failure (with Revert Authority matrix)
- Actions by failure type for each path

---

## Gate Override Policies

See [references/override-policies.md](references/override-policies.md) for:
- Override Authority Matrix (who can override which gates)
- Override procedure and documentation requirements
- When overrides are allowed vs forbidden (e.g., security gates cannot be overridden)

---

## Complete Label Reference

See [references/label-reference.md](references/label-reference.md) for complete list of:
- Gate status labels (passed/failed/pending for each gate)
- Warning labels (coverage, changelog, large PR, style issues, performance, flaky tests, etc.)
- When each label should be applied

---

## Gate Enforcement Checklist

See [references/gate-checklist.md](references/gate-checklist.md) for a copy-paste checklist covering:
- Pre-Review Gate verification steps
- Review Gate verification steps
- Pre-Merge Gate verification steps
- Post-Merge Gate verification steps

---

## Integration with Other Skills

### Related Skills

- **eia-label-taxonomy** - Complete label definitions
- **eia-code-review-patterns** - Review methodology for Review Gate
- **eia-github-pr-workflow** - PR workflow including gates
- **eia-tdd-enforcement** - TDD requirements for Pre-Review Gate
- **eia-ci-failure-patterns** - CI failure analysis

### Dependency on Label Taxonomy

This skill uses labels defined in **eia-label-taxonomy**. Ensure the label taxonomy is applied to the repository before using quality gates.

---

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to common issues:
- Gate appears stuck
- False positive gate failure
- Escalation not triggering
- Override needed but no authority available

---

## Design Document Scripts

These scripts manage design documents for quality gate integration:

| Script | Purpose | Usage |
|--------|---------|-------|
| `eia_design_create.py` | Create new design documents with proper GUUID | `python scripts/eia_design_create.py --type <TYPE> --title "<TITLE>"` |
| `eia_design_search.py` | Search design documents by UUID, type, or status | `python scripts/eia_design_search.py --type <TYPE> --status <STATUS>` |
| `eia_design_validate.py` | Validate design document frontmatter compliance | `python scripts/eia_design_validate.py --all` |

### PR Gate Scripts

These scripts enforce quality gates on pull requests:

| Script | Purpose | Usage |
|--------|---------|-------|
| `eia_github_pr_gate.py` | Run pre-merge quality checks on PRs | `python scripts/eia_github_pr_gate.py --pr <NUMBER>` |
| `eia_github_pr_gate_checks.py` | Individual check implementations for PR gates | (Internal, called by eia_github_pr_gate.py) |
| `eia_github_report.py` | Generate comprehensive GitHub project reports | `python scripts/eia_github_report.py --owner <OWNER> --repo <REPO> --project <NUM>` |
| `eia_github_report_formatters.py` | Format reports in markdown/JSON | (Internal, used by eia_github_report.py) |

### Script Locations

All scripts are located at `../../scripts/` relative to this skill.

---

## Resources

### Gate Details
- [references/gate-pipeline.md](references/gate-pipeline.md) - Complete pipeline flow diagram
- [references/pre-review-gate.md](references/pre-review-gate.md) - Pre-Review Gate details
- [references/review-gate.md](references/review-gate.md) - Review Gate details
- [references/pre-merge-gate.md](references/pre-merge-gate.md) - Pre-Merge Gate details
- [references/post-merge-gate.md](references/post-merge-gate.md) - Post-Merge Gate details

### Procedures and Examples
- [references/gate-examples.md](references/gate-examples.md) - Practical examples for all gates
- [references/gate-checklist.md](references/gate-checklist.md) - Copy-paste enforcement checklist
- [references/escalation-paths.md](references/escalation-paths.md) - Escalation paths A, B, C, D
- [references/escalation-procedures.md](references/escalation-procedures.md) - Detailed escalation procedures
- [references/override-policies.md](references/override-policies.md) - Override authority and procedures
- [references/override-examples.md](references/override-examples.md) - Override documentation examples

### Reference Materials
- [references/gate-decision-flowchart.md](references/gate-decision-flowchart.md) - Visual decision flowchart
- [references/label-reference.md](references/label-reference.md) - Complete label list
- [references/troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14 canonical text and enforcement procedures
- [references/pr-evaluation.md](references/pr-evaluation.md) - PR evaluation procedures from eia-pr-evaluator
- [references/integration-verification.md](references/integration-verification.md) - Integration verification from eia-integration-verifier

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Skill Type**: Integration Process
**Required Knowledge**: CI/CD, code review, GitHub workflows
