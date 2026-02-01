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

### SonarQube Issues Log

All SonarQube issues found during development are tracked in `docs/sonarqube-issues-log.md`.

**When you find and fix a SonarQube issue (either locally or from a blocked PR), you must:**
1. Add an entry to the summary table with date, file, rule, severity, and attempts to fix
2. Add a detailed log entry with:
   - Date and file path
   - MCP method used (e.g., `mcp__sonarqube__analyze_code_snippet`)
   - Rule ID and description
   - Severity and impact
   - The exact message from SonarQube
   - Number of attempts to fix
   - How the issue was resolved
   - If from a blocked PR: note the PR number and that it was caught by CI
3. Update the totals at the top of the file
4. **Reassess "Common Patterns to Avoid"**: If this is a new rule or a recurring pattern, add it to the "Common Patterns to Avoid" section below so future sessions can proactively prevent it

**Sources of SonarQube issues to track:**
- Local analysis using `mcp__sonarqube__analyze_code_snippet` before commits
- PR quality gate failures from SonarCloud CI
- Issues found via `mcp__sonarqube__search_sonar_issues_in_projects`

This log helps track code quality improvements and common issue patterns over time.

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
