# SonarQube Issues Log

This file tracks all SonarQube issues found during development, the MCP method used to detect them, and how many attempts were needed to fix them.

## Summary

| Date | File | Rule | Severity | Attempts to Fix |
|------|------|------|----------|-----------------|
| 2026-01-31 | app/main.py | S1192 | CRITICAL | 1 |
| 2026-01-31 | tests/test_database.py | S1192 | CRITICAL | 1 |
| 2026-01-31 | tests/test_api_insights.py | S1192 | CRITICAL | 1 |
| 2026-01-31 | app/dependencies.py | S7503 | MINOR | 1 |

**Total Issues Found:** 4
**Total Fix Attempts:** 4
**MCP Method Used:** `mcp__sonarqube__analyze_code_snippet`

---

## Detailed Issue Log

### Issue #1: Duplicated String Literal in main.py

- **Date:** 2026-01-31
- **File:** `prototypes/python-fastapi/app/main.py`
- **MCP Method:** `mcp__sonarqube__analyze_code_snippet`
- **Rule:** `S1192` - Define a constant instead of duplicating this literal
- **Severity:** CRITICAL
- **Impact:** MAINTAINABILITY=HIGH
- **Message:** Define a constant instead of duplicating this literal "Insight not found" 4 times.
- **Attempts to Fix:** 1
- **Fix:** Extracted to constant `INSIGHT_NOT_FOUND = "Insight not found"`

---

### Issue #2: Duplicated String Literal in test_database.py

- **Date:** 2026-01-31
- **File:** `prototypes/python-fastapi/tests/test_database.py`
- **MCP Method:** `mcp__sonarqube__analyze_code_snippet`
- **Rule:** `S1192` - Define a constant instead of duplicating this literal
- **Severity:** CRITICAL
- **Impact:** MAINTAINABILITY=HIGH
- **Message:** Define a constant instead of duplicating this literal "Test Insight" 6 times.
- **Attempts to Fix:** 1
- **Fix:** Extracted to constants `TEST_INSIGHT_TITLE` and `TEST_DESCRIPTION`

---

### Issue #3: Duplicated String Literals in test_api_insights.py

- **Date:** 2026-01-31
- **File:** `prototypes/python-fastapi/tests/test_api_insights.py`
- **MCP Method:** `mcp__sonarqube__analyze_code_snippet`
- **Rule:** `S1192` - Define a constant instead of duplicating this literal
- **Severity:** CRITICAL
- **Impact:** MAINTAINABILITY=HIGH
- **Messages:**
  - Define a constant instead of duplicating this literal "/api/v1/insights" 11 times.
  - Define a constant instead of duplicating this literal "Some description" 3 times.
  - Define a constant instead of duplicating this literal "Test insight" 4 times.
- **Attempts to Fix:** 1
- **Fix:** Extracted to constants:
  - `INSIGHTS_ENDPOINT = "/api/v1/insights"`
  - `TEST_INSIGHT_TITLE = "Test insight"`
  - `TEST_DESCRIPTION = "Test description"`
  - `SOME_DESCRIPTION = "Some description"`

---

### Issue #4: Unnecessary async keyword in dependencies.py

- **Date:** 2026-01-31
- **File:** `prototypes/python-fastapi/app/dependencies.py`
- **MCP Method:** `mcp__sonarqube__analyze_code_snippet`
- **Rule:** `S7503` - Use asynchronous features in this function or remove the `async` keyword
- **Severity:** MINOR
- **Impact:** RELIABILITY=LOW, MAINTAINABILITY=MEDIUM
- **Message:** Use asynchronous features in this function or remove the `async` keyword.
- **Attempts to Fix:** 1
- **Fix:** Removed `async` keyword from `get_current_user` function since it had no `await` calls

---

## Notes

- All issues were detected using the `mcp__sonarqube__analyze_code_snippet` MCP tool before committing code
- The workflow is: write code → analyze with SonarQube MCP → fix issues → commit
- Most common issue type: S1192 (duplicated string literals) - resolved by extracting constants
