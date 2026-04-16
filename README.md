# claude-usage-bar

A [SwiftBar](https://swiftbar.app) plugin that shows Claude Code token usage stats in your macOS menu bar — weekly and session progress bars, cost estimates, and per-day breakdowns.

## What it shows

- **Menu bar**: today's token count + dominant usage percentage (colour-coded)
- **Progress bars**: weekly (7-day rolling) and session (5h rolling) against your plan limits
- **Today**: input/output/cache tokens + estimated cost
- **Yesterday / Last 7 days / Last 30 days** summaries
- **Optional**: org-level API usage via Anthropic API key

Reads directly from `~/.claude/projects/**/*.jsonl` — no API key required for local Claude Code usage.

## Install

```bash
# 1. Install SwiftBar
brew install --cask swiftbar

# 2. Open SwiftBar and choose a plugin folder when prompted (e.g. ~/SwiftBarPlugins)

# 3. Run the install script
./install.sh

# 4. Click the menu bar icon → Refresh All
```

Or manually:
```bash
mkdir -p ~/SwiftBarPlugins
cp claude_usage.1m.py ~/SwiftBarPlugins/
chmod +x ~/SwiftBarPlugins/claude_usage.1m.py
```

## Configuration

On first run the plugin writes `~/.claude_usage.json` with Pro defaults. Edit it to match your plan:

```json
{
  "plan": "pro",
  "weekly_limit": 1000000,
  "session_window_hours": 5,
  "session_limit": 200000,
  "pricing_input": 3.00,
  "pricing_output": 15.00
}
```

Built-in plan presets (set `"plan"` and omit explicit limits):

| Plan  | Weekly limit | Session limit |
|-------|-------------|---------------|
| free  | 100K        | 20K           |
| pro   | 1M          | 200K          |
| team  | 2M          | 400K          |
| max   | 5M          | 800K          |

## Optional: Anthropic API key

For org-level API usage stats, add your key via right-click → Plugin settings → `ANTHROPIC_API_KEY`.

## Requirements

- macOS with [SwiftBar](https://swiftbar.app)
- Python 3 (ships with macOS)
- Claude Code with `~/.claude/projects/` directory
