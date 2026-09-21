---
name: external-dev-agent
description: Delegate and supervise implementation or review work through external agent CLIs such as Cursor, Codex DeepSeek (`codex -p deepseek`), agy, Claude, OpenCode, or Copilot using task packets, task-class isolation (impl worktree | review path | case workspace), tmux, audit artifacts, and primary-agent review. DeepSeek Harness/dsh is deprecated.
---

# External Dev Agent

Use this skill when an external CLI agent should implement or review work while
the primary agent retains architecture ownership, verification, commits, and
integration.

This skill governs **development delegation**. It does not define application
runtime adapters that invoke models inside a product or experiment.

## Operating Model

- The primary agent defines the objective, owning repository or case, technical
  route, task boundary, evidence, and acceptance criteria.
- Classify every task as **`impl` | `review` | `case-run`** before launch (see
  [Task classes](#task-classes-isolation)). The external agent works only in its
  assigned **task root** and does not commit or push.
- Every non-trivial task is driven by a checked task packet under the task root
  (normally `.scratch/agent_prompts/<task>.md`). The session receives a short
  bootstrap to read and execute that document; do not paste an evolving
  specification through many chat turns.
- The primary agent reviews the actual diff and artifacts, runs verification,
  requests bounded corrections, and creates accepted commits (**impl** only).
- Provider differences are profiles, not separate development workflows.

## Task classes (isolation)

| Class | When | Task root | Git worktree? | Write scope |
|-------|------|-----------|---------------|-------------|
| **impl** | Edit tracked **source** in a git repo | Branch + worktree | **Required** for a new parallel task | That worktree only |
| **review** | Read-only critique of plan/diff/docs/UI | Primary/skill path, pinned ref, or quiescent impl worktree | **Default no** | `.scratch/agent_artifacts/<task>/` + logs only |
| **case-run** | Produce/run a **case package** (e.g. paper reconstruction) | **Case workspace** (`reconstruction/<case>/` or `cases/<slug>/`) | **No** | Case workspace + case `.scratch/`; shared framework must stay clean |

Decision rule:

```text
Will the agent change tracked source in a git repo as the main deliverable?
  yes → impl (+ worktree)
  no  → Is the main deliverable a case package under a workspace path?
          yes → case-run
          no  → review
```

**If unsure whether tracked source may be modified: default to `impl` (create a
worktree) or halt for primary clarification. Never default an ambiguous
code-touching task to in-tree `review` or to `case-run`.**

### review rules

1. Prefer provider **hard** read-only / plan / ask modes (see provider profiles).
   Do not launch Cursor with `--yolo --sandbox disabled` for review.
2. Option A (in-tree): require `git status --porcelain` clean (or stash). Ensure
   `.scratch/` is gitignored, or place prompts/logs/artifacts under
   `<repo-parent>/.scratch/<repo-name>/<task>/`.
3. Option B (reuse an **impl** worktree cwd): only when that impl agent has
   reached its hard stop and its tmux is quiescent or killed. Multiple active
   agents must never share a worktree.
4. After review: verify no tracked files changed outside the write allowlist.

### case-run rules

1. Do **not** create `worktrees/<framework-repo>/<case-slug>/` merely to hold the
   case. Use the case workspace as cwd.
2. Shared skill/framework checkout is for **commands and docs**, not a writable
   sandbox. **`--add-dir` is not read-only** (Codex documents it as expanding
   the writable workspace). Do not treat `--add-dir` as a RO boundary.
3. Use one **shared frozen** venv (or host tools); forbid per-case `.venv` and
   forbid `pip install` mutating the shared env. Prefer
   `PYTHONDONTWRITEBYTECODE=1` / `PYTHONPYCACHEPREFIX` outside the framework tree.
4. Cap concurrent case-runs (suggest 2–4). Name tmux sessions deterministically
   (`recon-<slug>-<provider>-…`).
5. **Mandatory teardown:** fail the task if the shared framework is dirty:

```bash
git -C <shared-framework-root> diff --quiet
git -C <shared-framework-root> status --porcelain
# any output / non-zero → CRITICAL: case-run mutated shared framework
```

## Provider Selection

Choose a provider deliberately using this ordered preference unless the user
names a provider or model:

1. Prefer Cursor for general programming, backend, tests, automation, and
   ordinary documentation implementation.
2. Prefer Gemini via `agy` for UI/frontend visual design and multimodal visual
   review. For visual review, prefer a Gemini Flash model when the launcher
   supports an explicit compatible choice; do not silently switch a
   user-selected model.
3. Use another provider only when the user explicitly chooses it, the preferred
   provider lacks a required capability, or an evidenced availability failure
   blocks it. Record the reason; never silently substitute.

Do not make Gemini the default for non-visual backend work. Do not claim Cursor
or Gemini availability without checking it at dispatch time.

Establish that the selected CLI works before assigning a long task, using a
smoke test or reusable verification evidence as specified by its profile. Do
not silently replace a requested provider.

| Provider | Typical use | Required reference |
| --- | --- | --- |
| Cursor `agent` | Default for general interactive implementation | [references/cursor.md](references/cursor.md) |
| Codex `codex -p deepseek` | DeepSeek-family interactive implementation or bounded review (not the global default) | [references/codex-deepseek.md](references/codex-deepseek.md) |
| Antigravity `agy` | Default for Gemini UI/visual design and multimodal visual review; also other Gemini implementation/review | [references/agy.md](references/agy.md) |
| Claude, OpenCode, Copilot | Bounded implementation or review | [references/other-clis.md](references/other-clis.md) |
| DeepSeek Harness `dsh` (deprecated) | Legacy recovery only; do not start new DeepSeek tasks | [references/dsh.md](references/dsh.md) |

Read only the selected provider reference. For tasks spanning multiple
providers, keep separate task roots (separate worktrees for **impl**; separate
case workspaces for **case-run**).

## Preflight

Before delegation:

1. Identify the project/workstream and **task class** (`impl` | `review` |
   `case-run`).
2. For **impl** / **review** of a git repo: ensure a reviewed checkpoint commit
   when the task depends on a clean baseline.
3. Inspect `git status --short`, `git worktree list`, and `tmux list-sessions`.
   Do not remove user-created, unrelated, active, or unreviewed worktrees.
4. Review completed diffs before launching new work that edits the same owner
   files.
5. Classify scheduling:
   - `parallel-safe`: independent roots and acceptance evidence;
   - `review-first`: an existing diff must be accepted or rejected;
   - `serial-after-review`: depends on an accepted upstream artifact;
   - `plan-only`: no implementation authority or environment is available.
6. For externally defined behavior, record the normative source and version,
   real verification environment, and a negative conformance check when
   practical. Local examples are corroborating evidence, not authority.
7. Resolve the **task root**:
   - **impl:** repository worktree root =
     `<repository-parent>/worktrees/<repository-name>/<task-slug>` (or the
     repository-defined root). Do not create new task worktrees as siblings of
     the primary checkout or under a tool-specific global worktree directory.
     Confirm the path does not exist and the branch is not already checked out.
     Legacy worktrees: reuse until reviewed; do not auto-migrate.
   - **review:** primary/skill path or quiescent impl worktree; **do not** create
     a git worktree solely for the review. Apply [review rules](#review-rules).
   - **case-run:** existing or new **case workspace** directory; **do not** create
     a framework-repo git worktree for the case. Apply [case-run rules](#case-run-rules).
8. For a new **impl** task, create one branch/worktree. For continuation of the
   same task, reuse its root after inspecting diff, evidence, and live jobs.
   Multiple agents must never edit the same worktree or the same case workspace
   concurrently.
9. Create the task packet described in
   [references/task-packet.md](references/task-packet.md). Name task class, task
   root, hard stop, and reviewable outputs.
10. Create task-local logs and artifact directories under the task root (or external
    scratch), normally: `.scratch/agent_logs/<task>/` and
    `.scratch/agent_artifacts/<task>/`.

## Start And Submit

Start the selected provider from the assigned **task root** in a deterministically
named tmux session, or resume the existing task using its provider's supported
mechanism. Check for a live worker before launching another. Use the command in
its provider reference for the task class.

Wait until the provider input prompt is visible. Submit a short instruction:

```text
Read .scratch/agent_prompts/<task>.md and execute it completely.
Do not commit or push. Stop at the task packet's hard stop.
```

(If prompts live in an external scratch tree, use that absolute path in the
bootstrap.)

Send the text and Enter separately. Confirm observable model/tool activity;
text visible in an input box is not evidence that the turn started.

Attach a task-local pane log. Do not use `/tmp` as the durable location for
reviewable evidence. Temporary process files must be moved into the task root
before reporting.

Record the exact command, **task root** (and worktree path when impl), provider
session ID (when available), tmux pane or process/job ID, log path, expected
report/artifacts, and completion condition. Attach logging before submitting the
task so startup failures are captured. For headless runs, record the process
exit status; for interactive runs, task completion does not require the TUI
process to exit.

If this workstream is tracked on research-dashboard, follow
[references/research-dashboard-sessions.md](references/research-dashboard-sessions.md)
for register / supersede / complete. Otherwise skip session registry entirely;
still kill tmux and keep task-root artifacts after acceptance.

## Supervision

- Let an actively working session continue. Do not inject repeated status
  prompts merely because a task is long.
- Set the next inspection interval from the task's expected implementation and
  verification time instead of polling continuously. After a well-scoped task
  is submitted and observable work has started, wait about 10 minutes for a
  medium implementation task (for example, schedule the next review 600
  seconds later), and use a longer interval for clearly larger tasks. Shorten
  the interval only when the worker is near its stated completion point, a
  command is expected to finish soon, or there is evidence that primary-agent
  input may be required. Use an asynchronous wait or scheduler when available;
  do not occupy the foreground with a long blocking `sleep` that prevents user
  updates.
- Inspect observable pane state, task-root changes, test logs, and artifacts at
  reasonable intervals. Distinguish working, waiting for input, failed, ready
  for primary review, and accepted. An idle prompt or a provider's "done" message
  alone cannot establish acceptance. When a worker finishes its run and stops at
  the task packet's hard stop, it is `ready for primary review` (awaiting review);
  do not treat that state as accepted. Do not keep completed or abandoned worker
  tmux sessions running indefinitely under the guise of "audit preservation".
- If a session remains in repeated planning after it has enough evidence and a
  concrete design, send one bounded steering instruction to begin the edits and
  remain within the task packet. If it still repeats the plan, inspect whether
  input was submitted, a tool is pending, or the provider has failed before
  deciding to resume or restart. Do not accumulate identical steering prompts.
- If a provider reports quota/authentication/eligibility failure, preserve the
  evidence and classify it as an external environment issue. Resume or switch
  providers only when authorized, with provider identity recorded.
- A scheduling loop is only a scheduling mechanism. It must not introduce
  degraded technical behavior, fallback algorithms, or invented artifacts.
- Follow the task through its completion condition and primary review, or report
  a concrete blocker with preserved evidence. Starting a background job is not
  delivery. Use bounded waits and the available asynchronous job mechanism so
  the primary agent can observe progress and receive user updates.
- Answer status questions without dropping supervision. When the user changes
  the task, update the packet and inform the worker; verify it has stopped any
  incompatible writes before assigning overlapping work. Do not send an update
  into a busy terminal as though it were a ready input prompt.
- At handoff, record active jobs, accepted/provisional outputs, remaining checks,
  and the next concrete action. Recheck live state when resuming; stale logs do
  not prove that a process is still running or has finished.

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

Each correction names the failed command/case, observed result, root-cause
hypothesis, requested change, and check that can disprove the fix. When premise
and ownership are unchanged, keep the correction within the existing capability
task instead of opening a new task for each assertion or terminal failure.
Do not retry an unchanged deterministic failure. Retry a transient provider or
tool failure only with a reason and a bounded attempt/time budget; first check
that the previous job is no longer active to avoid duplicate work.

Continue the same session only for a local defect whose task premise and
context remain valid. Start from a clean reviewed checkpoint with a rewritten
task packet when the premise, authority, ownership, or architecture changes.
Before replacing the session/task root, preserve tracked and untracked changes,
the current packet, logs, test results, artifacts, and active-job state. The new
packet identifies what remains valid, what must be rechecked, and what must not
be reused. Carry forward accepted work and evidence deliberately; do not copy an
unreviewed diff into a clean task as though it were an accepted baseline.

When replacing an abandoned or context-overflowed session:
1. Terminate the obsolete worker's tmux session to free resources and stop quota burn:
   ```bash
   tmux kill-session -t <old_tmux_session_name>
   ```
2. If the workstream is tracked on research-dashboard, supersede the old session
   per [references/research-dashboard-sessions.md](references/research-dashboard-sessions.md).
   Otherwise skip registry updates.

## Review And Integration

When a provider reports completion or presents a reviewable diff:

1. Read its final report and audit log.
2. Inspect `git status --short`, `git diff --stat`, and the actual diff on the
   **task root** and, for **case-run**, on every **shared framework** path named
   in the packet (teardown cleanliness is mandatory). For **case-run** paper-ls
   reconstructions, also run hard-fail acceptance before treating the pack as
   done:
   ```bash
   python3 "$PAPER_LS/paper-ls-reproduce-from-pdf/scripts/check_case_run_acceptance.py" \
     --workspace <case-workspace> \
     --final-report <case>/.scratch/agent_artifacts/<task>/final_report.md \
     --framework <paper-ls-reconstruction-root>
   ```
   Fail the task on non-zero exit (path_selection / broken report links /
   missing outcome / dirty framework). Prefer linking
   `transcription/path_selection.json` in the final report over restating
   `chosen=`.
3. Trace external mappings and protocol assumptions to their normative source.
4. Verify according to the task type. For implementation, run the focused checks
   needed to establish the changed behavior; use negative checks for concrete
   invariants, not as a ritual. For read-only review, verify findings against
   source/evidence without requiring a code diff or implementation tests. For
   documentation, check instructions, links, and relevant command examples.
   Never trust a piped command whose recorded status came from `tee`; preserve
   each failing log before retrying.
5. Inspect real generated artifacts when the task requires them. A fixture or
   smoke test proves tooling, not representative application quality. Required
   real-case acceptance cannot be replaced by a collection of small tests.
6. For visual generation, inspect the requested rendered result. Require visible
   improvement over a baseline only for a visual-improvement task. A visual
   review delivers evidence-backed findings, not an edited artifact.
7. Apply corrections at every responsible layer. If the task exposed a
   reusable delegation gap, update this skill or its provider profile as well
   as the active task.
8. Commit only after primary-agent review and verification (**impl**).
9. **Session & Tmux Teardown Protocol (终端非存储，验收即销毁)**:
   - **Tmux is an ephemeral runtime, NOT durable evidence (产物即证据，终端非存储)**:
     authoritatively audited evidence lives strictly in Git commits (when impl),
     verified logs (`.scratch/agent_logs/<task>/`), and the task deliverable
     (`.scratch/agent_artifacts/<task>/final_report.md`). Terminal scrollback is
     ephemeral, non-reproducible, and easily lost.
   - **Prohibit lingering zombie sessions**: keeping worker tmux sessions open
     indefinitely after primary acceptance under the guise of "audit preservation"
     confuses users and clutters system resources.
   - **Mandatory completion teardown**:
     1. Once the primary agent has reviewed evidence and accepted (and committed
        when **impl**), immediately terminate the worker tmux session:
        ```bash
        tmux kill-session -t <worker_tmux_session>
        ```
     2. If the workstream is tracked on research-dashboard, mark the session
        completed and clear `tmux_session` per
        [references/research-dashboard-sessions.md](references/research-dashboard-sessions.md).
        Otherwise skip registry updates.
     3. Retain permanent deliverables under the task root: verified logs and
        `.scratch/agent_artifacts/<task>/` (and the worktree/case dir if kept).
     4. Remove completed **impl** worktrees only after their diff is accepted,
        intentionally discarded, or preserved elsewhere. **case-run** directories are
        product artifacts — do not delete them as if they were ephemeral
        worktrees. Keep required audit artifacts.

Once the declared acceptance checks and primary review pass, integrate and
report. Repeat or broaden verification only for new changes, failures, or a
specific unresolved correctness concern; do not add surprise requirements after
each passing report. Record which revision/artifact the evidence covers and
which required checks remain blocked or unrun.

Report outcomes in practical domain language: what works, what remains invalid
or blocked, distance to the real goal, and concrete evidence. Distinguish code
existence, unit tests, integrated real dependencies, representative valid
outputs, and final objective achievement.
