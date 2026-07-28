---
name: cursor-ide-dev-agent
description: >-
  Coordinate manual Cursor IDE agent sessions when the primary agent cannot
  start Cursor CLI/tmux: create paste-ready task packets, define parallel
  session boundaries, tell the user which Cursor IDE sessions to open or
  continue, and review returned diffs/artifacts before checkpointing.
---

# Cursor IDE Dev Agent

Use this skill when implementation is delegated to **Cursor IDE agent sessions
started manually by the user**, especially when Cursor CLI, tmux, or headless
agent orchestration is unavailable.

Do not use this skill to start `agent` CLI sessions. For tmux/CLI delegation,
use `cursor-dev-agent` instead.

## Operating Model

- The primary agent owns task boundaries, architecture, review, verification,
  merge order, and commits.
- The user is the human bridge and decision maker: they open or continue Cursor
  IDE agent sessions, paste the primary agent's instructions, decide whether to
  pause/continue/start sessions, and ask the primary agent to review results.
- Do not ask the user to manually inspect diffs, run verification, summarize
  logs, or decide technical correctness unless a human judgment is genuinely
  needed. The primary agent should inspect files, run commands, review diffs,
  and produce correction prompts directly.
- Cursor IDE agents implement only the assigned task packet.
- Cursor IDE agents must not commit.
- Each session should produce a concise final report with changed files,
  verification commands, artifact paths, and blockers.
- Prefer reviewable task packets with enough execution depth to produce a
  meaningful deliverable. Tiny corrections are appropriate for fixing drift, but
  new implementation sessions should usually be larger than a one-line/test-only
  cleanup and should include a real code path, tests, artifacts or diagnostics,
  and a clear stop point.

## Preflight

Before asking the user to start or continue a session:

1. Inspect current status with `git status --short` and relevant diffs.
2. Identify the baseline state and any active task/session names.
3. Decide whether to continue an existing session or start a new one.
4. Make task boundaries non-overlapping for parallel work.
5. Name the hard stop point and required verification.
6. Include exact paths for allowed changes and output artifacts.
7. State forbidden actions explicitly.
8. State the execution order: which sessions can start immediately, which can
   run only as interface/fixture work, and which must wait for upstream output.

If two tasks touch the same core file, serialize them unless one is review-only
or plan-only.

## Dependency Planning

Before listing prompts, classify every proposed session:

- **Parallel now** — independent files/layers; can implement and verify without
  another session's final diff.
- **Parallel with stub/interface only** — can define interfaces, tests, docs, or
  smoke fixtures now, but must wait for upstream artifacts before final
  verification.
- **Blocked / serialize** — must wait because it edits the same core files or
  needs upstream behavior to be real.

Always tell the user:

1. Which sessions they should start or continue in Cursor IDE.
2. Which paste-ready command/prompt to send to each session.
3. Which session must wait and what artifact/review result unblocks it.
4. What the primary agent will review next.
5. Which user decision, if any, is needed.

Use this compact table before the prompts:

```text
Execution plan:
- Parallel now: <sessions>
- Parallel with interface-only work: <sessions>
- Must wait: <sessions>
- Review order: 1) <session> -> 2) <session> -> 3) <session>
- Dependency artifacts: <upstream artifact> feeds <downstream session>
- User action: paste <commands> into <sessions>; no manual diff/test review needed
```

If the user asks "can these run in parallel?", answer yes/no per session, not as
a single blanket answer.

Default to **now-only prompts**:

- Provide paste-ready instructions only for sessions the user should start or
  continue now.
- For blocked or future sessions, state only the dependency and unblock
  condition.
- Do not include a full future continuation prompt unless the user explicitly
  asks for queued instructions, a runbook, or "the next prompt too".
- After the upstream artifact is reviewed, generate the dependent continuation
  prompt then, using the actual accepted paths and findings.

## Task Size

For fresh implementation sessions, avoid under-scoped tasks that merely rename a
test, tweak one assertion, or make a cosmetic local change unless the user asked
for a narrow correction. A good IDE-agent task should normally give the session
enough runway to:

- implement or strengthen one coherent behavior;
- add or update focused tests for that behavior;
- regenerate or inspect the relevant artifact/manifest when applicable;
- report measurable before/after evidence;
- stop at a reviewable checkpoint before crossing into another session's scope.

For correction prompts, keep the task narrow and session-owned. For next-step
development prompts, make the task longer-running but bounded by files, invariants,
verification commands, and acceptance evidence.

## Session Instruction Format

When giving the user instructions, give only what they need to bridge into
Cursor IDE. Do not include internal review steps unless they must be pasted into
the IDE session.

Use this shape:

```text
在之前 <session-name> 的 Cursor IDE session，发出下面的指令：

<task prompt>
```

or:

```text
新开一个 <session-name> 的 Cursor IDE session，在 <repo/worktree> 中发出下面的指令：

<task prompt>
```

If a session depends on another task, say so directly:

```text
这个 session 可以先做接口和测试骨架；等 <upstream-session> 完成后再接真实输出复验。
```

For Cursor IDE `/loop` sessions, prefer a paste-ready command:

```text
/loop @<task-doc-path> 每 10 分钟 fallback
```

Clarify that `fallback` here is only the IDE loop tick/reassess instruction. It
does not permit code-level fallback routing, repair paths, degraded behavior, or
case-specific patches.

After giving paste-ready instructions, state what the primary agent will do after
the user reports completion, for example:

```text
完成或跑一段时间后告诉我；我会直接 review diff、跑验证、看 artifact，然后给你 accept/correction/next-task。
```

After every formal review of a Cursor IDE session, always close with a concrete
next step. Do not stop at accept/reject findings. State whether the reviewed
session should continue, whether a new session should be opened, which sessions
can run in parallel, which must wait, and what exact artifact or review result
unblocks the next dependent task. If the next action is clear, include a
paste-ready prompt for the user to send to Cursor IDE.

When a task must wait, do not provide a full implementation prompt unless the
user explicitly asks for queued instructions. Provide the blocker and the exact
artifact or review result that unblocks it.

## Prompt Template

Paste one complete prompt into the Cursor IDE agent:

```text
You are a Cursor IDE coding subagent. Do not commit.

Context:
- Repo/worktree: <absolute path>
- Baseline/review state: <commit or "current dirty tree">
- Primary agent will review your diff and run verification.
- Read first: AGENTS.md, <task docs>, <relevant SKILL.md/files>.

Task:
- <concrete goal>
- Hard stop at: <reviewable checkpoint>

Allowed changes:
- <paths>

Forbidden:
- No commits.
- No git reset --hard, checkout --, or destructive cleanup.
- No Wang-only/path-only/device-ID-only/fixed-count-only special cases unless explicitly requested.
- No fallback/degraded/repair/post-processing path as the main solution when the task requires construction-time correctness.
- Do not silently skip required cases.

Implementation requirements:
- <general rules and invariants>
- Failed cases must produce explicit diagnostics.
- Successful artifacts should remain in the requested output directory.

Verification:
- <commands to run>
- <artifact checks>

Final report format:
Summary
- changed files
- implemented behavior

Verification
- commands run
- pass/fail result
- artifacts generated

Design notes
- why this is general, not case-specific
- what was intentionally not done

Known issues / blockers
- concrete file/function/artifact references
```

## Parallel Task Rules

Parallel sessions are acceptable when:

- They own different files or layers.
- They can be reviewed independently.
- One session can proceed with interfaces/fixtures while another produces the
  upstream artifact.

Parallel sessions are not acceptable when:

- Both need to edit the same runner or core script.
- One task's correct design depends on unresolved upstream behavior.
- The only separation is artificial and review would require merging both at
  once.

When parallelizing, tell the user the merge/acceptance order.

If two sessions are both useful but one produces the real input for the other,
start them as:

- upstream session: full implementation prompt;
- downstream session: interface/contract/smoke prompt only, with a hard stop
  before consuming real upstream artifacts.

### Session Ownership

Treat each Cursor IDE session as owning only its assigned task packet and allowed
paths. When reviewing multiple sessions, attribute every finding to the session
that should fix it.

Do not send one combined correction prompt for multiple sessions unless the fix
is intentionally a single serialized task. Split feedback by session ownership
so each IDE agent receives only the changes it should make. This prevents agents
from editing each other's scope or reworking accepted behavior.

For each session-specific correction, state:

- the target session name;
- the exact files or layers it may touch;
- the files or layers it must not touch because they belong to another session;
- whether the correction can run now or must wait for another session's accepted
  diff.

If a bug crosses session boundaries, break it into separate prompts:

- one prompt for the session that owns the failing behavior;
- one prompt for the session that owns stale tests/docs/contracts;
- a final primary-agent review step that runs integrated verification after both
  are complete.

## Review Loop

After the user says a Cursor IDE session finished:

1. Inspect `git status --short`.
2. Review the actual diff, not only the session report.
3. Run the requested verification yourself.
4. Inspect regenerated artifacts.
5. Report findings first, ordered by severity.
6. Decide: accept, request correction in the same session, or start a new
   narrower session.

Do not ask the user to run these review steps. The user may report "done",
"review this", or "现在如何"; the primary agent should then perform the review
from the shared workspace.

Do not approve the next dependent task until required gates are verified.

### Mid-Run Review

If the user asks whether to review while IDE `/loop` sessions are still running,
explain the tradeoff and then perform the useful review level directly:

- **Lightweight patrol** — run now. Inspect status/diff stat, file-boundary
  violations, forbidden actions, obvious design drift, and focused tests. State
  that findings are a snapshot and may change while the session continues.
- **Formal review** — run after the session stops or the user pauses it. Use this
  for acceptance, merge order, checkpointing, and dependent-task approval.

Do not wait for a long-running loop to stop before correcting obvious drift. If
the current diff shows a high-confidence architectural or safety issue, give the
user a short correction prompt to paste into the same IDE session.

Keep the user-facing response action-oriented:

```text
我现在做轻量巡检；如果发现方向问题，我会给你一段直接贴回 <session> 的 correction。
```

### Correction Prompts

When a session is close but wrong, prefer continuing the same IDE session with a
targeted correction rather than starting a broad replacement task.

If the running session was started with `/loop @<task-doc> ...`, prefer updating
that same task document with a dated/session-owned `Active Correction` section
before asking the user to paste anything. In loop mode, the next tick should
discover the correction from the document automatically. Only provide a paste-back
prompt when the task document cannot be edited, the session was not started from
a document, or the user explicitly asks for text to paste.

When writing corrections into task documents:

- append the correction under a clearly named section near the end of the doc;
- keep it scoped to that session's ownership and allowed paths;
- state the problem, required general fix, tests/verification, and forbidden
  shortcuts;
- do not edit another session's task document with mixed responsibilities;
- mention in the user-facing reply which document was updated and that the
  existing `/loop` session can pick it up on the next tick.

If multiple sessions need corrections, write one paste-ready correction per
session. Do not mix unrelated session responsibilities in a single prompt. Keep
the user's bridge action clear: tell them exactly which prompt goes into which
IDE session.

Good correction prompts include:

- the exact wrong behavior or file/function;
- the invariant being violated;
- the required general fix;
- one or two tests that must prove the fix;
- explicit forbidden shortcuts.

Keep correction prompts paste-ready:

```text
Correction for <session-name>:
- Problem: <file:function/line behavior>
- Required fix: <general contract>
- Tests: <focused assertions>
- Forbidden: <shortcuts to avoid>
```

Tell the user where to paste it:

```text
把下面这段贴到原来的 <session-name> Cursor IDE session 里即可。
```

### Evidence Integrity

When reviewing diagnostics, distinguish evidence strength:

- **Hard evidence**: generated from route requests, explicit IR/model objects,
  renderer-owned metadata, validators, or deterministic manifests.
- **Review evidence**: generated from visual/SVG heuristics, inferred geometry,
  screenshots, or human-inspection aids.

Do not let an IDE agent promote review evidence into a hard gate finding without
making the evidence source explicit. If a probe is heuristic or inferred from
SVG, it may be useful as a visual diagnostic, but it should not be labeled as a
hard-constraint failure unless the task explicitly accepts that evidence source.

When a manifest contains both product/gate status and hard diagnostics, verify
the semantics are unambiguous. For example, it can be valid for a visual gate to
pass while hard diagnostics are still partial, but the manifest must clearly say
which constraints were evaluated and which were not.

## Cleanup Notes

If sessions wrote scratch artifacts, keep useful logs/reports until review is
complete. Ask before deleting user-created worktrees or unrelated scratch
outputs.
