# Other CLI Provider Profiles

Use these for bounded tasks after a smoke test. Confirm installed CLI help when
flags or models may have changed.

## Claude

```bash
timeout 180s claude -p 'Read <task-packet> and execute it.' \
  --output-format text < /dev/null
```

## OpenCode

```bash
timeout 180s opencode run --dir <worktree> \
  --model prism/gpt-5.4 \
  --dangerously-skip-permissions \
  'Read <task-packet> and execute it.' < /dev/null
```

## Copilot

```bash
timeout 180s copilot -p 'Read <task-packet> and execute it.' < /dev/null
```

These commands are examples of known working invocations, not permanent model
availability guarantees. Record the actual CLI version, selected model,
permission mode, timeout, output, and exit status. For long interactive work,
use the common worktree/tmux/task-packet lifecycle rather than expanding a
single headless prompt indefinitely.
