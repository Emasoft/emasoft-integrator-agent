# Git Worktree Fundamentals - Operations

## Table of Contents
1. [When you need to know worktree constraints → Limitations](#limitations)
2. [If you need quick command reference → Basic Commands](#basic-commands)
3. [If you need a compact cheatsheet → Quick Reference](#quick-reference)
4. [When you need a high-level overview → Summary](#summary)

**See also**: [worktree-fundamentals-concepts.md](worktree-fundamentals-concepts.md) for concepts, benefits, and use cases.

---

## Limitations

### 1. Cannot Have Same Branch in Multiple Worktrees

**The Limitation**: Git enforces that a branch can only be checked out in one worktree at a time.

**Why This Limitation Exists**:
- Prevents ambiguity about what the branch HEAD points to
- Avoids conflicts when committing to the same branch from different locations
- Maintains consistency of branch state

**How It Manifests**:
```bash
# Main worktree
git checkout main

# Linked worktree
git worktree add ../project-test main
# ERROR: fatal: 'main' is already checked out at '/path/to/project'
```

**Workaround**:
- Create a new branch from the desired branch:
  ```bash
  git worktree add ../project-test -b test-main main
  ```
- Checkout a detached HEAD at the same commit:
  ```bash
  git worktree add ../project-test --detach main
  ```
- Remove the worktree where the branch is currently checked out first

### 2. Shared Staging Area Considerations

**The Limitation**: While each worktree has its own index (staging area), certain operations can have unexpected interactions.

**What This Means**:
- Each worktree stages files independently
- However, all worktrees share the same object database
- Commits made in one worktree are immediately visible in all worktrees
- Reflogs are shared across worktrees

**Potential Confusion**:
```bash
# Worktree A
git add file.txt
git status
# Shows: file.txt staged

# Worktree B (different branch)
git status
# Shows: nothing staged (independent index)

# Worktree A
git commit -m "Update file"

# Worktree B
git log
# Shows: the commit from Worktree A (shared history)
```

**Best Practice**:
- Treat each worktree as if it were a separate clone
- Avoid confusing yourself by checking logs in one worktree right after committing in another
- Always verify which worktree you are in before committing

### 3. Submodule Behavior

**The Limitation**: Submodules can behave unexpectedly with worktrees.

**Issues**:
- Submodules are not automatically shared between worktrees
- Each worktree may need its own submodule initialization
- Submodule updates in one worktree do not automatically propagate to others
- The `.git` directory of submodules can become inconsistent

**How It Manifests**:
```bash
# Main worktree
git submodule update --init

# Linked worktree
ls submodule-dir/
# May be empty or outdated

# Need to initialize again
git submodule update --init
```

**Best Practice**:
- Always run `git submodule update --init` after creating a worktree if your project uses submodules
- Be aware that submodule commits are independent in each worktree
- Consider whether you really need worktrees if your project relies heavily on submodules

**Alternative**:
- Use a script to ensure submodules are synchronized:
  ```bash
  git worktree add ../project-feature feature-x
  cd ../project-feature
  git submodule update --init --recursive
  ```

### 4. Additional Limitations

**Sparse Checkout**:
- Sparse checkout configuration is shared, which can cause issues
- Worktrees might have unexpected files missing or present

**Hooks**:
- Git hooks are shared among all worktrees
- A hook in one worktree affects all worktrees
- May need conditional logic in hooks to handle different worktrees

**Deletion Safety**:
- Deleting a worktree directory manually (without `git worktree remove`) leaves orphaned metadata
- Must use `git worktree prune` to clean up

---

## Basic Commands

### 1. git worktree add

**Purpose**: Create a new linked worktree.

**Basic Syntax**:
```bash
git worktree add <path> <branch>
```

**Parameters**:
- `<path>`: The directory where the new worktree will be created (must not exist)
- `<branch>`: The branch to checkout in the new worktree (optional)

**Common Usage**:

**Example 1: Checkout existing branch**
```bash
git worktree add ../project-feature feature-x
# Creates worktree at ../project-feature with feature-x branch checked out
```

**Example 2: Create and checkout new branch**
```bash
git worktree add ../project-feature -b feature-new main
# Creates worktree at ../project-feature
# Creates new branch feature-new based on main
# Checks out feature-new in the new worktree
```

**Example 3: Detached HEAD**
```bash
git worktree add ../project-test --detach main
# Creates worktree at ../project-test
# Checks out main commit in detached HEAD state
# Useful for temporary testing without branch lock
```

**Example 4: Checkout remote branch**
```bash
git worktree add ../project-review origin/pull-request-123
# Creates worktree at ../project-review
# Checks out remote branch origin/pull-request-123
```

**Flags**:
- `-b <new-branch>`: Create a new branch and check it out
- `-B <new-branch>`: Create a new branch (force) and check it out, even if it exists
- `--detach`: Checkout in detached HEAD state
- `--force`: Force creation even if directory exists or branch is checked out (dangerous)

**What Happens**:
1. Git creates the directory at `<path>`
2. Git creates a `.git` file (not directory) pointing to main repository
3. Git checks out the specified branch
4. Git updates the worktree metadata in `.git/worktrees/`

### 2. git worktree list

**Purpose**: Show all worktrees and their status.

**Basic Syntax**:
```bash
git worktree list
```

**Example Output**:
```
/Users/dev/project        abc123 [main]
/Users/dev/project-feature-x  def456 [feature-x]
/Users/dev/project-hotfix     789abc [hotfix-bug]
```

**Output Format**:
- First column: Worktree path
- Second column: Current commit hash
- Third column: Current branch (in brackets)

**Flags**:
- `--porcelain`: Machine-readable output
- `-v` or `--verbose`: Show additional information (locked status, prunable status)

**Example with Verbose**:
```bash
git worktree list -v
```

Output:
```
/Users/dev/project        abc123 [main]
/Users/dev/project-feature-x  def456 [feature-x]
/Users/dev/project-hotfix     789abc [hotfix-bug] locked: being rebased
```

**Use Cases**:
- Check which worktrees exist
- Find out which branch is checked out where
- Identify worktrees that need cleanup
- Verify worktree paths before switching

### 3. git worktree remove

**Purpose**: Remove a linked worktree cleanly.

**Basic Syntax**:
```bash
git worktree remove <path>
```

**Parameters**:
- `<path>`: The path to the worktree to remove

**Example**:
```bash
git worktree remove ../project-feature
# Removes the worktree at ../project-feature
# Deletes the directory and Git metadata
# Unlocks the branch that was checked out
```

**What Happens**:
1. Git verifies the worktree has no uncommitted changes (by default)
2. Git removes the worktree directory
3. Git removes metadata from `.git/worktrees/`
4. Git unlocks the branch that was checked out

**Flags**:
- `--force`: Remove even if there are uncommitted changes or untracked files

**Example with Force**:
```bash
git worktree remove --force ../project-feature
# Removes worktree even with uncommitted changes (data loss!)
```

**Safety**:
- By default, Git refuses to remove a worktree with uncommitted changes
- Use `--force` only if you are certain you do not need the changes
- Always verify the path before removing

**Error Handling**:
```bash
git worktree remove ../project-feature
# ERROR: fatal: validation failed, cannot remove working tree
# Reason: has uncommitted changes

git status
# Review changes

git commit -m "Save changes" OR git restore .
# Clean up

git worktree remove ../project-feature
# SUCCESS
```

### 4. git worktree prune

**Purpose**: Clean up stale worktree metadata.

**Basic Syntax**:
```bash
git worktree prune
```

**When to Use**:
- After manually deleting a worktree directory (without using `git worktree remove`)
- When worktree metadata is corrupted
- When you see phantom worktrees in `git worktree list`

**What It Does**:
- Scans `.git/worktrees/` directory
- Identifies worktree entries whose directories no longer exist
- Removes orphaned metadata entries

**Example Scenario**:
```bash
# Accidentally delete worktree directory manually
rm -rf ../project-feature

# Worktree list still shows it
git worktree list
# Shows: /path/to/project-feature  def456 [feature-x]

# Branch is still locked
git checkout feature-x
# ERROR: feature-x is already checked out

# Prune orphaned worktrees
git worktree prune

# Now worktree list is clean
git worktree list
# No longer shows project-feature

# Branch is unlocked
git checkout feature-x
# SUCCESS
```

**Flags**:
- `-n` or `--dry-run`: Show what would be pruned without actually pruning
- `-v` or `--verbose`: Show detailed information about what is being pruned

**Best Practice**:
- Always use `git worktree remove` instead of manually deleting directories
- Run `git worktree prune` periodically if you manage many worktrees
- Use `--dry-run` first to verify what will be removed

---

## Quick Reference

**Create worktree with existing branch**:
```bash
git worktree add <path> <branch>
```

**Create worktree with new branch**:
```bash
git worktree add <path> -b <new-branch> <base-branch>
```

**List all worktrees**:
```bash
git worktree list
```

**Remove worktree**:
```bash
git worktree remove <path>
```

**Clean up orphaned worktrees**:
```bash
git worktree prune
```

**Check branch availability**:
```bash
git worktree list | grep <branch-name>
```

---

## Summary

Git worktrees provide a powerful way to work with multiple branches simultaneously without the overhead of cloning repositories multiple times or constantly switching branches. They are especially useful for code reviews, parallel development, hotfixes, and testing scenarios.

**Key Takeaways**:
1. Worktrees are separate directories sharing the same Git repository
2. Each worktree can have a different branch checked out
3. All worktrees share the same commit history and repository database
4. A branch can only be checked out in one worktree at a time
5. Use `git worktree add` to create, `git worktree remove` to delete
6. Always use Git commands to manage worktrees, not manual file operations
