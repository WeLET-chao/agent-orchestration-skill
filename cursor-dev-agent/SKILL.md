---
name: cursor-dev-agent
description: Start and supervise Cursor's `agent` CLI as a coding subagent in tmux when implementation work should be delegated, with audit logs, yolo guardrails, fixed task prompts, and post-task review checkpoints.
---

# Cursor Dev Agent

Use this skill when Cursor should handle delegated implementation while a **primary agent** owns architecture, task boundaries, review, and checkpoint commits.

## Operating Model

- **Primary agent** — whoever invoked this skill and will review the result (Cursor, Claude Code, Codex, OpenCode, or the user). Not tied to one product.
- **Cursor subagent** — the `agent` CLI session in tmux that implements inside the assigned task package.

Responsibilities:

- The primary agent owns architecture direction, task boundaries, review, corrections, and checkpoint commits.
- Cursor owns implementation inside the assigned task package.
- Cursor must use the default Cursor agent auto model only. Do not pass model flags or ask it to switch models.
- Cursor may run in yolo mode, but it must not commit.
- Cursor output must be logged under a scratch/audit directory, normally `.scratch/cursor_logs/`.
- Task artifacts, rendered evidence, and primary-review conversions must be
  written inside the task's own worktree, normally under
  `.scratch/cursor_artifacts/<task>/`. Do not use `/tmp`, the main worktree, or
  another task worktree as the reviewable artifact location. A system temporary
  file may exist only during one command and must be copied or moved into the
  owning task worktree before inspection or reporting.
- Treat `/loop` fallback as a scheduling tick only; it is not technical fallback or degraded implementation.
- When multiple independent implementation tasks exist, prefer parallel Cursor sessions in separate git worktrees over serializing work in one session.
- When the user asks for status, next steps, or what can be assigned, the primary agent should proactively identify parallelizable work instead of waiting for the user to ask "what can run in parallel?"
- For visual generation work, each implementation iteration must produce a reviewable visual improvement and close at least one concrete visual/problem class. Do not accept iterations that only improve internal gates, tests, or diagnostics while the generated artifacts look unchanged.

## Preflight

Before starting a Cursor task:

1. Ensure there is an audit checkpoint commit before delegation.
2. Audit and clean previous Cursor delegation state before creating new work:
   - Run `git worktree list`, `tmux list-sessions`, and `git status --short`.
   - Stop stale or completed Cursor task and monitor sessions before starting a new batch.
   - Remove completed task worktrees with `git worktree remove` after their accepted diff has been reviewed, applied, committed, or intentionally discarded.
   - Do not remove active worktrees, unreviewed implementation work, read-only reports still needed for review, user-created worktrees, or unrelated external worktrees unless explicitly instructed.
   - Keep `.scratch/cursor_logs/`, `.scratch/cursor_reports/`, and task prompts as audit artifacts unless the user asks to clean scratch.
3. Confirm `git status --short`; note intentional untracked scratch files.
4. Run a parallelization assessment before writing prompts:
   - List candidate tasks that advance the main goal.
   - Mark each task as `parallel-safe`, `serial-after-review`, or `plan-only`.
   - Explain dependency edges in plain language, especially when tasks would edit the same files or rely on the same generated artifacts.
   - Prefer launching every genuinely independent `parallel-safe` task in its own worktree/session.
   - If representative or end-to-end acceptance depends on an upstream artifact
     that has not passed review, classify that acceptance as `serial-after-review`.
     A synthetic fixture may exercise an algorithm invariant, but it must be
     labeled synthetic and cannot substitute for the missing upstream artifact,
     satisfy the representative-case hard stop, or pass merely by proving its
     invented input infeasible.
   - Do not launch new implementation sessions when existing sessions already produced reviewable diffs that must be reviewed first.
5. Name a hard stop point for each task.
6. Run an authority-readiness check when behavior is defined outside the repository, such as by a file format, protocol, compiler, EDA tool, simulator, provider API, or pinned dependency:
   - Identify the normative source by exact document/API/source path and version or revision.
   - Confirm Cursor can access it and name an executable verification method.
   - Separate normative sources from local corroborating implementations and acceptance-only artifacts.
   - If the authority or real verification environment is unavailable, narrow the task to evidence collection or require an explicit `configuration_blocked` report. Do not ask Cursor to invent the missing semantics.
7. Prepare each task prompt with scope, allowed files, forbidden actions, verification, artifacts, report format, and the authority/evidence information above when applicable.
8. If the task depends on repo policy, require Cursor to read `AGENTS.md`, project context docs, relevant design docs/issues, and touched code entry points.

Restart Cursor from the checkpoint instead of continuing a polluted session if it confuses active code with legacy code, proposes fallback/repair as the main path when the project forbids it, rewrites unrelated files, edits tests to hide failures, or cannot summarize touched files and verification.

Also restart with a rewritten complete task packet when review reveals that the original task lacked a material source of truth, assigned the problem to the wrong architectural layer, or caused repeated implementation from an invalid premise. Do not accumulate follow-up prompts on top of a materially obsolete task definition.

## Authority and Evidence

For tasks whose correctness depends on externally defined semantics, the primary agent must make the evidence hierarchy explicit before implementation:

- **Normative** — the standard, grammar, real API/tool behavior, or pinned upstream source that defines the behavior.
- **Corroborating only** — a local adapter, bridge, example, or previous implementation that may agree with the authority but cannot define it.
- **Acceptance only** — real artifacts or domain cases used to verify the implementation; they must not be used to infer a mapping chosen to make those same cases pass.

Keep definition, implementation, and acceptance independent. Expected values in conformance tests must not be generated by the code path under test. When practical, include a negative test that changes one token, transform, field, or operation and proves the check fails. Use a neutral asymmetric calibration artifact when it can validate external transform semantics without relying on domain-specific labels or desired outputs.

An explicit, versioned table for standard tokens or API enums is contract data, not prohibited case-specific hardcoding, when it cites its authority and is validated independently. Branches keyed by corpus case names, desired terminal positions, or observed acceptance results remain prohibited.

For real external tools, record enough environment evidence to reproduce the check: executable and version, environment setup, relevant library/PDK/configuration, license or credential availability when applicable, verification command, and captured result. A mock, local reimplementation, or fixture does not prove real-tool semantics.

## Start Cursor

Use deterministic names that include the project and task:

```bash
tmux new -s <project>-cursor-task-a
```

Inside the session, start Cursor without model options:

```bash
agent --yolo --sandbox disabled
```

Do not add `--trust` in an interactive tmux session. Current Cursor CLI versions reject that combination with:

```text
--trust can only be used with --print/headless mode
```

Use `--trust` only for headless `agent --print ...` runs. For interactive tmux sessions, use `agent --yolo --sandbox disabled`.

In another shell, attach logging:

```bash
mkdir -p .scratch/cursor_logs
tmux pipe-pane -t <project>-cursor-task-a -o 'cat >> .scratch/cursor_logs/task-a-$(date +%Y%m%d-%H%M%S).log'
```

Paste the task prompt and explicitly submit it with Enter. In tmux this means sending the prompt text and then a separate `C-m`; Cursor can otherwise show `[Pasted text #1 +N lines]` without actually starting the task.

```bash
tmux send-keys -t <project>-cursor-task-a "$(cat .scratch/cursor_prompts/task-a.txt)" C-m
tmux send-keys -t <project>-cursor-task-a C-m
```

Confirm the pane state after submission. It should show `Working` or `Running`, not just `Pasted text`.

```bash
tmux capture-pane -t <project>-cursor-task-a -p | tail -80
```

## Parallel Sessions

Use parallel sessions when tasks are independent enough to review separately, such as one task for architecture planning, another for implementation, and another for artifact or conformance checks. Do not run multiple Cursor agents that edit the same worktree.

Default stance: before answering "next step" or starting a new Cursor batch, state the parallelization result:

- `Can run now` — independent tasks that should be launched in parallel.
- `Review first` — existing sessions with completed diffs or tasks blocked by unreviewed changes.
- `Serial later` — tasks that depend on an accepted checkpoint from another session.

This assessment should be actionable: include session names, worktree names, and the reason each task is parallel-safe or serial. The user should not need to prompt separately for parallel scheduling.

Create one branch/worktree per task from the same reviewed checkpoint:

```bash
git worktree add -b task-c-name ../<repo>-task-c <checkpoint>
git worktree add -b task-d-name ../<repo>-task-d <checkpoint>
git worktree add -b task-e-name ../<repo>-task-e <checkpoint>
```

Start one tmux session per worktree:

```bash
tmux new-session -d -s <project>-cursor-task-c -c ../<repo>-task-c 'agent --yolo --sandbox disabled'
tmux new-session -d -s <project>-cursor-task-d -c ../<repo>-task-d 'agent --yolo --sandbox disabled'
tmux new-session -d -s <project>-cursor-task-e -c ../<repo>-task-e 'agent --yolo --sandbox disabled'
```

Attach separate logs:

```bash
mkdir -p .scratch/cursor_logs
tmux pipe-pane -t <project>-cursor-task-c -o 'cat >> .scratch/cursor_logs/task-c-$(date +%Y%m%d-%H%M%S).log'
tmux pipe-pane -t <project>-cursor-task-d -o 'cat >> .scratch/cursor_logs/task-d-$(date +%Y%m%d-%H%M%S).log'
tmux pipe-pane -t <project>-cursor-task-e -o 'cat >> .scratch/cursor_logs/task-e-$(date +%Y%m%d-%H%M%S).log'
```

For long parallel runs, add a monitor session that records each pane tail and each worktree's git status/diff stat every 10 minutes. Keep the monitor log in `.scratch/cursor_logs/` and do not commit it.

Parallel task prompts must have non-overlapping ownership. If two tasks need the same file, either serialize them or make one task explicitly produce a plan only. Review and merge one worktree at a time; after accepting one checkpoint, rebase or recreate still-running worktrees before merging if their base is stale or conflicts with accepted architecture.

Before launching a new batch of parallel sessions, repeat the preflight cleanup audit. The expected steady state is: only the main worktree, active task worktrees, intentional external worktrees, and necessary non-Cursor services remain.

## Prompt Template

Paste a single `/loop` prompt into Cursor. Keep the task specific enough to review, even when it is a larger slice.

```text
/loop every 20 minutes:

Use the default Cursor agent auto model only. Do not switch models.

Context:
- Baseline checkpoint: <commit>
- You are a coding subagent. Do not commit.
- Primary agent will review your diff and create checkpoints.
- Read: AGENTS.md, project context docs, <relevant ADRs/design docs/issues>, <code entry points>.

Sources of truth (when external semantics are involved):
- Normative: <exact document/API/source path and version or revision>
- Corroborating only: <local adapters/examples that cannot define behavior>
- Acceptance only: <artifacts/cases that verify but must not determine the rule>
- Verification environment: <real tool, setup, command, and availability>
- If unavailable: report configuration_blocked at <hard stop>; do not infer semantics.

Task:
- <concrete goal>
- Hard stop at: <reviewable checkpoint>

Allowed changes:
- <paths>

Forbidden:
- No git reset --hard, checkout --, or destructive cleanup.
- No commits.
- No legacy import or restoration of legacy as the main path unless explicitly requested.
- No fallback/repair/post-processing as the main implementation path when the project requires construction-time correctness.
- No demo-only visual fixes unless the task is explicitly a demo-only artifact task.
- Do not silently skip required cases.

Implementation requirements:
- <requirements>
- Keep authoritative definition, implementation, and acceptance evidence independent.
- Do not derive expected behavior from the same implementation or acceptance artifact used to test it.
- Prefer parallel processing for independent cases where safe.
- Failed cases must produce explicit diagnostics; successful artifacts should remain.
- If any required case fails, final command/result must make that visible.

Verification:
- <test commands>
- <artifact commands>
- Write every reviewable artifact and any primary-review PNG/SVG conversion
  under this task worktree's `.scratch/cursor_artifacts/<task>/`; do not report
  `/tmp` paths as task evidence.
- For external contracts: cite the authority/version, run the real-tool or pinned-source conformance check, and include a negative check when practical.
- For visual artifact tasks: regenerate the target PNG/SVG or equivalent artifacts, report exact paths and mtimes, and identify at least one visible problem class that changed. If the artifact is visually unchanged, keep working or report the task as blocked rather than complete.

Final report format:
Summary
- changed files
- implemented behavior
- visual/problem class fixed in this iteration

Verification
- commands run
- pass/fail result
- artifacts regenerated, if any
- exact artifact paths, mtimes, and before/after visual evidence for visual tasks

Design notes
- how this advances the main architecture
- what was intentionally not done
- confirmation: no forbidden fallback/repair/legacy main-path dependency, when applicable

Known issues / blockers
- concrete file/function references
```

## Review Loop

After Cursor stops or reports completion:

1. Read its final report and tmux log.
2. Inspect `git status --short` and `git diff --stat`.
3. Review the actual diff, not only the summary.
4. For externally defined behavior, trace every new mapping, token table, transform, or protocol assumption to its declared normative source. Reject implementations that infer the rule from desired acceptance results or cite a local adapter as the authority.
5. Run focused tests yourself, including an available negative or mutation check that proves the conformance test can fail.
6. Inspect regenerated artifacts when relevant.
   Keep primary-review conversions, crops, screenshots, and annotated outputs
   in the same task worktree's `.scratch/cursor_artifacts/<task>/`, not `/tmp`
   or the main worktree.
7. For visual artifact tasks, verify that the artifact visibly improved and at least one problem class was actually fixed. Reject or correct results that only pass tests/gates while the image is unchanged or the claimed fix is not visible.
8. Classify each discovered problem before assigning a correction:
   - **Task/session error:** the governing contract and automated checks are sufficient, but this session did not follow them. Correct or restart the session.
   - **Harness enforcement gap:** the behavior is forbidden by the contract but invalid output passed automated validation. Fix the harness and add a regression test; a stronger prompt alone is insufficient.
   - **Skill or task-packet gap:** the expected behavior was not stated clearly enough for the delegated agent. Update the reusable skill or task template as well as the active session instruction.
   - **Architecture or contract gap:** the system has no authoritative rule or ownership boundary for the case. Update the governing design document/schema before implementing a local convention.
   - **External-tool or environment issue:** the implementation is correct but a provider, simulator, dependency, credential, or machine resource is unavailable or incompatible. Record the real blocker; do not disguise it with a fixture or fallback.
   - **Domain-result failure:** the tooling ran correctly but the produced circuit, document extraction, model, or other domain artifact is invalid or poor quality. Preserve the result as evidence and improve the generating/feedback process rather than patching the artifact silently.
9. Apply the correction at every responsible layer. A problem may require both a session correction and a reusable harness/skill fix. Do not treat these choices as mutually exclusive.
10. Apply a durable-correction gate before acceptance. For a harness, skill/task-packet, architecture, or contract gap, verify that the owning repository now contains the applicable contract/schema change and regression test. If the gap concerns delegation or review behavior, update the reusable skill/task template too. A chat message, continuation prompt, scratch task packet, or passing one-off command alone does not close the issue. Report the durable file and test paths in the review result.
11. Either provide the resulting correction task to the same session, restart from checkpoint if the context is polluted, launch a separate owner task when the defect belongs elsewhere, or make a checkpoint commit if the diff is acceptable.

Only commit after primary-agent review and verification.

When checking status for a running delegation, do not stop at a status-only update if a Cursor pane has reported completion, is waiting at `Add a follow-up`, or has produced a final report with changed files. In that case, proceed immediately into the review loop above: inspect the diff, run focused verification, and review artifacts as applicable. Report only a brief status first, then keep reviewing. Use a status-only response only when the Cursor task is still actively Working/Running or blocked before producing a reviewable diff.
