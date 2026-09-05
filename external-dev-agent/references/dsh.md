# DeepSeek Harness Provider Profile

Use the repository worktree as the working directory because Dsh derives its
workspace root from the current directory.

## Schedule

Prefer starting or resuming non-urgent Dsh development outside Beijing weekday
peak periods (`09:00-12:00`, `14:00-18:00`). A direct user request, urgent
recovery, or short smoke takes precedence. Do not terminate an active task
solely because the clock enters a peak period.

## Smoke

```bash
timeout 90s dsh exec --ephemeral \
  --sandbox read-only --ask-for-approval never \
  'Reply with exactly: DSH_OK'
```

The expected default model is currently
`deepseek-official/deepseek-v4-flash`. Verify the composed configuration with
`dsh --dump-config`; do not infer the effective model from a task prompt.

Before the first long Dsh task on a host, also verify that the composed TUI
profile enables semantic context compaction and tool-result pruning. Disk
compression of a session log is not model-context compaction. If host-local
profile overrides are required, keep them outside the project and verify the
composed result instead of assuming the override loaded. Exercise `/compact`
once in a disposable session and confirm that the TUI reports compacted
context.

## Interactive Development

```bash
tmux new-session -d -s <project>-dsh-<task> -c <worktree> \
  'dsh --full-auto'
```

`--full-auto` means worktree-scoped writes with approvals disabled. It is not
the same as `--yolo`, which permits unrestricted machine-wide writes. Use
`--add-dir /exact/path` only when the task packet assigns that additional root.

Wait for the Dsh input prompt, then send the short task-packet bootstrap and a
separate Enter. Confirm model or tool activity. Text left in the input box is
not a submitted task.

For a bounded headless implementation:

```bash
dsh exec --full-auto 'Read .scratch/agent_prompts/<task>.md and execute it.'
```

For a read-only review:

```bash
dsh exec --ephemeral --json \
  --sandbox read-only --ask-for-approval never \
  'Read the assigned review packet and return the requested result.'
```

Use `dsh --resume=<session-id>` only to continue the same objective and
permission scope. Record the session ID, selected model/configuration evidence,
permission mode, and any account switch in task-local audit artifacts.

For bounded resumable automation, use the CLI's `dsh exec resume <session-id>
'<follow-up>'` form only after confirming it preserves the original permission
controls. Do not use resume to change the task objective or worktree.

If Dsh keeps restating an already concrete plan without editing, send one short
steering message to begin implementation and stay within the task packet. If it
still does not progress, preserve the session evidence and restart from the
reviewed checkpoint instead of accumulating prompts.
