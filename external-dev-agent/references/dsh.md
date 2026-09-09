# DeepSeek Harness Provider Profile (Deprecated)

**Deprecated.** Do not start new DeepSeek development or review tasks with
`dsh`. Prefer Codex with the DeepSeek profile:

- Provider profile: [codex-deepseek.md](codex-deepseek.md)
- Launch: `codex -p deepseek`
- Headless smoke/exec: `codex -p deepseek exec ...`

Keep this document only for recovering an already-running Dsh session, reading
legacy audit logs, or answering why an old task used Dsh. If the user
explicitly requests `dsh` anyway, warn that it is deprecated, record that
override in the task packet, and still prefer migrating the next task to Codex.

---

## Legacy reference

The sections below are retained for historical recovery. They are not the
current preferred DeepSeek path.

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

`--sandbox read-only` prohibits file modifications; it does not restrict reads
outside the workspace. A primary-owned native probe on rc.13 read a harmless
outside-workspace file, while the same probe under the circuit runner's `bwrap`
wrapper could read its assigned file and received `FS_NOT_FOUND` for the outside
file. Record native permission posture separately from OS read visibility; do
not claim native read isolation merely because all artifacts agree on a flag.
Verify composed configuration using a YAML structure parser, rejecting duplicate
model/config keys and unresolved model expressions. A matching string inside a
dump is not enough evidence that the effective model configuration was verified.

Before the first long Dsh task on a host, also verify that the composed TUI
profile enables semantic context compaction and tool-result pruning. Disk
compression of a session log is not model-context compaction. If host-local
profile overrides are required, keep them outside the project and verify the
composed result instead of assuming the override loaded. Exercise `/compact`
once in a disposable session and confirm that the TUI reports compacted
context.

### Reusing environment verification

Keep a task-local verification record with the host, CLI version, selected
model, effective profile/configuration, execution mode, account identity (no
credentials), and paths to smoke/compaction results. Later tasks can reference
that record when those inputs are unchanged; do not repeat the disposable
`/compact` exercise or model smoke merely because a new task packet was written.
Check current configuration/version and live session state before relying on it.

Repeat affected checks after a CLI upgrade, model/profile/account change, host
change, or a failure that calls the previous result into question. An account or
quota problem requires a fresh availability check after recovery; a compaction
configuration change requires renewed compaction verification. Missing evidence
means the original first-use checks still apply. A previous smoke proves the
recorded invocation worked, not that quota or service availability remains valid.

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
still does not progress, inspect pending input/tools and provider failures as
described in the main skill. If a restart is needed, preserve the diff, untracked
outputs, packet, and job state before starting from the reviewed checkpoint;
carry forward valid results instead of accumulating prompts or repeating work.
