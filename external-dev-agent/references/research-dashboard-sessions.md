# Research Dashboard Session Registry

Use this reference **only** when the workstream is tracked on
`research-dashboard`. Otherwise skip every step here; the main skill's
task-root / tmux / artifact rules still apply.

Script root (adjust if your checkout differs):

```text
/home/wangchao/github/research-dashboard/scripts/session.py
```

## Register Or Update On Start

After the worker is launched and you have a provider session ID (when
available), tmux pane, **task root** (impl worktree, review path, or case
workspace), and resume command:

```bash
python3 /home/wangchao/github/research-dashboard/scripts/session.py record \
  --project-id <project_id> \
  --provider <codex|cursor|claude|agy|opencode> \
  --session-id <session_uuid> \
  --title "<Concise Chinese Task Title>" \
  --resume-cmd "<Exact resume command, e.g. codex resume <id>>" \
  --repo-path "<task-root: worktree | review path | case workspace>" \
  --tmux "<tmux_session:window.pane>" \
  --milestone-id <milestone_id> \
  --status working
```

Prefer recording the concrete **task root**. For **impl**, that is the git
worktree path (historically `worktree_path`). For **case-run**, use the case
workspace path — not a framework-repo worktree invented for the case.

## Status While Awaiting Primary Review

When a worker finishes its run and stops at the task packet's hard stop, it is
`ready for primary review`. Do **not** mark the session as `completed` on the
dashboard while it is merely paused awaiting review.

## Supersede On Session Replacement

When replacing an abandoned or context-overflowed session (after killing the
obsolete tmux session per the main skill):

Do **not** delete the old session from the dashboard. Mark it as superseded to
preserve historical provenance, and ensure its `tmux_session` is cleared to
`null`:

```bash
python3 /home/wangchao/github/research-dashboard/scripts/session.py supersede \
  --project-id <project_id> \
  --session-id <old_session_uuid> \
  --new-id <new_session_uuid> \
  --reason "<Brief reason, e.g., 上下文爆炸重新拉起/技术路线重构>"
```

## Complete And Clear Tmux On Acceptance

After primary review, verification, commit (when **impl**), and
`tmux kill-session` (mandatory in the main skill), update the registry: set
`status` to `completed` and **clear `tmux_session` to `null`** (either directly
in `data/projects/<project_id>.json` or via `session.py`):

```bash
python3 /home/wangchao/github/research-dashboard/scripts/session.py record \
  --project <project_id> \
  --parent <parent_session_id> \
  --title "<Task Title>" \
  --status completed \
  --clear-tmux
```

Retain only permanent deliverables in the registry fields: `artifact` and
`worktree_path` / task-root path (if kept for inspection). The dashboard should
then show `已完成` and `产物 📋` without a lingering `tmux: ... 📋` button.

Leaving worker tmux running after acceptance while the dashboard already shows
`completed` confuses users (suspected runaway loops or token burn) and wastes
resources; always kill tmux first, then clear the registry field.
