---
name: claude-dev-agent
description: Start and supervise Claude Code CLI as a coding subagent in tmux, using isolated git worktrees, audit logs, fixed task prompts, interactive or headless modes, and primary-agent review checkpoints.
---

# Claude Dev Agent

Use this skill when implementation should be delegated to a Claude Code CLI
subagent while the primary agent owns architecture, task boundaries, review,
verification, merge order, and commits.

Use `cursor-dev-agent` for Cursor's `agent` CLI. Use this skill for `claude`.

## Operating Model

- **Primary agent** — the current coordinating agent or user. It owns task
  decomposition, worktree setup, review, verification, and checkpoint commits.
- **Claude subagent** — a `claude` CLI session in tmux or headless mode. It
  implements only the assigned task package and must not commit.
- Prefer one branch/worktree per delegated task.
- Prefer parallel Claude sessions only when task ownership does not overlap.
- Keep logs, prompts, and reports under `.scratch/claude_logs/`,
  `.scratch/claude_prompts/`, and `.scratch/claude_reports/`.
- Use model flags only when the user or task explicitly requests a model. When
  using the requested Fable 5 path, prefer `--model fable`.
- Use `--permission-mode bypassPermissions` only in trusted local worktrees.
- Headless `claude -p` is good for non-interactive, prompt-file style runs.
  Interactive tmux is better when the primary agent may need to send follow-ups.

## Preflight

Before starting a Claude task:

1. Ensure there is a reviewed checkpoint commit before delegation.
2. Run `git worktree list`, `tmux list-sessions`, and `git status --short`.
3. Do not remove active sessions, unreviewed worktrees, user-created worktrees,
   or unrelated external worktrees.
4. Classify tasks:
   - `Can run now` — independent implementation tasks.
   - `Review first` — completed diffs or reports that must be reviewed before
     new work.
   - `Serial later` — tasks depending on an accepted checkpoint or artifact.
5. Create one task prompt per session with scope, allowed files, forbidden
   actions, verification commands, artifacts, and final report path.
6. If the task depends on project policy, require Claude to read `AGENTS.md`,
   relevant docs, and touched code entry points.

Restart from a clean checkpoint instead of continuing a polluted session if it
rewrites unrelated files, hides failures by weakening tests, imports legacy as a
main path when forbidden, or cannot identify touched files and verification.

## Start Interactive Claude

Create an isolated worktree:

```bash
git worktree add -b <task-branch> ../<repo>-<task> <checkpoint>
```

Create prompt/log/report directories:

```bash
mkdir -p .scratch/claude_prompts .scratch/claude_logs .scratch/claude_reports
```

Start an interactive tmux session:

```bash
tmux new-session -d -s <project>-claude-<task> \
  -c ../<repo>-<task> \
  'claude --model fable --effort max --permission-mode bypassPermissions'
```

Attach logging:

```bash
tmux pipe-pane -t <project>-claude-<task> -o \
  'cat >> .scratch/claude_logs/<task>-$(date +%Y%m%d-%H%M%S).log'
```

Send the prompt and submit it with a separate Enter:

```bash
tmux send-keys -t <project>-claude-<task> \
  "$(cat .scratch/claude_prompts/<task>.md)" C-m
tmux send-keys -t <project>-claude-<task> C-m
```

Confirm it started:

```bash
tmux capture-pane -t <project>-claude-<task> -p | tail -80
```

If the pane is waiting for input, send a concise follow-up in the same session.
Do not start a duplicate session unless the current session is polluted or dead.

## Headless Claude Alternative

Use headless mode for long, self-contained tasks where no interactive follow-up
is expected:

```bash
tmux new-session -d -s <project>-claude-<task> \
  "cd ../<repo>-<task> && \
   cat .scratch/claude_prompts/<task>.md | \
   claude -p --model fable --effort max --permission-mode bypassPermissions \
     --add-dir /path/to/extra/context \
   2>&1 | tee .scratch/claude_logs/<task>.log"
```

For `claude -p`, pass input through stdin or a prompt argument. Do not rely on
shell command substitution that expands in the wrong working directory.

## Parallel Sessions

Use separate worktrees and non-overlapping file ownership. If two sessions need
the same core files, serialize them unless one is explicitly review-only or
plan-only.

Default response shape before launch:

```text
Can run now:
- <session>: <worktree>, owns <paths>, reason parallel-safe

Review first:
- <session/report>: <why review is required>

Serial later:
- <task>: waits for <artifact/checkpoint>
```

Review and merge one worktree at a time. After accepting one checkpoint, rebase
or recreate still-running worktrees before merging if their base is stale or
conflicts with accepted architecture.

## Prompt Template

Use a fixed prompt file:

```text
You are working in this isolated worktree:
<absolute worktree path>

Baseline checkpoint: <commit>

You are a coding subagent. Do not commit.
Primary agent will review your diff, run verification, and create checkpoints.
Read: AGENTS.md, <relevant docs>, <code entry points>.

Task:
- <concrete goal>
- Hard stop at: <reviewable checkpoint>

Allowed changes:
- <paths>

Forbidden:
- No git reset --hard, checkout --, or destructive cleanup.
- No commits.
- No unrelated rewrites.
- No fallback/repair/post-processing as the main implementation path when the
  project requires construction-time correctness.
- Do not silently skip required cases.

Implementation requirements:
- <requirements>
- Failed cases must produce explicit diagnostics.
- If required verification fails, final report must make that visible.

Verification:
- <commands>

Final report:
Write to .scratch/claude_reports/<TASK>.md with:
- changed files
- implemented behavior
- verification commands and results
- generated artifacts and exact paths
- known issues/blockers
```

## Review Loop

After Claude stops, reports completion, or waits for a follow-up:

1. Read `.scratch/claude_reports/<TASK>.md` if present.
2. Read the tmux log tail.
3. Inspect `git status --short` and `git diff --stat`.
4. Review the actual diff.
5. Run focused verification yourself.
6. Inspect regenerated artifacts when relevant.
7. Either send a correction prompt to the same session, restart from checkpoint,
   or commit/merge after review.

When the user asks for status, do not stop at a status-only answer if the pane
has produced a report or reviewable diff. Start the review loop immediately and
then report the result.
