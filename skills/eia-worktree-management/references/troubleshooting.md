# Troubleshooting Worktree Issues - Index

This index provides quick access to all worktree troubleshooting documentation.

---

## Part 1: Basic Operations
**File:** [troubleshooting-part1-basic-operations.md](troubleshooting-part1-basic-operations.md)

| Section | Problem | When to Read |
|---------|---------|--------------|
| 1. Branch Already Checked Out | `fatal: 'branch' is already checked out` | When trying to checkout a branch used elsewhere |
| 2. Cannot Remove Locked Worktree | `fatal: 'path' is locked` | When worktree removal fails due to lock |
| 3. Missing Worktree | `fatal: 'path' does not exist` | When directory was deleted manually |
| 4. Registry Out of Sync | Registry doesn't match filesystem | When worktree count mismatches |
| 5. Port Conflicts | Service fails to start on allocated port | When ports are already in use |

---

## Part 2: Advanced Issues
**File:** [troubleshooting-part2-advanced-issues.md](troubleshooting-part2-advanced-issues.md)

| Section | Problem | When to Read |
|---------|---------|--------------|
| 1. Dirty Worktree | `contains modified or untracked files` | When removal blocked by uncommitted changes |
| 2. Submodule Issues | Submodules missing or broken | When code fails to build in new worktree |
| 3. Permission Errors | `Permission denied` | When cannot create worktree in target directory |
| 4. Stale Worktree References | Ghost entries in `git worktree list` | When list shows non-existent worktrees |
| 5. General Troubleshooting Steps | Any worktree issue | First steps for any problem |
| 6. Getting Help | Need additional resources | When issue not covered in docs |
| 7. Prevention Best Practices | Avoiding future issues | Before starting worktree operations |

---

## Quick Reference

### Most Common Issues

1. **Branch already checked out?** → Use `-b new-branch-name` or `--detach`
2. **Worktree locked?** → Run `git worktree unlock /path`
3. **Directory deleted manually?** → Run `git worktree prune`
4. **Port in use?** → Check `lsof -i :PORT` and reallocate
5. **Uncommitted changes?** → Commit, stash, or use `--force`
6. **Submodules missing?** → Run `git submodule update --init --recursive`

### Emergency Commands

```bash
# Prune all stale worktree references
git worktree prune

# Force remove a worktree (CAUTION: loses uncommitted work)
git worktree remove --force /path/to/worktree

# List all worktrees with status
git worktree list

# Validate and fix registry
python registry_validate.py --fix
```
