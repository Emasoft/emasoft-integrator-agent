# Git Worktree Fundamentals - Index

This document provides a complete reference for Git worktrees. The content is organized into two files for easier navigation.

---

## Part 1: Concepts
**File**: [worktree-fundamentals-concepts.md](worktree-fundamentals-concepts.md)

### Contents
1. **What Are Git Worktrees** - Definition, purpose, and how worktrees work internally
2. **Why Use Worktrees** - Benefits over branch switching (no context switching, no stashing, parallel development, disk efficiency)
3. **Worktree vs Branch** - Key differences and when to use each
4. **Core Concepts** - Main vs linked worktrees, shared .git directory, independent working directories, lock mechanism
5. **When to Use Worktrees** - Code reviews, parallel feature development, hotfixes, testing different branches

---

## Part 2: Operations
**File**: [worktree-fundamentals-operations.md](worktree-fundamentals-operations.md)

### Contents
1. **Limitations** - Branch locking, staging area considerations, submodule behavior, sparse checkout, hooks
2. **Basic Commands** - `git worktree add`, `git worktree list`, `git worktree remove`, `git worktree prune`
3. **Quick Reference** - Compact command cheatsheet
4. **Summary** - Key takeaways

---

## Quick Navigation

| If you need to... | Read this section |
|-------------------|-------------------|
| Understand what worktrees are | [Concepts: What Are Git Worktrees](worktree-fundamentals-concepts.md#what-are-git-worktrees) |
| Decide whether to use worktrees | [Concepts: Why Use Worktrees](worktree-fundamentals-concepts.md#why-use-worktrees) |
| Compare worktrees vs branches | [Concepts: Worktree vs Branch](worktree-fundamentals-concepts.md#worktree-vs-branch) |
| Learn internal mechanics | [Concepts: Core Concepts](worktree-fundamentals-concepts.md#core-concepts) |
| Find use case examples | [Concepts: When to Use Worktrees](worktree-fundamentals-concepts.md#when-to-use-worktrees) |
| Know worktree constraints | [Operations: Limitations](worktree-fundamentals-operations.md#limitations) |
| Run worktree commands | [Operations: Basic Commands](worktree-fundamentals-operations.md#basic-commands) |
| Get a quick cheatsheet | [Operations: Quick Reference](worktree-fundamentals-operations.md#quick-reference) |
