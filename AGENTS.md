# Agents

This repo follows strict workflow rules. Agents must comply with the project guidelines and skills.

## Core Rules
- Use TDD: write a failing test first, then the minimum implementation, then refactor. Coverage for any change must be > 80%.
- Never commit directly to `main`. Work on a feature branch.
- Before completing any task that writes code and always before a commit, run `/analyze`.
- Never call SonarQube MCP tools directly for analysis. The `/analyze` skill handles analysis, rule lookup, fixes, and logging to `docs/sonarqube-issues-log.md`.
- Always use `/pr` to push and create PRs. Do not use `gh pr create` directly.

## PR Skill
Use the `pr` skill to handle the full PR lifecycle:
- Push the feature branch.
- Create the PR.
- Monitor CI in the background.
- Ask for explicit permission before merging.
- After merge, check the SonarQube quality gate.
