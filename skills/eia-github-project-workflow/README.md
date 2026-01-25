# GitHub Project Workflow Skill

Track multi-developer work using GitHub Projects boards, issues with acceptance criteria, and Kanban workflows.

## When to Use

- Creating project boards with standard columns (Todo, In Progress, Review, Done)
- Creating issues with clear acceptance criteria
- Tracking task status through Kanban workflow
- Managing labels and dependencies across multiple developers

## Quick Reference

### Workflow Steps

1. Analyze requirements
2. Create task plan
3. Create GitHub Project Board
4. Create Issues with acceptance criteria
5. Assign issues to developers
6. Monitor progress via issue updates
7. Review completion via PR links
8. Integration decision making

### GitHub Project Board Columns

| Column | Tasks In This State |
|--------|---------------------|
| Todo | Not yet started |
| In Progress | Developer working on it |
| Review | PR created, awaiting review |
| Done | Verified complete |

### Standard Labels

| Label | Meaning |
|-------|---------|
| `subtask` | Individual work item |
| `integration` | Integration task |
| `blocker` | Blocking other tasks |
| `verification-needed` | Requires review |

### Workflow Summary

| Step | Action | GitHub Output |
|------|--------|---------------|
| 1 | Analyze requirements | - |
| 2 | Create task plan | docs_dev/plan.md |
| 3 | Create Project Board | Board with columns |
| 4 | Create Issues | Issues with criteria |
| 5 | Assign to developers | Issue assignments |
| 6 | Monitor progress | Read issue comments |
| 7 | Review completion | Check linked PRs |
| 8 | Integration decision | Merge authorization |

## Documentation

- **[SKILL.md](SKILL.md)** - Main skill documentation with TOC
- **[references/procedure-steps.md](references/procedure-steps.md)** - Detailed workflow steps
- **[references/instruction-templates.md](references/instruction-templates.md)** - Issue templates
- **[references/communication-patterns.md](references/communication-patterns.md)** - Failure handling

## Key Principles

1. **Tracking via GitHub Projects** - Use issues and boards for all work
2. **One task per developer** - No multitasking
3. **Clear acceptance criteria** - Every issue has success criteria
4. **TDD first** - Tests before integration approval

**Note**: This skill handles GitHub-side tracking only. AI Maestro messaging is orchestrator-only.
