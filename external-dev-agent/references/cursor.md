# Cursor Provider Profile

Use Cursor's default auto model. Do not pass a model flag or ask it to switch
models.

Start cwd = **task root** (`impl` worktree, `review` path, or `case-run` case
workspace). See `SKILL.md` task classes.

## Interactive Development (`impl`)

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

## Interactive Review (`review`)

**Do not** use `--yolo --sandbox disabled` for read-only review (full write/shell
access). Prefer plan/ask / read-only sandbox flags supported by the installed
`agent` CLI (verify with `agent --help` at dispatch time). Packet write allowlist
must be `.scratch/agent_artifacts/<task>/` (+ logs) only.

```bash
# Example shape — adjust flags to the host's agent CLI:
tmux new-session -d -s <project>-cursor-<task> -c <task-root> \
  'agent --mode plan'
```

If the CLI cannot enforce a hard read-only mode, use an **impl** worktree or
ephemeral snapshot instead of reviewing on a dirty primary checkout.

## Case-run

```bash
tmux new-session -d -s recon-<case-slug>-cursor-<task> -c <case-workspace> \
  'agent --yolo --sandbox disabled'
```

Do **not** `--add-dir` a shared framework path expecting read-only behavior.
Name shared frameworks in the packet for command invocation only. On teardown,
primary must `git -C <framework> status` / `diff` and **reject** the case if dirty.

## Logging

```bash
mkdir -p .scratch/agent_logs/<task>
tmux pipe-pane -t <project>-cursor-<task> -o \
  'cat >> .scratch/agent_logs/<task>/cursor-$(date +%Y%m%d-%H%M%S).log'
```

Cursor may run with broad CLI permissions inside the assigned **task root**, but
it must not commit, push, modify sibling repositories, or place review artifacts
outside the packet write allowlist.

## Teardown

Upon primary-agent review and acceptance, immediately destroy the tmux session:
```bash
tmux kill-session -t <project>-cursor-<task>
```
Do not keep completed Cursor tmux sessions alive after work is accepted into the baseline.
