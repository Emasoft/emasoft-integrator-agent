# Troubleshooting Worktree Issues - Part 1: Basic Operations

This document covers common problems encountered with basic Git worktree operations: branch checkout conflicts, locked worktrees, missing worktrees, registry synchronization, and port conflicts.

---

## Table of Contents

1. [If branch is already checked out in another worktree → Branch Already Checked Out](#1-branch-already-checked-out)
2. [When worktree is locked and can't be removed → Cannot Remove Locked Worktree](#2-cannot-remove-locked-worktree)
3. [If worktree directory was deleted manually → Missing Worktree](#3-missing-worktree)
4. [When registry doesn't match filesystem → Registry Out of Sync](#4-registry-out-of-sync)
5. [If services fail to start due to ports → Port Conflicts](#5-port-conflicts)

**For additional troubleshooting topics**, see:
- [troubleshooting-part2-advanced-issues.md](troubleshooting-part2-advanced-issues.md) - Dirty worktrees, submodules, permissions, stale references, and prevention best practices

---

## 1. Branch Already Checked Out

### Error Message
```
fatal: 'feature-branch' is already checked out at '/path/to/other/worktree'
```

### Cause
You are attempting to check out a branch that is already checked out in another worktree. Git prevents the same branch from being active in multiple worktrees simultaneously to avoid conflicts.

### Solution

**Option A: Use a Different Branch**
```bash
# Create and checkout a new branch from the desired branch
git worktree add /path/to/new-worktree -b new-branch-name existing-branch
```

**Option B: Remove the Other Worktree**
```bash
# List all worktrees to find the conflicting one
git worktree list

# Remove the conflicting worktree
git worktree remove /path/to/other/worktree

# Now create the new worktree
git worktree add /path/to/new-worktree existing-branch
```

**Option C: Use Detached HEAD**
```bash
# Create worktree in detached HEAD state at the same commit
git worktree add /path/to/new-worktree --detach existing-branch
```

### Example
```bash
# Scenario: feature-x is checked out in ~/worktrees/feature-x-dev
# You want to create another worktree for the same feature

# Bad: This will fail
git worktree add ~/worktrees/feature-x-testing feature-x

# Good: Create a new branch
git worktree add ~/worktrees/feature-x-testing -b feature-x-testing feature-x
```

---

## 2. Cannot Remove Locked Worktree

### Error Message
```
fatal: 'path/to/worktree' is locked; use 'unlock' to override, or 'remove --force'
```

### Cause
The worktree has been locked, either manually or automatically by Git. Locking prevents accidental removal of a worktree, especially on removable media or network drives.

### Solution

**Step 1: Check Lock Status**
```bash
# See which worktrees are locked
git worktree list

# Output shows lock status:
# /path/to/worktree  abc123 [branch-name] locked
```

**Step 2: Unlock the Worktree**
```bash
# Unlock the worktree
git worktree unlock /path/to/worktree
```

**Step 3: Remove the Worktree**
```bash
# Now remove it normally
git worktree remove /path/to/worktree
```

**Alternative: Force Remove**
```bash
# Remove without unlocking (use with caution)
git worktree remove --force /path/to/worktree
```

### Example
```bash
# Worktree was locked for protection
git worktree list
# /Users/dev/worktrees/production  def456 [main] locked

# Unlock it
git worktree unlock /Users/dev/worktrees/production

# Verify unlock
git worktree list
# /Users/dev/worktrees/production  def456 [main]

# Now remove
git worktree remove /Users/dev/worktrees/production
```

---

## 3. Missing Worktree

### Error Message
```
fatal: '/path/to/worktree' does not exist
```

### Cause
The worktree directory was deleted manually (using `rm -rf` or file manager) without using `git worktree remove`. Git's internal registry still references the deleted directory.

### Solution

**Step 1: Verify the Problem**
```bash
# List all worktrees - you'll see the missing one
git worktree list

# Check if directory exists
ls -la /path/to/worktree  # Should show "No such file or directory"
```

**Step 2: Prune Stale References**
```bash
# Dry run to see what will be removed
git worktree prune --dry-run

# Actually prune the stale references
git worktree prune
```

**Step 3: Verify Cleanup**
```bash
# Verify the worktree is gone from the list
git worktree list
```

### Example
```bash
# Someone deleted the directory directly
rm -rf ~/worktrees/old-feature

# Git still thinks it exists
git worktree list
# ~/worktrees/old-feature  abc123 [old-feature]  # Ghost entry

# Prune the registry
git worktree prune --dry-run
# Removing worktrees/old-feature: gitdir file points to non-existent location

git worktree prune
# Cleaned up references

git worktree list
# ~/worktrees/old-feature is now gone from the list
```

---

## 4. Registry Out of Sync

### Symptom
The worktree registry (JSON file) shows worktrees that no longer exist, or is missing worktrees that do exist.

### Cause
The registry was not updated when worktrees were created or destroyed. This can happen if:
- Worktrees were created manually without updating the registry
- The registry file was corrupted or edited incorrectly
- Multiple agents modified worktrees simultaneously without proper locking

### Solution

**Step 1: Run Registry Validation**
```bash
# Navigate to the registry directory
cd /path/to/integrator-agent/registry

# Run validation script in dry-run mode
python registry_validate.py --dry-run

# Review the output to see what will be fixed
```

**Step 2: Fix Registry**
```bash
# Apply fixes automatically
python registry_validate.py --fix

# The script will:
# - Remove entries for non-existent worktrees
# - Add entries for discovered worktrees
# - Validate port allocations
# - Fix corrupted metadata
```

**Step 3: Verify Results**
```bash
# Check the registry is now consistent
python registry_validate.py --dry-run

# Should report: "Registry is valid. No issues found."
```

### Manual Verification
```bash
# Compare git worktree list with registry
git worktree list

# Check registry file
cat worktree_registry.json | jq '.worktrees'

# They should match
```

### Example
```bash
# Registry shows 5 worktrees, but git worktree list shows 3
python registry_validate.py --dry-run
# Found 2 orphaned registry entries: feature-x, bugfix-y
# Found 0 unregistered worktrees

# Fix it
python registry_validate.py --fix
# Removed entry: feature-x (directory not found)
# Removed entry: bugfix-y (directory not found)
# Registry updated successfully

# Verify
git worktree list | wc -l  # 3
cat worktree_registry.json | jq '.worktrees | length'  # 3
# Now in sync
```

---

## 5. Port Conflicts

### Symptom
A service (development server, API, database) fails to start because its allocated port is already in use.

### Cause
- Another process is using the port
- The port was not properly released from a previous session
- Multiple worktrees were assigned the same port
- External service is using the port

### Solution

**Step 1: Identify the Conflict**
```bash
# Check what's using the port (example: port 8080)
lsof -i :8080

# Output shows:
# COMMAND  PID   USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
# node     1234  user   21u  IPv4  0x...      0t0  TCP *:8080 (LISTEN)
```

**Step 2: Stop the Conflicting Process**
```bash
# Option A: Kill by PID
kill 1234

# Option B: Kill by port (macOS/Linux)
lsof -ti:8080 | xargs kill

# Option C: Gracefully stop if you know what it is
# (e.g., if it's another worktree's dev server)
```

**Step 3: Reallocate Port**
```bash
# Use the registry script to allocate a new port
cd /path/to/integrator-agent/registry

# Reallocate port for the worktree
python registry_allocate_port.py --worktree my-feature --new-port

# The script will find an available port and update the registry
```

**Step 4: Update Service Configuration**
```bash
# Update your service config to use the new port
# For example, update .env file:
cd /path/to/worktree
echo "DEV_SERVER_PORT=8081" >> .env

# Restart the service
npm run dev  # or whatever command starts your service
```

### Prevention
```bash
# Always allocate ports through the registry
python registry_allocate_port.py --worktree new-feature

# The registry tracks all allocations and prevents conflicts
```

### Example
```bash
# Trying to start dev server fails
npm run dev
# Error: Port 3000 is already in use

# Check what's using it
lsof -i :3000
# node  5678  user  21u  IPv4  *:3000 (LISTEN)

# It's another worktree! Check registry
cat worktree_registry.json | jq '.worktrees[] | select(.ports.dev_server == 3000)'
# Shows: feature-a and feature-b both allocated 3000 (conflict!)

# Reallocate port for feature-b
python registry_allocate_port.py --worktree feature-b --service dev_server
# Allocated port 3001 for feature-b

# Update feature-b's .env
cd ~/worktrees/feature-b
echo "DEV_SERVER_PORT=3001" > .env

# Start server
npm run dev
# Success! Server running on port 3001
```

---

## Next Steps

For additional troubleshooting topics, see [troubleshooting-part2-advanced-issues.md](troubleshooting-part2-advanced-issues.md):

- Dirty Worktree (uncommitted changes)
- Submodule Issues
- Permission Errors
- Stale Worktree References
- General Troubleshooting Steps
- Prevention Best Practices
