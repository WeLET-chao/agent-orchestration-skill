# agent-orchestration skills

Cross-repo **agent delegation and supervision** workflows: external CLIs, tmux
sessions, git worktrees, audit logs, and review checkpoints.

## Table of contents

- [Skills](#skills)
- [Quick start](#quick-start)
- [Layout](#layout)

## Skills

| Skill | Purpose |
|-------|---------|
| `external-dev-agent` | Supervise Cursor, Dsh, agy, Claude, OpenCode, or Copilot through one task-packet/worktree/tmux/review workflow with provider profiles |
| `cursor-ide-dev-agent` | Coordinate manual Cursor IDE agent sessions with paste-ready task packets when CLI/tmux orchestration is unavailable |
| `claude-dev-agent` | Supervise Claude Code CLI as an implementation subagent (tmux/headless, worktrees, audit, no-commit guardrails) |

Use `external-dev-agent` for CLI-driven implementation or review. Select its
Cursor, Dsh, agy, Claude, OpenCode, or Copilot provider profile while retaining
one common task-packet and primary-review lifecycle. Use `cursor-ide-dev-agent`
when the user opens or continues Cursor IDE sessions manually. Use
`claude-dev-agent` only for its existing Claude-specific workflow.

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
  external-dev-agent/
    SKILL.md
    agents/openai.yaml
    references/           # provider profiles and task-packet contract
    scripts/              # provider-specific deterministic wrappers
  cursor-ide-dev-agent/
    SKILL.md
    agents/openai.yaml
  claude-dev-agent/
    SKILL.md
    agents/openai.yaml
```
