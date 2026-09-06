#!/usr/bin/env bash
set -euo pipefail

AGY_BIN="${AGY_BIN:-agy}"
MODEL="${AGY_MODEL:-gemini-3.8-flash-high}"
EFFORT="${AGY_EFFORT:-}"
PRINT_TIMEOUT="${AGY_PRINT_TIMEOUT:-8m}"
WALL_TIMEOUT="${AGY_WALL_TIMEOUT:-540s}"
PROMPT=""
PROMPT_FILE=""
PROMPT_INPUTS=0
OUT=""
LOG=""
WORKDIR="$(pwd)"
ADD_DIRS=()

usage() {
  cat <<'EOF'
Usage: run_agy_print.sh (-p 'prompt' | -f prompt.txt) [options]

Options:
  -p TEXT           Prompt string
  -f FILE           Read prompt from file
  --model NAME      agy model (default: gemini-3.8-flash-high)
  --effort LEVEL    agy reasoning effort (low, medium, or high)
  --timeout VALUE   Wall-clock timeout (default: 540s)
  --print-timeout D agy --print-timeout (default: 8m)
  --out FILE        New file for combined PTY output, including diagnostics (default: stdout)
  --log FILE        New pseudo-TTY transcript file (default: unique task-local file)
  --dir PATH        Repeatable agy --add-dir
  --workdir PATH    Working directory (default: current directory)

All relative prompt, output, log, and --dir paths are relative to --workdir.
Existing output/log files are never overwritten. Supply exactly one -p or -f.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p) PROMPT="${2:?}"; PROMPT_INPUTS=$((PROMPT_INPUTS + 1)); shift 2 ;;
    -f) PROMPT_FILE="${2:?}"; PROMPT_INPUTS=$((PROMPT_INPUTS + 1)); shift 2 ;;
    --model) MODEL="${2:?}"; shift 2 ;;
    --effort) EFFORT="${2:?}"; shift 2 ;;
    --timeout) WALL_TIMEOUT="${2:?}"; shift 2 ;;
    --print-timeout) PRINT_TIMEOUT="${2:?}"; shift 2 ;;
    --out) OUT="${2:?}"; shift 2 ;;
    --log) LOG="${2:?}"; shift 2 ;;
    --dir) ADD_DIRS+=("${2:?}"); shift 2 ;;
    --workdir) WORKDIR="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$PROMPT_INPUTS" -ne 1 ]]; then
  echo "ERROR: provide exactly one -p or -f" >&2
  exit 2
fi

# Resolve the executable before changing cwd, including a caller-relative AGY_BIN.
AGY_BIN="$(command -v "$AGY_BIN")" || { echo "ERROR: agy not found" >&2; exit 127; }
if [[ "$AGY_BIN" != /* ]]; then AGY_BIN="$(pwd)/$AGY_BIN"; fi
cd -- "$WORKDIR"
WORKDIR="$(pwd)"

if [[ -n "$PROMPT_FILE" ]]; then
  PROMPT="$(<"$PROMPT_FILE")"
fi
if [[ -z "$PROMPT" ]]; then
  echo "ERROR: provide -p or -f" >&2
  exit 2
fi

command -v script >/dev/null 2>&1 || { echo "ERROR: script not found" >&2; exit 127; }
command -v timeout >/dev/null 2>&1 || { echo "ERROR: timeout not found" >&2; exit 127; }

case "$EFFORT" in
  ""|low|medium|high) ;;
  *) echo "ERROR: --effort must be low, medium, or high" >&2; exit 2 ;;
esac

# Reserve explicit paths without clobbering prior evidence or aliases.
reserve_file() {
  mkdir -p -- "$(dirname -- "$1")"
  if [[ -e "$1" || -L "$1" ]] || ! (set -o noclobber; : >"$1"); then
    echo "ERROR: output/log must be a new file: $1" >&2
    exit 2
  fi
}

if [[ -n "$LOG" ]]; then
  reserve_file "$LOG"
  TTY_LOG="$LOG"
else
  mkdir -p .scratch/agent_logs/agy
  TTY_LOG="$(mktemp "$WORKDIR/.scratch/agent_logs/agy/agy_print_XXXXXX.tty")"
fi
if [[ -n "$OUT" ]]; then reserve_file "$OUT"; fi

PROMPT_TMP="$(mktemp /tmp/agy_prompt_XXXXXX.txt)"
INNER_SH="$(mktemp /tmp/agy_inner_XXXXXX.sh)"
cleanup() { rm -f "$PROMPT_TMP" "$INNER_SH"; }
trap cleanup EXIT

printf '%s' "$PROMPT" >"$PROMPT_TMP"

cat >"$INNER_SH" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd $(printf '%q' "$WORKDIR")
args=(
  timeout $(printf '%q' "$WALL_TIMEOUT")
  $(printf '%q' "$AGY_BIN")
  --dangerously-skip-permissions
  --model $(printf '%q' "$MODEL")
  --print-timeout $(printf '%q' "$PRINT_TIMEOUT")
)
EOF

if [[ -n "$EFFORT" ]]; then
  printf 'args+=(--effort %q)\n' "$EFFORT" >>"$INNER_SH"
fi

for dir in "${ADD_DIRS[@]}"; do
  printf 'args+=(--add-dir %q)\n' "$dir" >>"$INNER_SH"
done

cat >>"$INNER_SH" <<EOF
prompt=\$(cat $(printf '%q' "$PROMPT_TMP"))
args+=(--print="\$prompt")
"\${args[@]}"
EOF

chmod +x "$INNER_SH"
exit_status=0
if [[ -n "$OUT" ]]; then
  script -q -e -c "$INNER_SH" "$TTY_LOG" >"$OUT" 2>&1 || exit_status=$?
else
  script -q -e -c "$INNER_SH" "$TTY_LOG" || exit_status=$?
fi

echo "agy transcript: $TTY_LOG" >&2
exit "$exit_status"
