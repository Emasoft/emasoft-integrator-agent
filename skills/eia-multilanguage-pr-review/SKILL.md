---
name: eia-multilanguage-pr-review
description: Review pull requests in repositories containing multiple programming languages and targeting multiple platforms. Teaches language detection, routing reviews to appropriate checkers, and coordinating cross-language concerns.
license: Apache-2.0
version: 1.0.0
author: Emasoft
metadata:
  category: code-review
  complexity: advanced
  requires_tools:
    - gh
    - git
  supported_languages:
    - python
    - javascript
    - typescript
    - rust
    - go
    - bash
    - shell
agent: code-reviewer
context: fork
---

# Multilanguage PR Review Skill

## Overview

Modern repositories often contain code in multiple programming languages. A single repository might have:
- A Python backend with FastAPI
- A TypeScript frontend with React
- Rust binaries for performance-critical operations
- Go microservices
- Bash scripts for automation and CI/CD

Reviewing PRs in such repositories requires understanding which languages are affected and applying the appropriate review standards for each.

## Challenges of Multilanguage Repositories

1. **Different coding standards**: Each language has its own conventions for naming, formatting, and structure
2. **Different testing frameworks**: pytest for Python, Jest for JavaScript, cargo test for Rust
3. **Different linting tools**: ruff/mypy for Python, ESLint for JavaScript, Clippy for Rust
4. **Cross-language interfaces**: FFI boundaries, API contracts, data serialization
5. **Platform-specific code**: Code paths that only run on certain operating systems

## When to Use This Skill

Use this skill when:
- Reviewing a PR that touches files in multiple programming languages
- Setting up review workflows for a polyglot repository
- Determining which linters and checkers to run for changed files
- Coordinating cross-language interface reviews

## Quick Reference: Language Detection

For detailed language detection methods, see [language-detection.md](references/language-detection.md):
- 1.1 Detecting language from file extensions
- 1.2 Detecting language from shebang lines
- 1.3 Using .gitattributes linguist hints
- 1.4 Understanding GitHub's language detection algorithm
- 1.5 Handling mixed-language files

## Quick Reference: Language-Specific Review Patterns

### Python Reviews
See [python-review-patterns.md](references/python-review-patterns.md):
- 2.1 Python code style and formatting checklist
- 2.2 Type hints verification and mypy compliance
- 2.3 Docstring standards (Google, NumPy, Sphinx)
- 2.4 Import organization and dependency management
- 2.5 Test framework patterns with pytest
- 2.6 Linting with ruff, mypy, and bandit

### JavaScript/TypeScript Reviews
See [javascript-review-patterns.md](references/javascript-review-patterns.md):
- 3.1 JavaScript/TypeScript code style checklist
- 3.2 Type safety patterns in TypeScript
- 3.3 Module system considerations (ESM vs CommonJS)
- 3.4 Test framework patterns with Jest and Vitest
- 3.5 Linting with ESLint and Prettier

### Rust Reviews
See [rust-review-patterns.md](references/rust-review-patterns.md):
- 4.1 Rust code style and idioms checklist
- 4.2 Memory safety patterns and ownership
- 4.3 Error handling with Result and Option
- 4.4 Clippy lints and configuration
- 4.5 Documentation standards with rustdoc

### Go Reviews
See [go-review-patterns.md](references/go-review-patterns.md):
- 5.1 Go code style and idioms checklist
- 5.2 Error handling patterns in Go
- 5.3 Package organization and naming
- 5.4 Test patterns with go test
- 5.5 Linting with golint, go vet, and staticcheck

### Shell Script Reviews
See [shell-review-patterns.md](references/shell-review-patterns.md):
- 6.1 Bash/Shell script review checklist
- 6.2 POSIX compatibility requirements
- 6.3 ShellCheck lints and fixes
- 6.4 Cross-platform considerations for macOS and Linux

## Quick Reference: Cross-Platform Testing
See [cross-platform-testing.md](references/cross-platform-testing.md):
- 7.1 Testing on multiple operating systems
- 7.2 CI matrix configuration for GitHub Actions
- 7.3 Platform-specific test skips and annotations
- 7.4 Using Docker for reproducible builds

## Decision Tree: PR Review Approach

```
START: New PR to review
  |
  v
[1] Run atlas_detect_pr_languages.py to identify languages
  |
  v
[2] For each detected language:
  |
  +---> Is it Python? ---> Read python-review-patterns.md, run ruff + mypy
  |
  +---> Is it JavaScript/TypeScript? ---> Read javascript-review-patterns.md, run ESLint
  |
  +---> Is it Rust? ---> Read rust-review-patterns.md, run cargo clippy
  |
  +---> Is it Go? ---> Read go-review-patterns.md, run go vet + staticcheck
  |
  +---> Is it Bash/Shell? ---> Read shell-review-patterns.md, run ShellCheck
  |
  v
[3] Check for cross-language interfaces:
  |
  +---> API contracts between services? ---> Verify schema compatibility
  |
  +---> FFI boundaries? ---> Check type mappings and safety
  |
  +---> Shared configuration? ---> Ensure consistency
  |
  v
[4] Check for platform-specific code:
  |
  +---> Multiple OS targets? ---> Read cross-platform-testing.md
  |
  v
[5] Run atlas_get_language_linters.py for each language to get linter commands
  |
  v
[6] Execute all linters and compile results
  |
  v
[7] Write review summary with findings per language
  |
  v
END
```

## Included Scripts

### atlas_detect_pr_languages.py
Detects programming languages in a PR's changed files.

**Usage**:
```bash
# Detect languages in PR #123
python scripts/atlas_detect_pr_languages.py --repo owner/repo --pr 123

# Detect languages in local diff
python scripts/atlas_detect_pr_languages.py --diff-file changes.diff
```

**Output**: JSON with language breakdown and file counts.

### atlas_get_language_linters.py
Returns recommended linters and commands for a given language.

**Usage**:
```bash
# Get linters for Python
python scripts/atlas_get_language_linters.py --language python

# Get linters for multiple languages
python scripts/atlas_get_language_linters.py --languages python,javascript,rust
```

**Output**: JSON with linter names, install commands, and run commands.

## Workflow Example

When reviewing a PR in a multilanguage repository:

```bash
# Step 1: Detect languages in the PR
python scripts/atlas_detect_pr_languages.py --repo myorg/myrepo --pr 456

# Example output:
# {
#   "languages": {
#     "python": {"files": 12, "lines_changed": 450},
#     "typescript": {"files": 5, "lines_changed": 200},
#     "bash": {"files": 2, "lines_changed": 50}
#   },
#   "primary_language": "python"
# }

# Step 2: Get linters for detected languages
python scripts/atlas_get_language_linters.py --languages python,typescript,bash

# Example output:
# {
#   "python": {
#     "linters": ["ruff", "mypy"],
#     "commands": {
#       "ruff": "ruff check .",
#       "mypy": "mypy --strict ."
#     }
#   },
#   ...
# }

# Step 3: Read the appropriate review patterns for each language
# Step 4: Run linters and compile results
# Step 5: Write comprehensive review
```

## Common Pitfalls

1. **Ignoring generated files**: Many repos have generated code (protobuf, OpenAPI). Identify and skip these.
2. **Over-linting vendored code**: Third-party vendored code should be excluded from linting.
3. **Missing cross-language impacts**: A Python change might break a TypeScript client consuming its API.
4. **Platform assumptions**: Code working on Linux might fail on macOS due to path handling.
5. **Different Python versions**: A repo might support Python 3.8-3.12 with different type hint syntax.

## Troubleshooting

### Problem: Language detection returns unexpected results
**Solution**: Check .gitattributes for linguist overrides. Some files may be marked with `linguist-language` or `linguist-detectable=false`.

### Problem: Linter fails to run
**Solution**: Ensure the linter is installed. Use atlas_get_language_linters.py to get install commands.

### Problem: Too many linting errors
**Solution**: For legacy codebases, consider using `--fix` flags where available (ruff --fix, eslint --fix) and reviewing the automated fixes.

### Problem: Cross-platform test failures
**Solution**: Read cross-platform-testing.md section 7.3 for platform-specific skip annotations.

## Checklist: Multilanguage PR Review

- [ ] Detect all languages in the PR using atlas_detect_pr_languages.py
- [ ] Read the review patterns document for each detected language
- [ ] Run appropriate linters for each language
- [ ] Check for cross-language interface changes
- [ ] Verify platform-specific code has appropriate guards
- [ ] Ensure tests exist for new functionality in each language
- [ ] Check CI configuration covers all affected languages
- [ ] Verify documentation is updated if public APIs changed
