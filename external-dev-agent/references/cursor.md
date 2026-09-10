# Cursor Provider Profile

Use Cursor's default auto model. Do not pass a model flag or ask it to switch
models.

## Interactive Development

```bash
tmux new-session -d -s <project>-cursor-<task> -c <worktree> \
  'agent --yolo --sandbox disabled'
```

Do not add `--trust` in interactive tmux mode. Current Cursor CLI versions
reject it with:

```text
--trust can only be used with --print/headless mode
```

Use `--trust` only for a bounded headless `agent --print` invocation.

After the input prompt appears, send the task-packet bootstrap text and then a
separate `C-m`. Confirm the pane displays `Working` or `Running`, rather than
only pasted text.

## Logging

```bash
mkdir -p .scratch/agent_logs/<task>
tmux pipe-pane -t <project>-cursor-<task> -o \
  'cat >> .scratch/agent_logs/<task>/cursor-$(date +%Y%m%d-%H%M%S).log'
```

Cursor may run with broad CLI permissions inside the assigned worktree, but it
must not commit, push, modify sibling repositories, or place review artifacts
outside the task worktree.

## Teardown

Upon primary-agent review and acceptance, immediately destroy the tmux session:
```bash
tmux kill-session -t <project>-cursor-<task>
```
Do not keep completed Cursor tmux sessions alive after work is accepted into the baseline.
