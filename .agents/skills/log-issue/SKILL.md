---
name: log-issue
description: Log a SonarQube issue that was found and fixed to the issues log. Use after fixing a SonarQube issue from local analysis or a failed PR check.
argument-hint: [rule-id file-path]
allowed-tools: Read, Edit
---

# Log SonarQube Issue

Log a found-and-fixed SonarQube issue to `docs/sonarqube-issues-log.md`.

## Current log

!`head -16 docs/sonarqube-issues-log.md 2>/dev/null || echo "Log file not found"`

## Instructions

You need the following information (ask the user if not available from context):

- **File path** (project-relative)
- **Rule ID** (e.g., `S1192`)
- **Severity** (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- **SonarQube message** (the exact message from the analysis)
- **How it was fixed**
- **Number of attempts** to fix
- **Source**: local analysis (`mcp__sonarqube-a3s__run_advanced_code_analysis`) or PR failure (note the PR number)

## Step 1: Update the summary table

Add a row to the `## Summary` table:

```
| <date> | <file> | <rule> | <severity> | <attempts> |
```

## Step 2: Update the totals

Increment **Total Issues Found** and **Total Fix Attempts** counts.

## Step 3: Add a detailed entry

Add a new `### Issue #N` section under `## Detailed Issue Log` following this format:

```markdown
### Issue #N: <short description>

- **Date:** <YYYY-MM-DD>
- **File:** `<project-relative path>`
- **MCP Method:** `<method used to detect>`
- **Rule:** `<rule ID>` - <rule description>
- **Severity:** <severity>
- **Impact:** <impact from SonarQube>
- **Message:** <exact SonarQube message>
- **Attempts to Fix:** <number>
- **Fix:** <description of how it was resolved>
```

If the issue came from a PR failure, add:
- **Source:** PR #<number> (caught by CI)

## Step 4: Update CLAUDE.md patterns

If this is a **new rule** not already in the "Common Patterns to Avoid" section of CLAUDE.md, or a **recurring rule** that keeps appearing, add it there so future sessions avoid it proactively.
