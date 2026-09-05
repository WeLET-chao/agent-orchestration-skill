# Antigravity Provider Profile

Use `agy` for Gemini-backed implementation or review. Verify currently
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

For an interactive development session, run `agy` in tmux with the task's
authorized permission mode, submit the task-packet bootstrap after the TUI is
ready, and record the exact model and effort separately from the `agy`
launcher identity.

Do not label a result merely `Gemini`. Record the launcher/channel (`agy`) and
the selected model/effort. Account eligibility, quota, and region failures are
external environment blockers, not implementation failures.
