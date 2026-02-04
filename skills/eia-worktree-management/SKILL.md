---
name: eia-worktree-management
description: Use when managing Git worktrees for parallel development with registry tracking and port allocation. Trigger with /manage-worktrees.
license: Apache-2.0
compatibility: >-
  Cross-platform support for Windows, macOS, and Linux. Requires Git 2.17+ with worktree support.
  Python 3.8+ for script automation. File locking and atomic writes for safe concurrent access. Requires AI Maestro installed.
metadata:
  author: Anthropic
  version: 1.0.0
context: fork
---

# Worktree Management for Integrator Agent

## Overview

This skill teaches how to manage Git worktrees within the Integrator Agent system. A worktree is an isolated Git working directory that allows you to work on multiple branches simultaneously without switching branches or creating separate clones.

**Key Features:**
- **Worktree Registry**: Centralized tracking at `~/design/worktree-registry.json`
- **Port Allocation**: Managed port range 8100-8199 for services running in worktrees
- **Parallel Development**: Work on multiple features, fixes, or experiments in parallel

## Prerequisites

- Git 2.17+ with worktree support
- Python 3.8+ for automation scripts
- Write access to `~/design/` for registry storage
- Cross-platform: Works on Windows, macOS, and Linux

## Instructions

1. Verify Git 2.17+ is installed with worktree support
2. Ensure Python 3.8+ is available for automation scripts
3. Confirm write access to `~/design/` for registry storage
4. Use automation scripts or git commands to create worktrees
5. Always register worktrees in the registry for tracking and port allocation
6. Allocate ports from the managed range (8100-8199) when running services
7. Follow worktree naming conventions for consistency
8. Validate registry regularly to detect orphaned entries
9. Remove worktrees safely when no longer needed

For cross-platform details, see [Cross-Platform Support](./references/cross-platform-support.md):
- Overview - When you need to understand cross-platform compatibility
- Platform Detection - If you need to know how platforms are detected
- Shared Utilities - When you need to use cross-platform functions
- Windows-Specific Notes - If you're developing on Windows

## Core Concepts

For foundational understanding, see [Worktree Fundamentals](./references/worktree-fundamentals.md):
- What Are Git Worktrees - When you need to understand the concept
- Why Use Worktrees - If you're deciding whether to use worktrees
- Core Concepts - When you need to understand how worktrees work internally
- Limitations - When you need to know worktree constraints

**Threshold Configuration**: Worktree lifecycle uses thresholds from `../shared/thresholds.py`:
- `MAX_ACTIVE_WORKTREES: 10` - Maximum worktrees per developer

## Operations Checklist

Copy this checklist and track your progress:

- [ ] Create a new worktree
- [ ] List all existing worktrees
- [ ] Check worktree status
- [ ] Allocate a port to a worktree
- [ ] Access a worktree by name
- [ ] Remove a worktree safely
- [ ] View registry contents
- [ ] Verify registry integrity
- [ ] Export worktree information
- [ ] Troubleshoot worktree issues

## Quick Start Workflows

For step-by-step workflows, see [Quick Start Workflows](./references/quick-start-workflows.md):
- Workflow 1: Create Feature Worktree - When you need to start a new feature
- Workflow 2: Parallel Bug Fix - If you need to fix a bug while working on another task
- Workflow 3: Review and Cleanup - When you need to validate and clean up worktrees
- Workflow 4: Testing Isolation - If you need isolated test environments
- Workflow 5: Code Review Setup - When reviewing pull requests
- Workflow 6: Hotfix Emergency - If you need to deploy an urgent fix

## Step-by-Step Procedures

For detailed procedures, see [Step-by-Step Procedures](./references/step-by-step-procedures.md):
- Phase 1: Understanding Prerequisites - Before creating worktrees
- Phase 2: Create a Worktree - Creating new worktrees
- Phase 3: Manage Multiple Worktrees - Working with multiple worktrees
- Phase 4: Service Port Management - Allocating and managing ports
- Phase 5: Remove Worktrees - Safe worktree removal
- Phase 6: Maintain Registry - Registry maintenance procedures

## Reference Documents

### 1. Worktree Fundamentals ([references/worktree-fundamentals.md](references/worktree-fundamentals.md))
- When you need to understand what git worktrees are → What Are Git Worktrees
- If you're deciding whether to use worktrees → Why Use Worktrees
- If you're comparing worktrees to branch switching → Worktree vs Branch
- When you need to understand how worktrees work internally → Core Concepts
- If you're deciding when to create a worktree → When to Use Worktrees
- When you need to know worktree constraints → Limitations
- If you need quick command reference → Basic Commands

### 2. Registry System ([references/registry-system.md](references/registry-system.md))
- When you need to understand the registry system → Overview
- If you need to find the registry file → Registry Location
- When you need to understand registry structure → Registry Schema
- When you need to modify the registry → Registry Operations
- When you need to enforce registry rules → Validation Rules
- When you need to clean stale entries → Automatic Cleanup
- If you encounter registry problems → Troubleshooting

### 3. Creating Worktrees ([references/creating-worktrees.md](references/creating-worktrees.md))
- When you need to create a new worktree → Standard Creation Flow
- If you're creating worktrees for specific purposes → Purpose-Specific Creation Patterns
- When you need to allocate ports for services → Port Allocation Strategy
- If you need to configure the worktree environment → Environment Setup
- When you need worktree command syntax → Commands Reference
- If you need to verify worktree creation → Post-Creation Checklist
- When you encounter worktree creation errors → Error Handling and Troubleshooting

### 4. Port Allocation ([references/port-allocation.md](references/port-allocation.md))
- When you need to understand why ports matter → Why Port Allocation is Needed
- If you need to understand port organization → Understanding Port Ranges
- When you need to know how ports are assigned → Port Allocation Algorithm
- If you need to generate worktree configurations → Configuration Templates
- When you need to check port status → Port Status Commands
- If you encounter port conflicts → Conflict Resolution
- When you need to use Docker with worktrees → Integration with Docker
- If you need to release or reset ports → Port Cleanup

### 5. Worktree Operations ([references/worktree-operations.md](references/worktree-operations.md))
- When you need to see all active worktrees → Listing Worktrees
- If you need to work in a different worktree → Switching Between Worktrees
- When you need to get latest changes → Updating Worktrees
- If you need to protect a worktree from deletion → Locking and Unlocking Worktrees
- When you need to relocate a worktree → Moving Worktrees
- If you need to check worktree state → Checking Worktree Status
- When you need to incorporate main branch changes → Syncing with Main Branch

### 6. Removing Worktrees ([references/removing-worktrees.md](references/removing-worktrees.md))
- When you need to understand worktree removal → Overview
- Before removing any worktree → Pre-Removal Checklist
- When you need to delete a worktree → Removal Commands
- After removing a worktree → Post-Removal Steps
- If you want to automate worktree cleanup → Cleanup Script
- When worktree removal fails → Handling Failures
- If you need to remove multiple worktrees → Bulk Removal

### 7. Port Management ([references/port-management.md](references/port-management.md))
- When you need to understand port management → Overview
- If you need to understand the registry format → Port Registry Structure
- When you need to allocate ports programmatically → Port Allocation Functions
- If you need to use port management commands → Command-Line Interface
- When you encounter port conflicts → Conflict Detection
- If you need to verify services are running → Health Checking
- When you need dynamic Docker port mapping → Docker Compose Integration

### 8. Troubleshooting ([references/troubleshooting.md](references/troubleshooting.md))
- If branch is already checked out in another worktree → Branch Already Checked Out
- When worktree is locked and can't be removed → Cannot Remove Locked Worktree
- If worktree directory was deleted manually → Missing Worktree
- When registry doesn't match filesystem → Registry Out of Sync
- If services fail to start due to ports → Port Conflicts
- When worktree has uncommitted changes → Dirty Worktree
- If submodules are missing or broken → Submodule Issues
- When you get permission denied errors → Permission Errors
- If git shows deleted worktrees → Stale Worktree References

### 9. Scripts and Automation ([references/scripts-guide.md](references/scripts-guide.md))
- When you need to understand automation scripts → Overview
- Before using any scripts → Prerequisites
- When you need script usage details → Script Reference
- When you need step-by-step procedures → Common Workflows
- If you encounter script problems → Troubleshooting

### 10. Worktree Naming Conventions ([references/worktree-naming-conventions.md](references/worktree-naming-conventions.md))
- When you need to understand naming rules → General Principles
- If you need purpose-specific patterns → Naming Patterns by Purpose
- If you need to understand ID vs path → Registry ID vs Path
- When converting branch names to paths → Branch Name Mapping
- If you need to validate names → Validation Rules
- When you need practical examples → Examples by Scenario

### 11. Review Worktree Isolation ([references/review-worktree-isolation.md](references/review-worktree-isolation.md))
- When you need to understand worktree isolation for reviews → Purpose
- If you need the fundamental isolation rule → Core Rule
- When you need to set up a review worktree → Worktree Setup for Review
- If you need to understand why isolation is important → Why Isolation Matters
- When you need to name review worktrees → Worktree Naming Convention

### 12. Testing Worktree Isolation ([references/testing-worktree-isolation.md](references/testing-worktree-isolation.md))
- When you need to understand testing in isolated worktrees → Overview
- If you need to understand worktree types for testing → Types of Testing Worktrees
- When you need to create test worktrees → Creating Test Worktrees
- If you need to set up test environment → Test Environment Setup
- When you need to run tests → Running Tests in Isolation
- If you need database testing patterns → Database Testing Patterns

### 13. Docker Worktree Testing ([references/docker-worktree-testing.md](references/docker-worktree-testing.md))
- When you need to understand Docker with worktrees → Overview
- If you need one container set per worktree → Container-Per-Worktree Pattern
- When you need Docker Compose configuration → Docker Compose Per Worktree
- If you need dynamic ports → Dynamic Port Configuration
- When you need a complete example → Workflow Example

### 14. Merge Safeguards ([references/merge-safeguards.md](references/merge-safeguards.md))
- When you need to understand merge safeguards → Overview
- If you need fundamental merge concepts → Core Concepts
- When you need to perform merge workflows → Usage Workflows
- Before merging any worktree → Pre-Merge Validation Checklist
- If you need advanced merge techniques → Advanced Scenarios
- When automating merge operations → Automation Scripts

### 15. Cross-Platform Support ([references/cross-platform-support.md](references/cross-platform-support.md))
- When you need to understand cross-platform compatibility → Overview
- If you need to know how platforms are detected → Platform Detection
- When you need to use cross-platform functions → Shared Utilities
- If you're developing on Windows → Windows-Specific Notes
- If you're developing on Unix-based systems → macOS/Linux Notes

### 16. Quick Start Workflows ([references/quick-start-workflows.md](references/quick-start-workflows.md))
- When you need to start a new feature → Workflow 1: Create Feature Worktree
- If you need to fix a bug while working on another task → Workflow 2: Parallel Bug Fix
- When you need to validate and clean up worktrees → Workflow 3: Review and Cleanup
- If you need isolated test environments → Workflow 4: Testing Isolation
- When reviewing pull requests → Workflow 5: Code Review Setup
- If you need to deploy an urgent fix → Workflow 6: Hotfix Emergency

### 17. Step-by-Step Procedures ([references/step-by-step-procedures.md](references/step-by-step-procedures.md))
- Before creating worktrees → Phase 1: Understanding Prerequisites
- When creating new worktrees → Phase 2: Create a Worktree
- If working with multiple worktrees → Phase 3: Manage Multiple Worktrees
- When allocating and managing ports → Phase 4: Service Port Management
- If removing worktrees safely → Phase 5: Remove Worktrees
- When maintaining the registry → Phase 6: Maintain Registry

### 18. Quick Reference ([references/quick-reference.md](references/quick-reference.md))
- When you need core worktree commands → Essential Git Commands
- If you need registry access and validation → Registry Commands
- When you need port allocation and status → Port Management Commands
- If you need all available scripts → Script Quick Reference
- When you need frequently used command sequences → Common Patterns

## Automation Scripts

See [Scripts and Automation](references/scripts-guide.md) for detailed usage.

| Script | Purpose |
|--------|---------|
| `worktree_create.py` | Create new worktree with registry entry |
| `worktree_list.py` | List all worktrees with details |
| `worktree_remove.py` | Remove worktree with cleanup |
| `registry_validate.py` | Validate registry integrity |
| `port_allocate.py` | Allocate ports to worktrees |
| `port_status.py` | Display port usage report |
| `merge_safeguard.py` | Merge conflict detection and prevention |

## Related Skills

This skill integrates with other Integrator Agent skills:

- **eia-github-projects-sync** - Link worktrees to GitHub issues, synchronize development status with project boards
- **eia-verification-patterns** - Apply verification patterns to worktree isolation tests

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Worktree Registry | JSON file at `~/design/worktree-registry.json` | Centralized tracking of all worktrees with metadata, ports, and status |
| Port Allocation Table | Console/JSON | Port assignments for each worktree in range 8100-8199 |
| Worktree List | Console/JSON | List of active worktrees with paths, branches, and ports |
| Validation Report | Console/JSON | Registry integrity check results with detected issues |
| Creation Confirmation | Console | Success message with worktree path and allocated port |
| Removal Confirmation | Console | Cleanup status and freed resources |

## Examples

### Example 1: Create a Feature Worktree

```bash
# Create worktree for new feature
python scripts/worktree_create.py --name feature-auth --branch feature/user-auth

# Allocate port for development server
python scripts/port_allocate.py --worktree feature-auth --port 8101

# Verify creation
python scripts/worktree_list.py
```

### Example 2: Clean Up After Merge

```bash
# List all worktrees
python scripts/worktree_list.py

# Remove merged worktree
python scripts/worktree_remove.py --name feature-auth --cleanup

# Validate registry
python scripts/registry_validate.py
```

## Error Handling

| Problem | Solution Reference |
|---------|-------------------|
| Registry file does not exist | [Port Management - Initializing Registry](references/port-management-part1-overview-registry.md#initializing-a-new-registry) |
| Registry file is corrupted | [Registry System - Troubleshooting](references/registry-system-part4-cleanup.md#registry-file-corrupted) |
| Registry contains orphaned entries | [Troubleshooting - Stale Worktree References](references/troubleshooting-part2-advanced-issues.md#4-stale-worktree-references) |
| Branch already checked out | [Troubleshooting - Branch Already Checked Out](references/troubleshooting-part1-basic-operations.md#1-branch-already-checked-out) |
| Directory exists but invalid | [Troubleshooting - Missing Worktree](references/troubleshooting-part1-basic-operations.md#3-missing-worktree) |
| Uncommitted changes block removal | [Removing Worktrees - Handling Failures](references/removing-worktrees-part1-basics.md#handling-removal-failures) |
| Port is already in use | [Troubleshooting - Port Conflicts](references/troubleshooting-part1-basic-operations.md#5-port-conflicts) |

## Best Practices

1. **Always Use Registry**: Record all worktrees in the registry, even manually created ones
2. **Allocate Ports in Advance**: Plan port usage to avoid conflicts
3. **Lock Worktrees**: Use `git worktree lock` for long-lived worktrees
4. **Regular Cleanup**: Remove unused worktrees promptly to avoid clutter
5. **Validate Registry**: Run validation scripts weekly to detect orphaned entries
6. **Document Purpose**: Include clear names and descriptions for each worktree
7. **Use Consistent Naming**: Follow naming conventions (e.g., `feature-name`, `bugfix-id`)
8. **Monitor Port Usage**: Check port allocations before starting services

## Next Steps

### For Beginners
1. Read [Worktree Fundamentals](references/worktree-fundamentals.md)
2. Read [Registry System](references/registry-system.md)
3. Review [Worktree Naming Conventions](references/worktree-naming-conventions.md)
4. Follow [Creating Worktrees](references/creating-worktrees.md)
5. Try the [Quick Start Workflows](references/quick-start-workflows.md)

### For Testing and Validation
1. Read [Review Worktree Isolation](references/review-worktree-isolation.md)
2. Follow [Testing Worktree Isolation](references/testing-worktree-isolation.md)
3. Use [Docker Worktree Testing](references/docker-worktree-testing.md)
4. See eia-verification-patterns skill

### For Automation
1. Review [Scripts and Automation](references/scripts-guide.md)
2. Use provided Python scripts for common operations
3. See eia-github-projects-sync skill
4. Set up automated validation with `registry_validate.py`

### For Troubleshooting
1. Check [Troubleshooting](references/troubleshooting.md)
2. Run `registry_validate.py` to detect problems
3. Review [Port Management](references/port-management.md)
4. Consult [Removing Worktrees](references/removing-worktrees.md)

## Resources

- [references/worktree-fundamentals.md](references/worktree-fundamentals.md) - Git worktree basics
- [references/registry-system.md](references/registry-system.md) - Registry management
- [references/creating-worktrees.md](references/creating-worktrees.md) - Creation workflows
- [references/port-allocation.md](references/port-allocation.md) - Port management
- [references/removing-worktrees.md](references/removing-worktrees.md) - Safe removal
- [references/troubleshooting.md](references/troubleshooting.md) - Problem solving
- [references/scripts-guide.md](references/scripts-guide.md) - Automation scripts

---

**Last Updated**: 2025-01-08
**Status**: Ready for Use
