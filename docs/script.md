# Demo Script: A3S Advanced Analysis via MCP
### "Your agent wrote it. Did it write it right?"

**Duration:** 20 min
**Format:** Live terminal demo (Claude Code) + narration
**Key product moment:** `/analyze` → A3S finds a real async bug → rule-aware fix

---

## Pre-show Setup

Do this before anyone arrives. The goal is zero fumbling during the demo.

| What | How |
|------|-----|
| Terminal open | `cd ~/Documents/repos/insider`, branch `feature/analytics-export-task` |
| Font size | Increase to 18pt+ — the audience needs to read the terminal |
| Split view | Terminal left (70%), task spec open right (30%) in VS Code |
| Browser tab | SonarQube Cloud project `tom-howlett-sonarsource_insider` — Quality Gate screen |
| Verify clean | `git status` should show only `docs/script.md` as untracked |

**Run once before the demo:**
```
cd prototypes/python-fastapi && .venv/bin/pytest tests/ -q
```
Should show all passing (existing tests). Close that output before the audience arrives.

---

## Beat 1 — The Problem `[2 min]`

**SCREEN:** Blank terminal or switch to whiteboard/slide

**SAY:**
> "Most organisations want to use AI agents to ship faster. The fear is that speed comes at the cost of quality — that agents generate code that looks correct but isn't."

> "The obvious answer: run static analysis. But here's the problem."

**SHOW:** Switch to browser, navigate to `a3s/knowledge-base/concepts.md`, or draw this table on a whiteboard:

```
┌─────────────────────────┬─────────────────────────────────────────────────┐
│ Basic linter            │ No project context — misses 36% of issues,      │
│ (single-file analysis)  │ 75% of security vulnerabilities                 │
├─────────────────────────┼─────────────────────────────────────────────────┤
│ Full CI analysis        │ Takes minutes — too slow for an agent loop       │
└─────────────────────────┴─────────────────────────────────────────────────┘
```

**SAY:**
> "A linter that doesn't understand your project misses the issues that matter most. A full CI scan is too slow — agents can't wait minutes between iterations."

> "A3S solves this with a two-phase approach: collect context during CI, restore it on-demand. Same analysis precision as a full scan, in seconds."

**LOOK FOR:** Audience nodding or leaning in. This is the hook.

---

## Beat 2 — The MCP Connection `[1 min]`

**SCREEN:** Terminal

**SAY:**
> "Before I start the task — let me show you the SonarQube MCP is live. This isn't a mock. It's connected to a real SonarQube Cloud project right now."

**ACTION:** Type in the terminal:

```
/mcp
```

**LOOK FOR:** `sonarqube-a3s` listed as a connected server with a green status indicator.

**POINT at it:**
> "That's the A3S MCP server. Claude Code has it registered — so every tool call you're about to see, `run_advanced_code_analysis`, `show_rule` — those go directly to SonarQube Cloud. No wrapper, no middleware."

**ACTION:** To prove it's live, ask Claude:

```
Which SonarQube projects do I have access to?
```

**LOOK FOR:** The `search_my_sonarqube_projects` call and the response showing `tom-howlett-sonarsource_insider`.

**SAY:**
> "There's the project. Same one we'll be analysing in a moment."

---

## Beat 3 — Start the Task `[30 sec]`

**SCREEN:** Terminal (full screen, font 18pt+)

**SAY:**
> "Let me show you what this looks like end to end. I'm going to give the agent a real task and let it run."

**ACTION:** Type in the terminal:

```
Implement the task described in docs/tasks/analytics-export-endpoints.md
```

**SAY** (as Claude begins reading files):
> "It's reading the codebase — the existing endpoints, the test fixtures, the schemas. Building up context before writing a single line."

**WAIT** for Claude to hit PAUSE 1 — it will show a prompt: *"I've read the codebase and have a clear plan. Ready for me to start writing the schemas and tests?"*

**DO NOT CLICK YES YET.** Leave the question on screen.

---

## Beat 4 — The Contract (during PAUSE 1) `[3 min]`

**SCREEN:** Leave the PAUSE 1 prompt visible in terminal. Switch right pane to `docs/tasks/analytics-export-endpoints.md`.

**SAY:**
> "While it's waiting — let me show you what it's been given. Here's the task spec."

**POINT TO** the Objective section:
> "Two new API endpoints. An analytics summary, and a CSV export with a webhook notification. Real feature work — not a toy example."

**POINT TO** the TDD section at the top:
> "The spec mandates TDD: tests first, minimum implementation to pass, then analyse before committing."

**SCREEN:** Switch right pane to `CLAUDE.md` (or `cat CLAUDE.md` in a second terminal pane)

**POINT TO line 20:**
> *"Before completing a task that changes or writes code and always before a commit use `/analyze`"*

**SAY:**
> "Every project has a CLAUDE.md — the rules of engagement for this agent. Ours makes one thing non-negotiable: before any commit, run `/analyze`. The agent can't skip it."

**SCREEN:** Open `.claude/skills/analyze/SKILL.md` (or show the skills list)

**SAY:**
> "Skills are the mechanism. Each one is a scoped instruction file — this one tells the agent how to analyse code, look up rules, fix issues, and log them. It has explicit, narrow permissions — it can read files and run git diffs. It can't push to GitHub on its own."

> "When `/analyze` runs, it reads every modified file, sends each to A3S with the project key and branch name, then looks up the rule rationale before applying any fix. Not blindly suppressing. Understanding."

**PAUSE.** Let that land. Then turn back to the terminal.

**SAY:**
> "OK — let's let it run."

**ACTION:** Click **"Yes, start coding"** in the AskUserQuestion prompt.

---

## Beat 5 — Red Phase `[~2 min — narrate as it runs]`

**SCREEN:** Terminal left (Claude Code), task spec right

**LOOK FOR:** Claude writing to `tests/test_api_insights.py` first — before any implementation files.

**SAY** (point to the test file being written):
> "Tests first. This is TDD in practice — Claude is writing the failing tests before a single line of implementation exists."

**WAIT** for Claude to hit PAUSE 2 — it shows the failing test output and asks: *"Tests written and failing as expected — the TDD red state. Ready to implement?"*

**POINT at the failures before clicking:**

> "That's the red phase. Those failures are *correct* — there's no implementation yet. This proves the tests are actually testing something, not just rubber-stamping code that already works."

**ACTION:** Click **"Yes, implement now"**.

---

## Beat 6 — Green Phase `[~2 min — narrate as it runs]`

**SCREEN:** Terminal (Claude writing implementation files)

**SAY** (as implementation is written):
> "Now the minimum code to make those tests pass. Schemas, repository methods, two new endpoints — one analytics aggregate, one CSV export."

**WAIT** for Claude to hit PAUSE 3 — it shows the passing test output and asks: *"All tests green and coverage looks good. Ready to run Sonar analysis?"*

**PAUSE.** Point at the result before clicking. Then:

**SAY:**
> "Thirty tests. All green. Coverage above 80%."

> "Most developers would commit right here."

*(beat)*

> "Let's not."

**ACTION:** Click **"Yes, run /analyze"**.

---

## Beat 7 — The Analysis `[~2 min]` ← **Main Event Begins**

**SCREEN:** Full-screen terminal. Close the right pane if possible — this needs space.

**ACTION:** Type:

```
/analyze
```

**SAY** (as Claude reads files):
> "The analyze skill picks up every modified file from git diff and sends each one to A3S."

**LOOK FOR:** The parallel tool calls. You should see 4 `run_advanced_code_analysis` calls go out at once — one per modified file.

**POINT at the calls:**
> "Notice those are running simultaneously. Four files, four analysis calls, in parallel. Each one sent with the project key and the branch name — so A3S can restore the cached context from our last CI run."

> "This isn't sending code to a linter. A3S is spinning up the Python analyzer with full type information, dependency graphs, and symbol tables for this project. It knows this is FastAPI. It knows which functions are async."

**PAUSE** while results return. Let the audience wait. The tension is good.

---

## Beat 8 — The Finding `[1 min]` ← **Climax**

**LOOK FOR** in the results:

```
app/db_repository.py  — ✓ clean
app/schemas.py        — ✓ clean
tests/test_api_insights.py — ✓ clean
app/main.py           — ⚠ 1 issue
```

**PAUSE** on that result. Point at it.

**SAY:**
> "Three files clean. One issue, in main.py."

Read the message aloud slowly:

> *"Use an asynchronous file API instead of synchronous tempfile.NamedTemporaryFile() in this async function."*

> "MAJOR severity. RELIABILITY impact: HIGH."

> "Pause on this. A basic linter looking at this file would see valid Python — the code runs, the tests pass. But A3S knows this function is `async`. It knows it's a FastAPI endpoint handling concurrent requests. And it knows that synchronous file I/O in that context blocks the *entire event loop*."

---

## Beat 9 — The Rule `[1.5 min]`

**SCREEN:** Watch Claude call `show_rule`

**SAY:**
> "Before fixing anything, Claude looks up the rule. Not to find a patch — to understand *why* it matters."

**LOOK FOR** key phrases in the rule output as it appears. Read them:

> *"The event loop is completely blocked until the file I/O operation completes. No other coroutines can run during this time."*

**SAY:**
> "In production at load — ten concurrent requests, a hundred — every one of them stalls while that one file write completes. That's the kind of issue that looks fine in testing and causes intermittent timeouts in production."

> "SonarQube's rule library is backed by years of research into real-world defects. The rule recommends `anyio.open_file()` — which is already a dependency in this project."

---

## Beat 10 — The Fix `[1 min]`

**SCREEN:** Watch Claude apply the fix

**LOOK FOR:** The before/after. Specifically:
- `tempfile.NamedTemporaryFile` + `finally: os.unlink` → gone
- `io.StringIO()` buffer → replaces it

**SAY:**
> "The fix is actually simpler than the original code. No temp file, no finally block, no `os.unlink`. In-memory buffer — non-blocking, no disk I/O, and the CSV content was never returned in the response anyway."

**LOOK FOR:** Re-analysis result:

```json
{"issues": []}
```

**PAUSE.**

**SAY:**
> "Clean. And thirty tests still pass."

> "That's the loop: A3S finds a real bug, explains why it matters, applies the right fix, and confirms it's resolved — all before a single commit."

---

## Beat 11 — The Full Loop `[2 min]` *(run if time allows)*

**ACTION:** After Claude commits, watch it type `/pr`

**SAY:**
> "Now the `/pr` skill takes over."

**LOOK FOR:** PR being created in the terminal output.

**SAY:**
> "It pushes the branch, creates the PR, and starts watching the CI checks in the background. If the SonarQube quality gate finds something we missed — a cross-file issue, a taint flow that spans multiple modules — the skill will catch it, fix it, and re-push. Automatically."

**OPTIONAL — switch to browser (SonarQube Cloud project):**
> "This is where you'd see the quality gate status update as CI runs. Pass or fail, the agent handles it."

---

## Beat 12 — Wrap-up `[1 min]`

**SCREEN:** Blank terminal or slide

**SAY:**
> "Three things to take away."

1. **Context is what changes everything.** A linter sees one file. A3S sees your whole project — types, dependencies, async boundaries. That's why it caught something the tests couldn't.

2. **Speed makes the loop possible.** Under three seconds per file means agents can iterate — generate, check, fix — before the PR exists. Issues don't reach code review.

3. **It's baked in, not bolted on.** The analysis isn't optional. It's in the project rules, triggered automatically, with the fix logged and the pattern remembered. The agent gets better each session.

---

## Fallback: If `/analyze` returns clean

This can happen — the implementation might be perfect.

**SAY:**
> "Clean — which is the best outcome. But let me show you what A3S finding something looks like."

**ACTION:** Add a deliberate issue to `main.py`:

```python
# in export_insights, temporarily add:
tmp_path = None
with open("/tmp/demo.csv", "w") as f:
    f.write("id,title\n")
```

Run `/analyze` on that file only:
```
/analyze prototypes/python-fastapi/app/main.py
```

A3S should flag S7493 immediately. Walk through the finding and rule lookup. Then revert:
```
git checkout -- prototypes/python-fastapi/app/main.py
```

---

## Timing Reference

| Beat | What's on screen | Duration |
|------|-----------------|----------|
| 1 · Problem | Slide / whiteboard | 2 min |
| 2 · MCP connection | Terminal — `/mcp` + project list | 1 min |
| 3 · Start task | Terminal — Claude reading files | 30 sec |
| **⏸️ PAUSE 1** | AskUserQuestion prompt on screen | — |
| 4 · Contract | Task spec + `CLAUDE.md` + skill file (while paused) | 3 min |
| 5 · Red phase | Terminal — failing tests + PAUSE 2 prompt | ~2 min |
| 6 · Green phase | Terminal — 30 passed + PAUSE 3 prompt | ~2 min |
| 7 · Analysis | Terminal — 4 parallel A3S calls | ~2 min |
| 8 · Finding | Terminal — issue + severity | 1 min |
| 9 · Rule | Terminal — rule explanation | 1.5 min |
| 10 · Fix | Terminal — before/after + re-analysis | 1 min |
| 11 · PR loop | Terminal + browser (optional) | 2 min |
| 12 · Wrap-up | Slide or blank | 1 min |
| **Total** | | **~19–21 min** |

---

## Directing Notes

**Pauses that must happen:**
- **PAUSE 1** (Claude waiting for confirmation) — use this time fully for the CLAUDE.md/skills explanation; don't rush to click "Yes"
- **PAUSE 2** (after red phase) — let the failures sit on screen, read one aloud before clicking "Yes, implement now"
- **PAUSE 3** (after green phase) — full beat of silence after "most developers would commit here" before clicking "Yes, run /analyze"
- After the issue appears — read the message aloud, slowly, before explaining it
- After `{"issues": []}` — let the clean result breathe

**Where to point on screen:**
- Beat 2: The `allowed-tools` line in the skill — scope of permissions is a key point
- Beat 6: The 4 parallel tool calls appearing — this is visually distinctive and shows speed
- Beat 7: The severity label (`MAJOR`, `RELIABILITY — HIGH`) — make this the anchor of the explanation
- Beat 9: The deleted `finally` block — "no cleanup code needed" is satisfying to see gone

**What the audience is thinking at each beat:**
- Beat 5: "OK, it works, what's the point?"
- Beat 7: "Huh, the tests passed but there was still a bug"
- Beat 9: "The fix is actually simpler — that makes sense"
- End: "I want this in my workflow"
