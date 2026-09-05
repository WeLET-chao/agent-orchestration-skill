---
name: external-dev-agent
description: Delegate and supervise implementation or review work through external agent CLIs such as Cursor, DeepSeek Harness/dsh, agy, Claude, OpenCode, or Copilot using task packets, isolated worktrees, tmux, audit artifacts, and primary-agent review.
---

# External Dev Agent

Use this skill when an external CLI agent should implement or review work while
the primary agent retains architecture ownership, verification, commits, and
integration.

This skill governs **development delegation**. It does not define application
runtime adapters that invoke models inside a product or experiment.

## Operating Model

- The primary agent defines the objective, owning repository, technical route,
  task boundary, evidence, and acceptance criteria.
- The external agent works only in its assigned task worktree and does not
  commit or push.
- Every non-trivial task is driven by a checked task packet in the worktree.
  The session receives a short bootstrap instruction to read and execute that
  document; do not paste an evolving specification through many chat turns.
- The primary agent reviews the actual diff and artifacts, runs verification,
  requests bounded corrections, and creates accepted commits.
- Provider differences are profiles, not separate development workflows.

## Provider Selection

Choose a provider deliberately. Smoke-test the selected CLI before assigning a
long task, and do not silently replace a requested provider.

| Provider | Typical use | Required reference |
| --- | --- | --- |
| Cursor `agent` | General interactive implementation | [references/cursor.md](references/cursor.md) |
| DeepSeek Harness `dsh` | Long interactive implementation or bounded review | [references/dsh.md](references/dsh.md) |
| Antigravity `agy` | Gemini implementation/review, including visual work | [references/agy.md](references/agy.md) |
| Claude, OpenCode, Copilot | Bounded implementation or review | [references/other-clis.md](references/other-clis.md) |

Read only the selected provider reference. For tasks spanning multiple
providers, read each applicable profile and keep their worktrees separate.

## Preflight

Before delegation:

1. Identify the actual project/workstream and owning repository.
2. Ensure the repository has a reviewed checkpoint commit.
3. Inspect `git status --short`, `git worktree list`, and `tmux list-sessions`.
   Do not remove user-created, unrelated, active, or unreviewed worktrees.
4. Review completed diffs before launching new work that edits the same owner
   files.
5. Classify candidate tasks:
   - `parallel-safe`: independent files and acceptance evidence;
   - `review-first`: an existing diff must be accepted or rejected;
   - `serial-after-review`: depends on an accepted upstream artifact;
   - `plan-only`: no implementation authority or environment is available.
6. For externally defined behavior, record the normative source and version,
   real verification environment, and a negative conformance check when
   practical. Local examples are corroborating evidence, not authority.
7. Create one branch/worktree per implementation task. Multiple agents must
   never edit the same worktree.
8. Create the task packet described in
   [references/task-packet.md](references/task-packet.md). Name a concrete hard
   stop and reviewable outputs.
9. Create task-local logs and artifact directories, normally:
   `.scratch/agent_logs/<task>/` and `.scratch/agent_artifacts/<task>/`.

## Start And Submit

Start the selected provider from the assigned worktree in a deterministically
named tmux session. Use the command in its provider reference.

Wait until the provider input prompt is visible. Submit a short instruction:

```text
Read .scratch/agent_prompts/<task>.md and execute it completely.
Do not commit or push. Stop at the task packet's hard stop.
```

Send the text and Enter separately. Confirm observable model/tool activity;
text visible in an input box is not evidence that the turn started.

Attach a task-local pane log. Do not use `/tmp` as the durable location for
reviewable evidence. Temporary process files must be moved into the task
worktree before reporting.

## Supervision

- Let an actively working session continue. Do not inject repeated status
  prompts merely because a task is long.
- Inspect observable pane state, worktree changes, test logs, and artifacts at
  reasonable intervals.
- If a session remains in repeated planning after it has enough evidence and a
  concrete design, send one bounded steering instruction to begin the edits and
  remain within the task packet. Do not rewrite the task interactively.
- If a provider reports quota/authentication/eligibility failure, preserve the
  evidence and classify it as an external environment issue. Resume or switch
  providers only when authorized, with provider identity recorded.
- A scheduling loop is only a scheduling mechanism. It must not introduce
  degraded technical behavior, fallback algorithms, or invented artifacts.

## Failure Diagnosis

Before assigning a correction for a repeated failure, real-case failure,
runtime explosion, or cross-repository defect:

1. Preserve the smallest real reproducer, command, typed failure, logs, diff,
   and generated artifacts.
2. Distinguish task/session error, harness enforcement gap, skill/task-packet
   gap, architecture/contract gap, external environment issue, and valid but
   poor domain result.
3. Identify the owning layer and falsifiable root-cause hypotheses.
4. Reject budget increases, retries, fallback, or case-specific heuristics
   unless evidence identifies them as the real correction.
5. Record durable contract or architecture changes in the owning repository.

Continue the same session only for a local defect whose task premise and
context remain valid. Start from a clean reviewed checkpoint with a rewritten
task packet when the premise, authority, ownership, or architecture changes.

## Review And Integration

When a provider reports completion or presents a reviewable diff:

1. Read its final report and audit log.
2. Inspect `git status --short`, `git diff --stat`, and the actual diff.
3. Trace external mappings and protocol assumptions to their normative source.
4. Run focused tests yourself, including a red-capable negative check where
   practical. Never trust a piped command whose recorded status came from
   `tee`; preserve each failing log before retrying.
5. Inspect real generated artifacts. A fixture or smoke test proves tooling,
   not representative application quality.
6. For visual work, inspect rendered output and require a visible improvement,
   not only passing tests.
7. Apply corrections at every responsible layer. If the task exposed a
   reusable delegation gap, update this skill or its provider profile as well
   as the active task.
8. Commit only after primary-agent review and verification.
9. Remove completed worktrees and sessions only after their diff is accepted,
   intentionally discarded, or preserved elsewhere. Keep required audit
   artifacts.

Report outcomes in practical domain language: what works, what remains invalid
or blocked, distance to the real goal, and concrete evidence. Distinguish code
existence, unit tests, integrated real dependencies, representative valid
outputs, and final objective achievement.
