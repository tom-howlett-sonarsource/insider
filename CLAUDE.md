# Insider - Project Guidelines

## Development Approach

### Test-First Development (TDD)
All new code must follow test-first development:
1. Write a failing test first
2. Write the minimum code to make it pass
3. Refactor while keeping tests green
4. Ensure Code Coverage of any change > 80%

Never write implementation code without a corresponding test.

### Git Workflow

**IMPORTANT: Never commit directly to main.** Always use feature branches. If I give other instructions to do otherwise then revert back to feature branches afterwards.

1. Create a feature branch: `git checkout -b feature/<name>`
2. Make commits on the feature branch
3. **Before completing a task that changes or writes code and always before a commit use `/analyze`** Never call SonarQube MCP tools directly for analysis — the skill handles analysis, rule lookup, fixes, and logging to `docs/sonarqube-issues-log.md` automatically.
4. **Always use `/pr` to push and create PRs.** Never use `gh pr create` directly — the skill handles the full lifecycle: create, monitor CI checks, fix failures, and merge (with user permission).


