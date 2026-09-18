# Codex DeepSeek Provider Profile

Preferred provider within the DeepSeek family (not the global default). Use
Codex with the local profile overlay `~/.codex/deepseek.config.toml` via
`-p deepseek`.

Do not use plain `codex` for DeepSeek work: that keeps the default OpenAI
auth/model path. Do not launch DeepSeek Harness `dsh` for new tasks; see
[dsh.md](dsh.md) only for legacy recovery.

## Prerequisites

Confirm before the first DeepSeek task on a host:

- `~/.codex/deepseek.config.toml` sets `model_provider = "deepseek"`,
  `model = "deepseek-v4-flash"`, and a real DeepSeek API credential
  (`experimental_bearer_token` or `env_key`)
- `model_catalog_json` points at a readable catalog that includes
  `deepseek-v4-flash` (normally `~/.codex/models.json`)
- The profile remains a layer over base `~/.codex/config.toml`; do not move
  DeepSeek defaults into the base config if OpenAI auth must keep working

## Smoke

```bash
timeout 90s codex -p deepseek exec --skip-git-repo-check -C /tmp \
  'Reply with exactly: deepseek-codex-ok. Do not use tools. Do not explain.'
```

Expect exit 0 and the exact text `deepseek-codex-ok`. The run should report
`model: deepseek-v4-flash` and `provider: deepseek`. A successful OpenAI
`codex` smoke does not prove the DeepSeek profile works.

Keep a task-local verification record with host, Codex version, profile name
(`deepseek`), selected model, and smoke log path. Later tasks may reuse that
record when those inputs are unchanged. Re-check after a Codex upgrade,
profile/catalog/credential change, host change, or a failure that calls the
previous result into question.

## Interactive Development

```bash
tmux new-session -d -s <project>-codex-ds-<task> -c <worktree> \
  'codex -p deepseek --dangerously-bypass-approvals-and-sandbox'
```

`--dangerously-bypass-approvals-and-sandbox` matches the skill's interactive
full-auto posture: approvals skipped inside the assigned session. Prefer a
narrower sandbox (`-s workspace-write -a never`) when the task packet does not
require unrestricted writes. Use `--add-dir /exact/path` only when the packet
assigns that additional root.

Wait for the Codex input prompt, then send the short task-packet bootstrap and
a separate Enter. Confirm model or tool activity. Text left in the input box is
not a submitted task.

## Headless And Review

Bounded headless implementation:

```bash
codex -p deepseek exec --skip-git-repo-check -C <worktree> \
  --dangerously-bypass-approvals-and-sandbox \
  'Read .scratch/agent_prompts/<task>.md and execute it. Do not commit or push.'
```

Read-only review:

```bash
codex -p deepseek exec --skip-git-repo-check -C <worktree> \
  -s read-only -a never \
  'Read the assigned review packet and return the requested result. Do not edit files.'
```

Resume only with the same objective, worktree, and permission scope:

```bash
codex -p deepseek resume --last
```

Record the session ID, profile (`deepseek`), model/provider evidence, permission
mode, and log path in task-local audit artifacts. Do not use resume to change
the task objective or worktree.

## Logging

```bash
mkdir -p .scratch/agent_logs/<task>
tmux pipe-pane -t <project>-codex-ds-<task> -o \
  'cat >> .scratch/agent_logs/<task>/codex-deepseek-$(date +%Y%m%d-%H%M%S).log'
```

Codex may write inside the assigned worktree, but it must not commit, push,
modify sibling repositories, or place review artifacts outside the task
worktree.
