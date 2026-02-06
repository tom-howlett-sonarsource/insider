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

## Instructions

If `$ARGUMENTS` is provided, analyze only that file. Otherwise, analyze all modified/staged/untracked source files (ignore `.venv/`, `__pycache__/`, etc.).

For each source file:

1. **Read the file** using the Read tool
2. **Run analysis** using `mcp__sonarqube-a3s__run_advanced_code_analysis` with:
   - `projectKey`: `tom-howlett-sonarsource_insider`
   - `filePath`: project-relative path (e.g., `prototypes/python-fastapi/app/main.py`)
   - `fileContent`: the full file contents
   - `branchName`: current branch name
3. **Report findings** grouped by severity (CRITICAL > HIGH > MEDIUM > LOW > INFO)
4. **Fix CRITICAL and HIGH issues** immediately
5. **Re-analyze** fixed files to confirm the fix worked

## After fixing issues

When you find and fix a SonarQube issue, log it in `docs/sonarqube-issues-log.md`:
1. Add an entry to the summary table with date, file, rule, severity, and attempts to fix
2. Add a detailed log entry with:
   - Date and file path
   - MCP method used (`mcp__sonarqube-a3s__run_advanced_code_analysis`)
   - Rule ID, description, severity, and the exact SonarQube message
   - Number of attempts to fix and how it was resolved
3. Update the totals at the top of the file
4. If this is a new rule or recurring pattern, add it to the "Common Patterns to Avoid" section in CLAUDE.md

## Common Patterns to Avoid

Apply these proactively when fixing code:

- **S1192**: Extract any string used 3+ times into a constant
- **S7503**: Only use `async def` when the function contains `await` calls
- Define constants for repeated strings before duplicating them
- In tests: create constants for endpoints, test titles, descriptions
