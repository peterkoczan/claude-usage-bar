#!/usr/bin/env bash
set -e

PLUGIN_DIR="${SWIFTBAR_PLUGIN_DIR:-$HOME/SwiftBarPlugins}"
SCRIPT="$(cd "$(dirname "$0")" && pwd)/claude_usage.15s.py"

mkdir -p "$PLUGIN_DIR"
cp "$SCRIPT" "$PLUGIN_DIR/"
chmod +x "$PLUGIN_DIR/claude_usage.15s.py"

echo "Installed to $PLUGIN_DIR/claude_usage.15s.py"
echo "Open SwiftBar and click Refresh All (or it will pick it up automatically)."
