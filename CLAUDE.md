# Insider - Project Guidelines

## Development Approach

### Test-First Development (TDD)
All new code must follow test-first development:
1. Write a failing test first
2. Write the minimum code to make it pass
3. Refactor while keeping tests green

Never write implementation code without a corresponding test.

### Code Quality
- All code is analyzed by SonarCloud via the SonarQube MCP
- Use the SonarQube MCP to check for issues before committing
- PRs must pass quality gates before merge
- Address security hotspots immediately

### Git Workflow

**IMPORTANT: Never commit directly to main.** Always use feature branches. If I give other instructions to do otherwise then revert back to feature branches afterwards

1. Create a feature branch: `git checkout -b feature/<name>`
2. Make commits on the feature branch
3. Push and create a PR
4. Merge only after all checks pass

### PR Workflow

**IMPORTANT: Always use the `/pr` skill for PRs.** Never create PRs manually with `gh pr create` — the `/pr` skill handles the full lifecycle: create, monitor CI checks, fix failures, and merge (with user permission). Manually creating PRs skips CI monitoring and merge steps.

## Tech Stack

### Python Prototype (FastAPI)
- Framework: FastAPI
- Database: SQLite (initial)
- Testing: pytest

## Commands

```bash
# Run tests (from prototypes/python-fastapi/)
pytest

# Run with coverage
pytest --cov
```

## Code Analysis

Use the `/analyze` skill before every commit to run SonarQube analysis on modified files.

- All SonarQube issues are tracked in `docs/sonarqube-issues-log.md`
- PRs must pass quality gates before merge

### Common Patterns to Avoid (Learned from Issues Log)

**S1192 - Duplicated String Literals (CRITICAL)**
- Extract any string used 3+ times into a constant
- Common offenders: error messages, API endpoints, test data
- Fix: Define constants at top of file (e.g., `INSIGHT_NOT_FOUND = "Insight not found"`)

**S7503 - Async Without Await (MINOR)**
- Only use `async def` when the function contains `await` calls
- If no async operations, use regular `def`

**When writing new code, proactively:**
1. Define constants for repeated strings before duplicating them
2. In tests: create constants for endpoints, test titles, descriptions
3. Check if a function actually needs `async` before adding it
