# claude-usage-bar

> Free macOS menu bar plugin showing **real-time Claude Code token usage** — session and weekly progress bars that match the Claude.ai desktop exactly.

![SwiftBar plugin showing Claude usage stats](https://img.shields.io/badge/SwiftBar-plugin-blue) ![Python 3](https://img.shields.io/badge/python-3.x-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![macOS](https://img.shields.io/badge/macOS-only-lightgrey)

---

## What it shows

- **Menu bar**: today's output tokens + current usage % (colour-coded green → amber → red)
- **Session bar**: 5h rolling window usage vs your plan limit — matches Claude.ai desktop exactly
- **Weekly bar**: 7-day rolling usage with reset countdown
- **Burn rate**: tokens/hour over the last 3 hours + ETA to limit
- **Today / Yesterday / 7d / 30d** token counts and estimated cost
- **Top projects**: which Claude Code projects used the most tokens

Numbers are pulled directly from Anthropic's API rate-limit headers on every refresh, so they match the "Plan usage limits" page in the Claude.ai desktop app to the percent.

---

## Install

> **Requirements:** macOS, [Claude Code](https://claude.ai/code) already installed and logged in, Python 3 (comes with macOS), [Homebrew](https://brew.sh)

### One-liner (recommended)

```bash
brew install --cask swiftbar && mkdir -p ~/SwiftBarPlugins && curl -fsSL https://raw.githubusercontent.com/peterkoczan/claude-usage-bar/main/claude_usage.15s.py -o ~/SwiftBarPlugins/claude_usage.15s.py && chmod +x ~/SwiftBarPlugins/claude_usage.15s.py
```

Then **open SwiftBar** (it's now in `/Applications`) and point it at `~/SwiftBarPlugins` when asked for a plugin folder.

---

### Step-by-step

**1. Install SwiftBar**
```bash
brew install --cask swiftbar
```

**2. Open SwiftBar**

Launch SwiftBar from `/Applications/SwiftBar.app`. It will ask you to choose a plugin folder — type or paste:
```
~/SwiftBarPlugins
```
Click **Select Plugin Folder**.

**3. Download the plugin**
```bash
mkdir -p ~/SwiftBarPlugins
curl -fsSL https://raw.githubusercontent.com/peterkoczan/claude-usage-bar/main/claude_usage.15s.py \
  -o ~/SwiftBarPlugins/claude_usage.15s.py
chmod +x ~/SwiftBarPlugins/claude_usage.15s.py
```

**4. Done** — the ⚡ icon appears in your menu bar immediately.

---

### Already have SwiftBar?

Just copy the plugin into your existing plugin folder:
```bash
curl -fsSL https://raw.githubusercontent.com/peterkoczan/claude-usage-bar/main/claude_usage.15s.py \
  -o ~/SwiftBarPlugins/claude_usage.15s.py && chmod +x ~/SwiftBarPlugins/claude_usage.15s.py
```

Then click the SwiftBar icon → **Refresh All**.

---

## Configuration

On first run the plugin creates `~/.claude_usage.json` with Pro plan defaults. Edit it to match your plan:

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

Built-in plan presets — set `"plan"` and omit the explicit limits:

| Plan | Weekly limit | Session limit |
|------|-------------|---------------|
| free | 100K | 20K |
| pro  | 1M   | 200K |
| team | 2M   | 400K |
| max  | 5M   | 800K |

---

## How it works

The plugin reads `~/.claude/projects/**/*.jsonl` for project breakdowns and cost estimates, and makes a minimal API call once per minute to read Anthropic's rate-limit response headers:

```
anthropic-ratelimit-unified-5h-utilization  → session %
anthropic-ratelimit-unified-7d-utilization  → weekly %
anthropic-ratelimit-unified-*-reset         → exact reset timestamps
```

This gives numbers that match the Claude.ai desktop precisely. The API call uses the OAuth token Claude Code stores in your macOS Keychain — no setup required. The display refreshes every 15 seconds; the API is called at most once per minute (result is cached).

---

## Uninstall

```bash
rm ~/SwiftBarPlugins/claude_usage.15s.py
```

---

## License

MIT — free to use, modify, and share.
