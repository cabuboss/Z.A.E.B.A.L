#!/usr/bin/env bash
# Prove that Kimi consumes the UserPromptSubmit hook without calling a model.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE="${ZAEBAL_CORE_PATH:-$SRC/core/zaebal.py}"
KIMI_BIN="${KIMI_BIN:-$(command -v kimi || true)}"

if [ -z "$KIMI_BIN" ] || [ ! -x "$KIMI_BIN" ]; then
  echo "error: kimi executable not found" >&2
  exit 1
fi
if [ ! -f "$CORE" ]; then
  echo "error: zaebal core not found: $CORE" >&2
  exit 1
fi

CANARY_ROOT="$(mktemp -d /tmp/zaebal-kimi-canary.XXXXXX)"
cleanup() {
  case "$CANARY_ROOT" in
    /tmp/zaebal-kimi-canary.*) rm -rf -- "$CANARY_ROOT" ;;
  esac
}
trap cleanup EXIT

KIMI_HOME="$CANARY_ROOT/kimi"
STATE_DIR="$CANARY_ROOT/state"
mkdir -p "$KIMI_HOME" "$STATE_DIR"

python3 - "$KIMI_HOME/config.toml" "$CORE" "$CANARY_ROOT/blocker-ran" <<'PYEOF'
import json
import pathlib
import shlex
import sys

config_path = pathlib.Path(sys.argv[1])
core = pathlib.Path(sys.argv[2]).resolve()
block_marker = pathlib.Path(sys.argv[3]).resolve()
core_command = f"python3 {shlex.quote(str(core))} --host kimi"
block_code = (
    "import pathlib,sys; "
    "pathlib.Path(sys.argv[1]).write_text('blocked', encoding='utf-8'); "
    "raise SystemExit(2)"
)
block_command = (
    f"python3 -c {shlex.quote(block_code)} {shlex.quote(str(block_marker))}"
)
config_path.write_text(
    """default_model = "kimi-code/k3"

[providers."managed:kimi-code"]
type = "kimi"
api_key = "zaebal-canary-fake-token"
base_url = "http://127.0.0.1:1/v1"

[models."kimi-code/k3"]
provider = "managed:kimi-code"
model = "k3"
max_context_size = 1048576
capabilities = ["thinking", "always_thinking", "image_in", "video_in", "tool_use"]
display_name = "K3"

[[hooks]]
event = "UserPromptSubmit"
command = """ + json.dumps(core_command) + """
timeout = 20

[[hooks]]
event = "UserPromptSubmit"
command = """ + json.dumps(block_command) + """
timeout = 5
""",
    encoding="utf-8",
)
PYEOF

set +e
KIMI_CODE_HOME="$KIMI_HOME" \
KIMI_DISABLE_TELEMETRY=1 \
ZAEBAL_STATE_DIR="$STATE_DIR" \
"$KIMI_BIN" -p "ты меня заебал" --output-format text \
  >"$CANARY_ROOT/stdout" 2>"$CANARY_ROOT/stderr"
KIMI_STATUS=$?
set -e

if [ "$KIMI_STATUS" -eq 0 ]; then
  echo "error: Kimi turn was not blocked before the model boundary" >&2
  exit 1
fi
if [ ! -f "$CANARY_ROOT/blocker-ran" ]; then
  echo "error: blocking hook did not run; nonzero Kimi exit is not sufficient evidence" >&2
  sed -n '1,80p' "$CANARY_ROOT/stderr" >&2
  exit 1
fi
if ! grep -Eq "UserPromptSubmit hook blocked|Prompt hook blocked" "$CANARY_ROOT/stderr"; then
  echo "error: Kimi did not confirm that UserPromptSubmit blocked the turn" >&2
  sed -n '1,80p' "$CANARY_ROOT/stderr" >&2
  exit 1
fi

python3 - "$STATE_DIR/incidents.jsonl" <<'PYEOF'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
if not path.is_file():
    raise SystemExit("error: Kimi did not execute the Z.A.E.B.A.L. hook")
events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
matches = [
    event for event in events
    if event.get("kind") == "directed"
    and event.get("weight") == 1.0
    and isinstance(event.get("trigger_id"), str)
]
if len(matches) != 1:
    raise SystemExit(f"error: expected one directed hook incident, got {len(matches)}")
PYEOF

echo "Kimi host canary passed: hook consumed a content-part prompt; model turn was blocked."
