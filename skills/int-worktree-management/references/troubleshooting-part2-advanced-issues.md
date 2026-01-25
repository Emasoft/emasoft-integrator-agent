# Troubleshooting Worktree Issues - Part 2: Advanced Issues

This document covers advanced problems encountered with Git worktrees: dirty worktrees, submodule issues, permission errors, stale references, and prevention best practices.

---

## Table of Contents

1. [When worktree has uncommitted changes → Dirty Worktree](#1-dirty-worktree)
2. [If submodules are missing or broken → Submodule Issues](#2-submodule-issues)
3. [When you get permission denied errors → Permission Errors](#3-permission-errors)
4. [If git shows deleted worktrees → Stale Worktree References](#4-stale-worktree-references)
5. [General Troubleshooting Steps](#5-general-troubleshooting-steps)
6. [Getting Help](#6-getting-help)
7. [Prevention Best Practices](#7-prevention-best-practices)

**For basic operations troubleshooting**, see:
- [troubleshooting-part1-basic-operations.md](troubleshooting-part1-basic-operations.md) - Branch checkout conflicts, locked worktrees, missing worktrees, registry sync, port conflicts

---

## 1. Dirty Worktree

### Symptom
Cannot remove a worktree because it has uncommitted changes or untracked files.

### Error Message
```
fatal: '/path/to/worktree' contains modified or untracked files, use --force to delete it
```

### Cause
You are attempting to remove a worktree that has:
- Modified files (changed but not committed)
- Staged changes (added to index but not committed)
- Untracked files (new files not in git)

Git prevents removal to avoid data loss.

### Solution

**Option A: Save Changes (Recommended)**
```bash
# Navigate to the worktree
cd /path/to/worktree

# Check status
git status

# Commit the changes
git add .
git commit -m "Save work in progress"

# Now remove from main repo
cd /path/to/main-repo
git worktree remove /path/to/worktree
```

**Option B: Stash Changes**
```bash
# Stash changes to retrieve later
cd /path/to/worktree
git stash push -u -m "Stashing before worktree removal"

# Note the stash reference
git stash list
# stash@{0}: On branch-name: Stashing before worktree removal

# Remove worktree
cd /path/to/main-repo
git worktree remove /path/to/worktree

# Later, retrieve the stash in another worktree
cd /path/to/another-worktree
git stash apply stash@{0}
```

**Option C: Force Remove (Data Loss)**
```bash
# WARNING: This will permanently delete uncommitted changes!
git worktree remove --force /path/to/worktree
```

### Example
```bash
# Trying to remove worktree with uncommitted work
git worktree remove ~/worktrees/experiment
# fatal: '~/worktrees/experiment' contains modified or untracked files

# Check what's uncommitted
cd ~/worktrees/experiment
git status
# Modified: src/main.py
# Untracked: test_results.txt

# Decision: Work is valuable, commit it
git add .
git commit -m "WIP: experimental feature implementation"

# Now remove safely
cd ~/main-repo
git worktree remove ~/worktrees/experiment
# Success
```

---

## 2. Submodule Issues

### Symptom
Submodules are not initialized or are missing in a newly created worktree.

### Cause
When you create a new worktree, Git does not automatically initialize submodules. Submodules must be initialized separately in each worktree.

### Solution

**Step 1: Create Worktree**
```bash
# Create the worktree normally
git worktree add /path/to/new-worktree branch-name
```

**Step 2: Initialize Submodules**
```bash
# Navigate to the new worktree
cd /path/to/new-worktree

# Initialize and update submodules
git submodule update --init --recursive
```

**Step 3: Verify Submodules**
```bash
# Check submodule status
git submodule status

# Should show initialized submodules with commit hashes:
# abc123 path/to/submodule (v1.0.0)
```

### Automation
```bash
# Create a script to automate worktree creation with submodules
cat > create_worktree_with_submodules.sh << 'EOF'
#!/bin/bash
WORKTREE_PATH=$1
BRANCH_NAME=$2

git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
cd "$WORKTREE_PATH"
git submodule update --init --recursive
echo "Worktree created with submodules initialized"
EOF

chmod +x create_worktree_with_submodules.sh

# Use it
./create_worktree_with_submodules.sh ~/worktrees/feature-x feature-x
```

### Example
```bash
# Created worktree but code won't build
git worktree add ~/worktrees/fix-build bugfix

cd ~/worktrees/fix-build
npm install
# Error: Cannot find module 'vendor/library'

# Check submodules
git submodule status
# -abc123 vendor/library
# The minus sign (-) means uninitialized

# Initialize submodules
git submodule update --init --recursive
# Submodule 'vendor/library' (https://...) registered
# Cloning into '.../vendor/library'...
# Submodule path 'vendor/library': checked out 'abc123'

# Now build works
npm install
npm run build
# Success
```

---

## 3. Permission Errors

### Symptom
Cannot create a worktree in the target directory due to permission denied errors.

### Error Message
```
fatal: could not create directory '/path/to/worktree': Permission denied
```

### Cause
- Insufficient permissions on the target directory
- Parent directory is owned by another user
- Directory is on read-only filesystem
- SELinux or AppArmor restrictions

### Solution

**Step 1: Check Permissions**
```bash
# Check the target directory's parent
ls -la /path/to/parent

# Check your user
whoami

# Check ownership
stat /path/to/parent
```

**Step 2: Fix Permissions**

**If you own the parent directory:**
```bash
# Make sure you have write permissions
chmod u+w /path/to/parent
```

**If root owns the directory:**
```bash
# Change ownership to your user
sudo chown -R $(whoami):$(id -gn) /path/to/parent

# Or create worktree in your home directory instead
git worktree add ~/worktrees/my-feature branch-name
```

**If on network/shared drive:**
```bash
# Use a local directory instead
mkdir -p ~/local-worktrees
git worktree add ~/local-worktrees/my-feature branch-name
```

### Example
```bash
# Trying to create worktree in /opt/projects
git worktree add /opt/projects/feature-x feature-x
# fatal: could not create directory '/opt/projects/feature-x': Permission denied

# Check ownership
ls -la /opt/projects
# drwxr-xr-x  root  root  ... projects

# Option A: Change to user directory
git worktree add ~/worktrees/feature-x feature-x
# Success

# Option B: Fix permissions (if appropriate)
sudo chown -R $USER:$USER /opt/projects
git worktree add /opt/projects/feature-x feature-x
# Success
```

---

## 4. Stale Worktree References

### Symptom
`git worktree list` shows entries for worktrees that no longer exist or are invalid.

### Cause
- Directories were deleted manually without using `git worktree remove`
- System crash or power failure during worktree operations
- Network drives disconnected while worktrees were active
- `.git/worktrees/` directory was manually modified

### Solution

**Step 1: List All Worktrees**
```bash
# See which worktrees git knows about
git worktree list

# Look for entries that don't exist
# Example output:
# /home/user/main-repo        abc123 [main]
# /home/user/feature-a        def456 [feature-a]
# /mnt/external/feature-b     ghi789 [feature-b]  # <- This might be stale
```

**Step 2: Verify Each Worktree**
```bash
# Check if directories actually exist
ls -la /home/user/feature-a  # Should exist
ls -la /mnt/external/feature-b  # Might not exist
```

**Step 3: Dry Run Prune**
```bash
# See what would be pruned without actually doing it
git worktree prune --dry-run

# Output shows what will be removed:
# Removing worktrees/feature-b: gitdir file points to non-existent location
```

**Step 4: Prune Stale References**
```bash
# Actually remove the stale references
git worktree prune

# Verify cleanup
git worktree list
# /mnt/external/feature-b should now be gone
```

**Step 5: Update Registry**
```bash
# If using worktree registry, sync it
cd /path/to/integrator-agent/registry
python registry_validate.py --fix
```

### Force Prune with Verbose Output
```bash
# For stubborn cases, use verbose mode
git worktree prune --verbose

# Output:
# Removing worktrees/feature-b: gitdir file points to non-existent location
# Removing worktrees/old-experiment: gitdir file does not exist
```

### Example
```bash
# External drive was disconnected, but git still references it
git worktree list
# /Users/dev/main           abc123 [main]
# /Volumes/USB/project-x    def456 [project-x]  # USB was removed

# Try to remove it normally (fails)
git worktree remove /Volumes/USB/project-x
# fatal: '/Volumes/USB/project-x' does not exist

# Prune stale references
git worktree prune --dry-run
# Removing worktrees/project-x: gitdir file points to non-existent location

git worktree prune
# Cleaned up

# Verify
git worktree list
# /Users/dev/main           abc123 [main]
# /Volumes/USB/project-x is gone
```

---

## 5. General Troubleshooting Steps

When encountering any worktree issue:

1. **Check Current State**
   ```bash
   git worktree list
   git status
   ```

2. **Review Git Configuration**
   ```bash
   git config --list | grep worktree
   ```

3. **Check Disk Space**
   ```bash
   df -h /path/to/worktrees
   ```

4. **Validate Registry (if using)**
   ```bash
   python registry_validate.py --dry-run
   ```

5. **Consult Git Logs**
   ```bash
   git reflog
   git log --oneline --all --graph
   ```

6. **Use Verbose Mode**
   ```bash
   git worktree add --verbose /path/to/worktree branch
   git worktree remove --verbose /path/to/worktree
   ```

---

## 6. Getting Help

If you encounter issues not covered here:

1. Check Git worktree documentation: `git worktree --help`
2. Review the worktree management skill's other reference documents
3. Examine the `.git/worktrees/` directory structure
4. Enable Git trace mode: `GIT_TRACE=1 git worktree <command>`
5. Check the registry validation logs (if using the registry system)

---

## 7. Prevention Best Practices

To avoid common issues:

- **Always use `git worktree remove`** instead of manually deleting directories
- **Use the registry system** to track worktrees and allocate resources
- **Run `git worktree prune` regularly** to clean up stale references
- **Lock worktrees** on removable media: `git worktree lock /path/to/worktree`
- **Document worktree purpose** in the registry metadata
- **Initialize submodules** immediately after creating worktrees
- **Commit or stash** work before removing worktrees
- **Validate the registry** before and after major operations

---

## Related Documents

- [troubleshooting-part1-basic-operations.md](troubleshooting-part1-basic-operations.md) - Branch checkout conflicts, locked worktrees, missing worktrees, registry sync, port conflicts
