---
name: pr
description: Create a PR, monitor CI checks, and merge when green. Use after committing to a feature branch to handle the full PR lifecycle.
argument-hint: [title (optional)]
allowed-tools: Bash(gh *), Bash(git push *), Bash(git branch *)
---

# PR Workflow

Handle the full pull request lifecycle: create, monitor, fix, and merge.

## Context

- Current branch: !`git branch --show-current`
- Remote tracking: !`git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no upstream"`
- Unpushed commits: !`git log @{u}..HEAD --oneline 2>/dev/null || git log --oneline -5`
- SonarQube project: `tom-howlett-sonarsource_insider`

## Instructions

**IMPORTANT: Never merge directly to main. This workflow is for feature branches only.**

### Step 1: Push and Create PR

1. Push the current branch: `git push -u origin HEAD`
2. Create a PR using `gh pr create`
   - If `$ARGUMENTS` is provided, use it as the PR title
   - Otherwise, derive a title from the branch name and recent commits
   - Write a description summarizing the changes

### Step 2: Monitor CI Checks

1. Get the PR number from the create output
2. Run `gh pr checks <pr-number> --watch` with `run_in_background: true`
3. **Tell the user** that checks are running in the background and they can continue working

### Step 3: Handle Results

When checks complete:

**If all checks pass:**
1. Inform the user
2. Ask if they want to merge (or merge if they've indicated to proceed)
3. Merge with `gh pr merge <pr-number> --merge`
4. After merge, check the SonarQube quality gate in the background:
   - Use `mcp__sonarqube-a3s__get_project_quality_gate_status` with `projectKey: tom-howlett-sonarsource_insider`
   - Alert the user if quality gate fails

**If checks fail:**
1. Investigate: `gh pr checks <pr-number>` to see which check failed
2. For SonarQube failures:
   - Use `mcp__sonarqube-a3s__search_sonar_issues_in_projects` to find the issues
   - Fix the issues
   - Log them in `docs/sonarqube-issues-log.md`
3. Commit and push fixes
4. Re-monitor checks: `gh pr checks <pr-number> --watch` with `run_in_background: true`
5. Repeat until all checks pass
