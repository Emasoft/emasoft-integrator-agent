# Git Worktree Fundamentals - Concepts

## Table of Contents
1. [When you need to understand what git worktrees are → What Are Git Worktrees](#what-are-git-worktrees)
2. [If you're deciding whether to use worktrees → Why Use Worktrees](#why-use-worktrees)
3. [If you're comparing worktrees to branch switching → Worktree vs Branch](#worktree-vs-branch)
4. [When you need to understand how worktrees work internally → Core Concepts](#core-concepts)
5. [If you're deciding when to create a worktree → When to Use Worktrees](#when-to-use-worktrees)

**See also**: [worktree-fundamentals-operations.md](worktree-fundamentals-operations.md) for limitations, commands, and quick reference.

---

## What Are Git Worktrees

**Definition**: A Git worktree is an additional working directory linked to the same Git repository. It allows you to have multiple branches checked out simultaneously in separate directories, all sharing the same `.git` history and objects.

**Purpose**: Worktrees enable you to work on multiple branches at the same time without the need to stash changes, switch branches, or clone the repository multiple times.

**How It Works**: When you create a worktree, Git creates a new directory with its own working files, but all worktrees share the same underlying `.git` repository database. This means:
- All worktrees see the same commits, branches, and tags
- All worktrees share the same repository history
- Each worktree has its own independent working directory and HEAD pointer
- Each worktree can have different files checked out

**Example Structure**:
```
my-project/               ← Main worktree (original clone)
├── .git/                 ← Shared repository database
├── src/
├── tests/
└── README.md

my-project-feature-x/     ← Linked worktree
├── .git                  ← File pointing to main .git directory
├── src/
├── tests/
└── README.md

my-project-hotfix/        ← Another linked worktree
├── .git                  ← File pointing to main .git directory
├── src/
├── tests/
└── README.md
```

---

## Why Use Worktrees

### Benefits Over Branch Switching

**1. No Context Switching Overhead**
- **Problem with branch switching**: When you switch branches using `git checkout` or `git switch`, Git modifies your working directory files. This can:
  - Break running development servers
  - Invalidate IDE indexes
  - Require rebuilding dependencies
  - Lose unsaved IDE state

- **Worktree solution**: Each worktree is a separate directory. You can have:
  - Development server running in worktree A
  - Tests running in worktree B
  - Code editor open in worktree C
  - All at the same time, no interruption

**2. No Need to Stash Changes**
- **Problem with branch switching**: If you have uncommitted changes and need to switch branches, you must:
  - Commit incomplete work
  - Stash changes (and remember to unstash later)
  - Risk losing work if stash is forgotten

- **Worktree solution**: Changes in worktree A remain untouched when you work in worktree B. No stashing needed.

**3. Parallel Development**
- **Problem with single worktree**: You can only work on one branch at a time

- **Worktree solution**: Work on multiple features simultaneously:
  - Feature development in one worktree
  - Bug fixing in another worktree
  - Code review testing in a third worktree

**4. Faster Comparison and Testing**
- **Problem with branch switching**: To compare behavior between branches, you must:
  - Switch branch
  - Rebuild/reinstall
  - Test
  - Switch back
  - Repeat

- **Worktree solution**: Run both versions side-by-side and compare results immediately

**5. Disk Space Efficiency**
- **Alternative approach**: Clone repository multiple times
- **Problem**: Each clone duplicates the entire `.git` history (can be gigabytes)

- **Worktree solution**: All worktrees share one `.git` directory, saving disk space

---

## Worktree vs Branch

### Key Differences

| Aspect | Branch | Worktree |
|--------|--------|----------|
| **What it is** | A pointer to a commit in Git history | A physical directory on disk with a branch checked out |
| **Existence** | Exists only in Git metadata | Exists as a real directory in your filesystem |
| **Working files** | Must switch branches to see different files | Each worktree has its own set of files on disk |
| **Simultaneity** | Can only have one branch checked out at a time (in one worktree) | Can have multiple branches checked out in different worktrees |
| **IDE/Server state** | Lost when switching branches | Preserved independently in each worktree |
| **Uncommitted changes** | Must commit or stash before switching | Each worktree maintains its own uncommitted changes |

### When to Use Each

**Use Branches When**:
- You work on one task at a time sequentially
- You do not need to preserve running processes
- You do not need to compare branches side-by-side
- You have a simple, linear workflow

**Use Worktrees When**:
- You need to work on multiple branches simultaneously
- You want to test a pull request without losing your current work
- You need to make a hotfix while in the middle of feature development
- You want to run the same project with different branches side-by-side
- You review code and want to test changes in isolation

---

## Core Concepts

### 1. Main Worktree vs Linked Worktrees

**Main Worktree**:
- The original directory where you cloned or initialized the repository
- Contains the actual `.git` directory (a directory, not a file)
- Created with `git clone` or `git init`
- Can be deleted, but requires special handling
- All repository configuration lives here

**Example**:
```bash
# Create main worktree
git clone https://github.com/user/repo.git
cd repo
ls -la
# Shows: .git/ (directory), src/, README.md, etc.
```

**Linked Worktrees**:
- Additional directories created with `git worktree add`
- Contains a `.git` file (not a directory) that points to the main `.git` directory
- Can be easily added and removed
- Depends on the main worktree for repository data

**Example**:
```bash
# Create linked worktree
git worktree add ../repo-feature-x feature-x
cd ../repo-feature-x
cat .git
# Shows: gitdir: /path/to/repo/.git/worktrees/repo-feature-x
```

### 2. Shared .git Directory

**How Sharing Works**:
- All worktrees (main and linked) share the same repository database
- Objects (commits, trees, blobs) are stored only once
- Branches and tags are visible in all worktrees
- Configuration settings are shared
- Hooks are shared

**What This Means**:
- A commit made in worktree A is immediately visible in worktree B
- A branch created in worktree A can be checked out in worktree B (after worktree A is removed or switches branches)
- Fetching in one worktree updates all worktrees
- Pushing from any worktree pushes the same shared commits

**Example**:
```bash
# In main worktree
git commit -m "Add feature"
git log --oneline -1
# Shows: abc123 Add feature

# In linked worktree
git log --oneline -1
# Shows: abc123 Add feature (same commit immediately visible)
```

### 3. Independent Working Directories

**What is Independent**:
- Each worktree has its own working directory files on disk
- Each worktree has its own HEAD pointer (currently checked out commit)
- Each worktree has its own index (staging area)
- Each worktree can have different uncommitted changes

**What This Means**:
- Modifying files in worktree A does not change files in worktree B
- You can have different branches checked out in different worktrees
- You can stage different files in different worktrees

**Example**:
```bash
# In main worktree (on branch main)
echo "main content" > file.txt
git add file.txt

# In linked worktree (on branch feature-x)
echo "feature content" > file.txt
git add file.txt

# These are independent - each worktree has different staged content
```

### 4. Lock Mechanism

**What is the Lock Mechanism**:
- Git prevents the same branch from being checked out in multiple worktrees simultaneously
- This is a safety feature to prevent conflicts
- When a branch is checked out in one worktree, it is "locked" and cannot be checked out in another

**Why This Exists**:
- Prevents confusing situations where the same branch has different working directory states
- Avoids race conditions when committing to the same branch from different worktrees
- Maintains consistency of what a branch represents

**How It Works**:
```bash
# In main worktree
git checkout main

# In linked worktree
git checkout main
# ERROR: fatal: 'main' is already checked out at '/path/to/main-worktree'
```

**Working Around the Lock**:
- Check out different branches in different worktrees
- Create a new branch in the linked worktree if needed
- Remove the worktree that has the branch checked out
- Use `git worktree remove` to unlock the branch

**Example Workflow**:
```bash
# Main worktree on main
cd ~/project
git checkout main

# Create linked worktree for feature
git worktree add ../project-feature feature-x

# Create linked worktree for hotfix
git worktree add ../project-hotfix -b hotfix-123 main

# Now you have:
# - main worktree: main branch
# - project-feature: feature-x branch
# - project-hotfix: hotfix-123 branch (newly created from main)
```

---

## When to Use Worktrees

### 1. Code Reviews (Isolated Testing)

**Scenario**: You are working on feature-x, and a colleague asks you to review their pull request for feature-y.

**Without Worktrees**:
1. Stash or commit your current work on feature-x
2. Switch to feature-y branch
3. Rebuild dependencies
4. Restart development server
5. Test feature-y
6. Switch back to feature-x
7. Rebuild dependencies again
8. Unstash or continue work

**With Worktrees**:
1. Create a new worktree for feature-y: `git worktree add ../project-review feature-y`
2. Open the review worktree in a new terminal/editor
3. Test feature-y without touching your feature-x work
4. When done: `git worktree remove ../project-review`
5. Continue working on feature-x with no interruption

**Command Example**:
```bash
# You are on feature-x branch with uncommitted changes
git worktree add ../myproject-review origin/feature-y
cd ../myproject-review
npm install
npm test
# Review complete
cd -
git worktree remove ../myproject-review
# Back to feature-x, nothing changed
```

### 2. Parallel Feature Development

**Scenario**: You are working on two features simultaneously, and both require different dependencies or configurations.

**Use Case**:
- Feature A requires Node.js 18
- Feature B requires Node.js 20
- You need to work on both today

**With Worktrees**:
```bash
# Main worktree: feature-a with Node 18
cd ~/project
nvm use 18
git checkout feature-a

# Linked worktree: feature-b with Node 20
git worktree add ../project-feature-b feature-b
cd ../project-feature-b
nvm use 20

# Now you can work in both directories with different Node versions
```

### 3. Hotfix While in Feature Branch

**Scenario**: You are in the middle of developing a large feature (uncommitted changes), and a critical production bug is reported.

**Without Worktrees**:
1. Stash all your feature work
2. Switch to main branch
3. Create hotfix branch
4. Fix bug
5. Test, commit, push
6. Switch back to feature branch
7. Unstash changes
8. Hope nothing broke

**With Worktrees**:
```bash
# You are on feature-big with many uncommitted changes
git worktree add ../project-hotfix -b hotfix-critical-bug main
cd ../project-hotfix
# Fix bug, test, commit, push
git push origin hotfix-critical-bug
cd -
git worktree remove ../project-hotfix
# Your feature work untouched, still uncommitted
```

### 4. Testing Different Branches Simultaneously

**Scenario**: You need to compare the behavior of your application on two different branches (for example, main vs feature branch).

**Use Case**:
- Compare performance between main and your optimization branch
- Compare UI between main and your redesign branch
- Run integration tests against both versions

**With Worktrees**:
```bash
# Main worktree: production version on port 3000
cd ~/project
npm start -- --port 3000

# Linked worktree: feature version on port 3001
git worktree add ../project-feature feature-optimization
cd ../project-feature
npm install
npm start -- --port 3001

# Now compare http://localhost:3000 vs http://localhost:3001 side-by-side
```
