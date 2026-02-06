---
name: analyze
description: Run SonarQube code analysis on modified files before committing. Use this before any git commit to catch bugs, code smells, and security vulnerabilities.
argument-hint: [file-path (optional)]
allowed-tools: Read, Glob, Grep, Bash(git diff *), Bash(git status *)
---

# SonarQube Code Analysis

Analyze modified code with SonarQube before committing.

## Context

- Project key: `tom-howlett-sonarsource_insider`
- Issues log: `docs/sonarqube-issues-log.md`
- Current branch: !`git branch --show-current`

## Modified files

!`git diff --name-only HEAD 2>/dev/null; git diff --name-only --cached HEAD 2>/dev/null; git ls-files --others --exclude-standard`

## Step 1: Analyze

If `$ARGUMENTS` is provided, analyze only that file. Otherwise, analyze all modified/staged/untracked source files (ignore `.venv/`, `__pycache__/`, etc.).

For each source file:

1. **Read the file** using the Read tool
2. **Run analysis** using `mcp__sonarqube-a3s__run_advanced_code_analysis` with:
   - `projectKey`: `tom-howlett-sonarsource_insider`
   - `filePath`: project-relative path (e.g., `prototypes/python-fastapi/app/main.py`)
   - `fileContent`: the full file contents
   - `branchName`: current branch name
3. **Report findings** grouped by severity (CRITICAL > HIGH > MEDIUM > LOW > INFO)

## Step 2: Fix issues

For each issue found:

1. **Look up the rule** using `mcp__sonarqube-a3s__show_rule` with the rule key (e.g., `python:S1192`) to understand the rationale and recommended fix
2. **Check CLAUDE.md** — the "Common Patterns to Avoid" section may already have a known fix pattern for this rule
3. **Fix CRITICAL and HIGH issues** immediately, following the rule guidance
4. **Re-analyze** the file to confirm the fix doesn't introduce new issues

## Step 3: Log fixes

When an issue has been fixed, log it in `docs/sonarqube-issues-log.md`:

1. Add an entry to the summary table with date, file, rule, severity, and attempts to fix
2. Add a detailed log entry with:
   - Date and file path
   - MCP method used (`mcp__sonarqube-a3s__run_advanced_code_analysis`)
   - Rule ID, description, severity, and the exact SonarQube message
   - Number of attempts to fix and how it was resolved
3. Update the totals at the top of the file
4. If this is a new or recurring rule, add it to "Common Patterns to Avoid" in CLAUDE.md so future sessions avoid it proactively
