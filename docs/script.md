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

## Beat 2 — The Workflow Contract `[2 min]`

**SCREEN:** Switch to terminal. Open `CLAUDE.md`.

```
cat CLAUDE.md
```
*(or open in VS Code right pane)*

**POINT TO line 20:**
> *"Before completing a task that changes or writes code and always before a commit use `/analyze`"*

**SAY:**
> "Every project has a CLAUDE.md — the rules of engagement for this agent. Ours makes one thing non-negotiable: before any commit, run `/analyze`. The agent can't skip it."

**SCREEN:** Open `.claude/skills/analyze/SKILL.md`

**POINT TO the `allowed-tools` line:**
> *`allowed-tools: Read, Glob, Grep, Bash(git diff *), Bash(git status *)`*

**SAY:**
> "This is the skill definition. Notice the tool permissions: it can read files and run git diffs. It can't write to GitHub. Each skill has explicit, narrow permissions — this is how you keep an agent trustworthy."

> "When `/analyze` runs, it reads every modified file, sends each one to A3S with the project key and branch name, and then — importantly — looks up the rule rationale before applying any fix. Not blindly suppressing. Understanding."

**PAUSE:** Let that land. Then:

> "Let's see it in action."

---

## Beat 3 — The Task `[1 min]`

**SCREEN:** Switch right pane to `docs/tasks/analytics-export-endpoints.md`. Scroll to show structure.

**SAY:**
> "Here's the task. We're adding two endpoints to a FastAPI prototype: an analytics summary, and a CSV export with a webhook notification. Real-world feature work."

> "The spec says TDD: tests first, minimum implementation, then analyse before committing. Let's run it."

**ACTION:** Type in the terminal:

```
Implement the task described in docs/tasks/analytics-export-endpoints.md
```

**SAY** (as Claude begins):
> "While this runs, watch the right pane — you can follow along with the spec as Claude works through it. I'll call out the key moments."

---

## Beat 4 — Red Phase `[~2 min — narrate as it runs]`

**SCREEN:** Terminal left (Claude Code), task spec right

**LOOK FOR:** Claude writing to `tests/test_api_insights.py` first — before any implementation files.

**SAY** (point to the test file being written):
> "Tests first. This is TDD in practice — Claude is writing the failing tests before a single line of implementation exists."

**LOOK FOR:** Test run output. You should see something like:

```
FAILED tests/test_api_insights.py::TestAnalyticsInsights::test_analytics_empty_database
FAILED tests/test_api_insights.py::TestExportInsights::test_export_returns_count
...
5 failed, 1 passed
```

**PAUSE** and point at the failures:

> "That's the red phase. Those failures are *correct* — there's no implementation yet. This proves the tests are actually testing something, not just rubber-stamping code that already works."

---

## Beat 5 — Green Phase `[~2 min — narrate as it runs]`

**SCREEN:** Terminal (Claude writing implementation files)

**SAY** (as implementation is written):
> "Now the minimum code to make those tests pass. Schemas, repository methods, two new endpoints — one analytics aggregate, one CSV export."

**LOOK FOR:** Test run output — the green moment:

```
30 passed in X.XXs
```

**PAUSE.** Let it sit for a beat. Then:

**SAY:**
> "Thirty tests. All green. Coverage above 80%."

> "Most developers would commit right here."

*(beat)*

> "Let's not."

---

## Beat 6 — The Analysis `[~2 min]` ← **Main Event Begins**

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

## Beat 7 — The Finding `[1 min]` ← **Climax**

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

## Beat 8 — The Rule `[1.5 min]`

**SCREEN:** Watch Claude call `show_rule`

**SAY:**
> "Before fixing anything, Claude looks up the rule. Not to find a patch — to understand *why* it matters."

**LOOK FOR** key phrases in the rule output as it appears. Read them:

> *"The event loop is completely blocked until the file I/O operation completes. No other coroutines can run during this time."*

**SAY:**
> "In production at load — ten concurrent requests, a hundred — every one of them stalls while that one file write completes. That's the kind of issue that looks fine in testing and causes intermittent timeouts in production."

> "SonarQube's rule library is backed by years of research into real-world defects. The rule recommends `anyio.open_file()` — which is already a dependency in this project."

---

## Beat 9 — The Fix `[1 min]`

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

## Beat 10 — The Full Loop `[2 min]` *(run if time allows)*

**ACTION:** After Claude commits, watch it type `/pr`

**SAY:**
> "Now the `/pr` skill takes over."

**LOOK FOR:** PR being created in the terminal output.

**SAY:**
> "It pushes the branch, creates the PR, and starts watching the CI checks in the background. If the SonarQube quality gate finds something we missed — a cross-file issue, a taint flow that spans multiple modules — the skill will catch it, fix it, and re-push. Automatically."

**OPTIONAL — switch to browser (SonarQube Cloud project):**
> "This is where you'd see the quality gate status update as CI runs. Pass or fail, the agent handles it."

---

## Beat 11 — Wrap-up `[1 min]`

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
| 1 · Problem | Whiteboard / table | 2 min |
| 2 · Contract | `CLAUDE.md` + skill file | 2 min |
| 3 · Task start | Task spec + terminal prompt | 1 min |
| 4 · Red phase | Terminal — failing tests | ~2 min |
| 5 · Green phase | Terminal — 30 passed | ~2 min |
| 6 · Analysis | Terminal — 4 parallel A3S calls | ~2 min |
| 7 · Finding | Terminal — issue + severity | 1 min |
| 8 · Rule | Terminal — rule explanation | 1.5 min |
| 9 · Fix | Terminal — before/after + re-analysis | 1 min |
| 10 · PR loop | Terminal + browser (optional) | 2 min |
| 11 · Wrap-up | Slide or blank | 1 min |
| **Total** | | **~18–20 min** |

---

## Directing Notes

**Pauses that must happen:**
- After red phase output — let the failures sit on screen for 3 seconds before continuing
- After "most developers would commit here" — full beat of silence before "let's not"
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
