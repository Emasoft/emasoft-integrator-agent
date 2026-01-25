# Port Allocation for Worktrees

This document provides an overview of the port allocation system for worktrees. The content has been split into four parts for easier navigation.

---

## Document Overview

| Part | File | Topics |
|------|------|--------|
| 1 | [port-allocation-part1-core-concepts.md](./port-allocation-part1-core-concepts.md) | Core concepts, port ranges, allocation algorithm |
| 2 | [port-allocation-part2-config-status.md](./port-allocation-part2-config-status.md) | Configuration templates, port status commands |
| 3 | [port-allocation-part3-conflict-docker.md](./port-allocation-part3-conflict-docker.md) | Conflict resolution, Docker integration |
| 4 | [port-allocation-part4-cleanup-troubleshooting.md](./port-allocation-part4-cleanup-troubleshooting.md) | Port cleanup, troubleshooting, quick reference |

---

## Complete Table of Contents

### Part 1: Core Concepts
- [port-allocation-part1-core-concepts.md](./port-allocation-part1-core-concepts.md)

1. When you need to understand why ports matter → Why Port Allocation is Needed
2. If you need to understand port organization → Understanding Port Ranges
3. When you need to know how ports are assigned → Port Allocation Algorithm

### Part 2: Configuration & Status
- [port-allocation-part2-config-status.md](./port-allocation-part2-config-status.md)

4. If you need to generate worktree configurations → Configuration Templates
5. When you need to check port status → Port Status Commands

### Part 3: Conflict Resolution & Docker
- [port-allocation-part3-conflict-docker.md](./port-allocation-part3-conflict-docker.md)

6. If you encounter port conflicts → Conflict Resolution
7. When you need to use Docker with worktrees → Integration with Docker

### Part 4: Cleanup & Troubleshooting
- [port-allocation-part4-cleanup-troubleshooting.md](./port-allocation-part4-cleanup-troubleshooting.md)

8. If you need to release or reset ports → Port Cleanup
9. When you encounter port allocation problems → Troubleshooting
10. Quick command reference → Quick Reference

---

## Quick Navigation by Use Case

| If you need to... | Go to |
|-------------------|-------|
| Understand why port allocation exists | Part 1 - Why Port Allocation is Needed |
| Learn about port ranges | Part 1 - Understanding Port Ranges |
| Understand how ports are assigned | Part 1 - Port Allocation Algorithm |
| Create configuration templates | Part 2 - Configuration Templates |
| Check port status | Part 2 - Port Status Commands |
| Resolve port conflicts | Part 3 - Conflict Resolution |
| Use Docker with worktrees | Part 3 - Integration with Docker |
| Clean up unused ports | Part 4 - Port Cleanup |
| Fix port-related issues | Part 4 - Troubleshooting |
| Find command reference | Part 4 - Quick Reference |

---

## Key Files Reference

```
Registry:           .git/worktree-registry/ports.json
Config Template:    .env.worktree.template
Docker Template:    docker-compose.worktree.template.yml
Generated Config:   <worktree>/.env.worktree
Generated Docker:   <worktree>/docker-compose.yml
```

## Port Ranges Summary

| Service | Range | Count |
|---------|-------|-------|
| Web | 8080-8099 | 20 |
| Database | 5432-5439 | 8 |
| Testing | 9000-9099 | 100 |
| Debug | 5555-5564 | 10 |
| API | 3000-3099 | 100 |

---

## Common Commands Quick Reference

```bash
# Allocate ports for new worktree
atlas worktree create <name>  # Auto-allocates

# List all ports
atlas port list

# Check specific port
atlas port check <port>

# Show ports for worktree
atlas port show <worktree>

# Release ports
atlas port release <worktree>

# Clean up stale allocations
atlas port cleanup

# Rebuild registry
atlas port scan-rebuild

# Check port conflicts
atlas port check-conflicts
```
