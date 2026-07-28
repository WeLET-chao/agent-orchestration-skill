# agent-orchestration skills

Cross-repo **agent delegation and supervision** workflows: external CLIs, tmux sessions, git worktrees, audit logs, and review checkpoints.

## Table of contents

- [Skills](#skills)
- [Quick start](#quick-start)
- [Layout](#layout)

## Skills

| Skill | Purpose |
|-------|---------|
| `cursor-dev-agent` | Supervise Cursor `agent` CLI as an implementation subagent (tmux, worktrees, audit, no-commit guardrails) |
| `cursor-ide-dev-agent` | Coordinate manual Cursor IDE agent sessions with paste-ready task packets when CLI/tmux orchestration is unavailable |
| `claude-dev-agent` | Supervise Claude Code CLI as an implementation subagent (tmux/headless, worktrees, audit, no-commit guardrails) |

Use `cursor-dev-agent` when you can start `agent` in tmux or headless mode. Use
`cursor-ide-dev-agent` when the user opens or continues Cursor IDE sessions
manually and the primary agent prepares prompts plus review checkpoints. Use
`claude-dev-agent` when delegation should run through Claude Code CLI.

## Quick start

No shared package or `.venv` for this group. Each skill is self-contained (`SKILL.md` + optional `agents/` metadata).

```bash
REPO=/path/to/agent-skills
bash "$REPO/scripts/bootstrap_links.sh" --repo-root "$REPO"
```

Use from any project after the skill is linked under `~/.agents/skills/` (or your Codex skills path).

## Layout

```text
agent-orchestration/
  cursor-dev-agent/
    SKILL.md
    agents/openai.yaml    # optional Codex UI metadata
  cursor-ide-dev-agent/
    SKILL.md
    agents/openai.yaml
  claude-dev-agent/
    SKILL.md
    agents/openai.yaml
```

Future siblings (e.g. `external-agent-cli`) belong in this group when migrated.
