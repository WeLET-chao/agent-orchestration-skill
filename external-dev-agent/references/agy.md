# Antigravity Provider Profile

Use `agy` for Gemini-backed implementation or review. Prefer Gemini via `agy`
for UI/frontend visual design and multimodal visual review. For visual review,
prefer a Gemini Flash model when the launcher supports an explicit compatible
choice; do not silently switch a user-selected model. Verify currently
available model names with `agy models`; availability and account eligibility
can change.

Start cwd / `--workdir` = **task root** (`impl` worktree, `review` path, or
`case-run` case workspace). See `SKILL.md` task classes.

## TTY Requirement

`agy --print` requires a pseudo-TTY on this host. A pipe or ordinary redirected
stdout may be empty, truncated, or hang. Use the bundled wrapper:

```bash
SKILL="${EXTERNAL_DEV_AGENT_SKILL:-$HOME/.agents/skills/external-dev-agent}"
bash "$SKILL/scripts/run_agy_print.sh" \
  -f .scratch/agent_prompts/<task>.md \
  --model gemini-3.8-flash-high \
  --effort high \
  --timeout 12m \
  --workdir <task-root> \
  --out .scratch/agent_artifacts/<task>/response.txt \
  --log .scratch/agent_logs/<task>/agy.tty
```

The wrapper adds `--dangerously-skip-permissions` for headless operation and
preserves the pseudo-TTY transcript. Keep output and logs in the assigned
**task root**.

Relative prompt, output, log, and additional-directory paths resolve from
`--workdir`, not the shell that launches the wrapper. Supply exactly one `-p` or
`-f`. Explicit output/log paths must be new files; use a fresh run directory for
each retry. The default transcript path is unique per invocation.

`--out` captures combined terminal output, including diagnostics and possible
control sequences; it is not a structured assistant-only response. The wrapper
preserves the CLI exit status (GNU timeout normally returns 124 on timeout) and
prints the transcript location even on failure. Inspect the transcript and task
artifacts before treating a zero exit as task completion. A timeout does not
prove that independently launched child jobs have stopped; check recorded jobs
before retrying.

Wrapper regression check (fake CLI, no provider calls): run
`python3 scripts/test_run_agy_print.py` from this skill's directory. It exercises
the actual PTY wrapper, argument/path handling, file preservation, failure exit
codes, and timeout evidence.

## Interactive By Task Class

**impl** (writable worktree):

```bash
tmux new-session -d -s <project>-agy-<task> -c <worktree> \
  'agy --model <model> --effort high --mode accept-edits --dangerously-skip-permissions'
```

**review** (no new worktree; hard plan mode required):

```bash
tmux new-session -d -s <project>-agy-<task> -c <task-root> \
  'agy --model gemini-3.8-flash-high --effort high --mode plan --dangerously-skip-permissions'
```

`--mode plan` reduces native edit tools; the packet must still forbid writes
outside `.scratch/`. Shell can still mutate files — primary verifies `git status`
afterward. Prefer a clean tree (see `SKILL.md` review rules).

**case-run** (cwd = case workspace):

```bash
tmux new-session -d -s recon-<case-slug>-agy-<task> -c <case-workspace> \
  'agy --model <model> --effort high --mode accept-edits --dangerously-skip-permissions'
```

Do **not** treat `--add-dir <framework>` as read-only. Put framework paths in the
packet for invocation only. Teardown: fail if `git -C <framework>` is dirty.

Submit the task-packet bootstrap after the TUI is ready. Record the exact model
and effort separately from the `agy` launcher identity.

Do not label a result merely `Gemini`. Record the launcher/channel (`agy`) and
the selected model/effort. Account eligibility, quota, and region failures are
external environment blockers, not implementation failures.
