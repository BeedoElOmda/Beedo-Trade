#!/usr/bin/env bash
# Beedo-Trade installer for macOS / Linux.
# Usage:  ./install.sh [goldapi-key]
set -euo pipefail

EGX_REPO="https://github.com/M-Abdelmegeed/EGX-Data-MCP-Server.git"
EGX_COMMIT="d4ee5625b48ed0c9682c321ab5776936b845cf63"   # tested version
EGX_DIR="$HOME/mcp-servers/EGX-Data-MCP-Server"
SKILL_DIR="$HOME/.claude/skills/beedo-trade"
HERE="$(cd "$(dirname "$0")" && pwd)"
KEY="${1:-}"

need() { command -v "$1" >/dev/null || { echo "Missing '$1'. $2" >&2; exit 1; }; }
need git "Install Git first."
need uv  "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"

echo "1/4 Installing the Beedo-Trade skill to $SKILL_DIR"
mkdir -p "$(dirname "$SKILL_DIR")"; rm -rf "$SKILL_DIR"
cp -R "$HERE/skills/beedo-trade" "$SKILL_DIR"

echo "2/4 Installing the EGX MCP server to $EGX_DIR"
[ -d "$EGX_DIR/.git" ] || { mkdir -p "$(dirname "$EGX_DIR")"; git clone --quiet "$EGX_REPO" "$EGX_DIR"; }
git -C "$EGX_DIR" fetch --quiet origin
git -C "$EGX_DIR" checkout --quiet --force "$EGX_COMMIT"
# The server prints a startup line on stdout, which is the MCP channel; send it to stderr instead.
sed -i.orig 's/print("Starting EGX Stock Tools MCP Server...")/print("Starting EGX Stock Tools MCP Server...", file=sys.stderr)/' "$EGX_DIR/main.py"
(cd "$EGX_DIR" && uv sync --quiet)
[ -n "$KEY" ] && printf 'GOLDAPI_KEY=%s\n' "$KEY" > "$EGX_DIR/.env"
UV="$(command -v uv)"

echo "3/4 Registering egx-mcp with Claude Code"
if command -v claude >/dev/null; then
  claude mcp remove egx-mcp -s user >/dev/null 2>&1 || true
  claude mcp add egx-mcp --scope user -- "$UV" --directory "$EGX_DIR" run main.py
else echo "   Claude Code CLI not found; skipped."; fi

echo "4/4 Registering egx-mcp and beedo-trade with Claude Desktop"
case "$(uname)" in
  Darwin) CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json" ;;
  *)      CFG="$HOME/.config/Claude/claude_desktop_config.json" ;;
esac
mkdir -p "$(dirname "$CFG")"; [ -f "$CFG" ] || echo '{}' > "$CFG"
cp "$CFG" "$CFG.bak"
uv run --no-project python - "$CFG" "$UV" "$EGX_DIR" "$SKILL_DIR" <<'EOF'
import json, sys
cfg, uv, d, skill = sys.argv[1:]
data = json.load(open(cfg))
servers = data.setdefault("mcpServers", {})
servers["egx-mcp"] = {"command": uv, "args": ["--directory", d, "run", "main.py"]}
servers["beedo-trade"] = {"command": uv, "args": ["run", "--script", skill + "/scripts/mcp_server.py"]}
json.dump(data, open(cfg, "w"), indent=2)
EOF
echo "   Updated $CFG (backup: $CFG.bak). Fully quit and reopen Claude Desktop."

echo; echo "Done. Start a new Claude session and ask: 'Analyse COMI with my course method.'"
[ -n "$KEY" ] || [ -f "$EGX_DIR/.env" ] || echo "Gold/silver prices need a free key from goldapi.io. Re-run: ./install.sh <key>"
