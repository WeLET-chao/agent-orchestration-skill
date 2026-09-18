# Antigravity Provider Profile

Use `agy` for Gemini-backed implementation or review. Prefer Gemini via `agy`
for UI/frontend visual design and multimodal visual review. For visual review,
prefer a Gemini Flash model when the launcher supports an explicit compatible
choice; do not silently switch a user-selected model. Verify currently
available model names with `agy models`; availability and account eligibility
can change.

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
  --workdir <worktree> \
  --out .scratch/agent_artifacts/<task>/response.txt \
  --log .scratch/agent_logs/<task>/agy.tty
```

The wrapper adds `--dangerously-skip-permissions` for headless operation and
preserves the pseudo-TTY transcript. Keep output and logs in the assigned
worktree.

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

For an interactive development session, run `agy` in tmux with the task's
authorized permission mode, submit the task-packet bootstrap after the TUI is
ready, and record the exact model and effort separately from the `agy`
launcher identity.

Do not label a result merely `Gemini`. Record the launcher/channel (`agy`) and
the selected model/effort. Account eligibility, quota, and region failures are
external environment blockers, not implementation failures.
