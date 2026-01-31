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

### Before Every Commit

**IMPORTANT:** Always analyze code with SonarQube MCP before committing:

1. Use `mcp__sonarqube__analyze_code_snippet` to check each modified Python file
2. Fix any issues found (especially CRITICAL and HIGH severity)
3. Re-analyze to confirm fixes
4. Only then proceed with commit

Example usage:
```
mcp__sonarqube__analyze_code_snippet(
    projectKey="tom-howlett-sonarsource_insider",
    codeSnippet="<file contents>",
    language="python"
)
```

The tool returns issues with:
- `ruleKey`: The SonarQube rule that was violated
- `primaryMessage`: Description of the issue
- `severity`: CRITICAL, HIGH, MEDIUM, LOW, INFO
- `textRange`: Location of the issue in the code
