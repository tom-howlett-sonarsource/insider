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

Use the SonarQube MCP server to analyze code quality:
- Check for bugs, code smells, and security vulnerabilities
- Review issues before creating PRs
- Ensure quality gate passes before merge
