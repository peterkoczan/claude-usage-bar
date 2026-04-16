#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <swiftbar.title>Claude Usage Stats</swiftbar.title>
# <swiftbar.version>2.0</swiftbar.version>
# <swiftbar.author>Claude</swiftbar.author>
# <swiftbar.desc>Track Claude Code sessions with weekly and session progress bars</swiftbar.desc>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.environment>[ANTHROPIC_API_KEY=]</swiftbar.environment>

"""
Claude Usage Stats v2 — SwiftBar plugin
────────────────────────────────────────
Shows Claude Code token usage with progress bars matching the
"Settings → Usage" view in Claude.ai desktop.

LIMITS CONFIG
  Edit or create  ~/.claude_usage.json  to set your plan limits:

    {
      "plan":                 "pro",
      "weekly_limit":          1000000,
      "session_window_hours":  5,
      "session_limit":         200000,
      "pricing_input":         3.00,
      "pricing_output":        15.00
    }

  Plan defaults (auto-applied if you set "plan" without explicit limits):
    free   weekly=100K    session=20K
    pro    weekly=1M      session=200K
    team   weekly=2M      session=400K
    max    weekly=5M      session=800K

INSTALL
  1. brew install --cask swiftbar
  2. Open SwiftBar, choose plugin folder (e.g. ~/SwiftBarPlugins)
  3. cp claude_usage.1m.py ~/SwiftBarPlugins/
  4. chmod +x ~/SwiftBarPlugins/claude_usage.1m.py
  5. Click menu bar icon -> Refresh All

OPTIONAL - Anthropic API key for org-level usage
  Right-click plugin icon -> Plugin settings
  Add: ANTHROPIC_API_KEY = sk-ant-...
"""

import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict

# ── Paths & env ───────────────────────────────────────────────────────────────

CLAUDE_DIR  = Path.home() / ".claude" / "projects"
CONFIG_FILE = Path.home() / ".claude_usage.json"
API_KEY     = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Plan defaults ─────────────────────────────────────────────────────────────

PLAN_DEFAULTS = {
    "free": {"weekly_limit":   100_000, "session_limit":  20_000},
    "pro":  {"weekly_limit": 1_000_000, "session_limit": 200_000},
    "team": {"weekly_limit": 2_000_000, "session_limit": 400_000},
    "max":  {"weekly_limit": 5_000_000, "session_limit": 800_000},
}

def load_config() -> dict:
    """Load ~/.claude_usage.json, falling back to Pro defaults."""
    cfg = {
        "plan":                 "pro",
        "weekly_limit":         1_000_000,
        "session_window_hours": 5,
        "session_limit":        200_000,
        "pricing_input":        3.00,
        "pricing_output":       15.00,
    }
    if CONFIG_FILE.exists():
        try:
            user = json.loads(CONFIG_FILE.read_text())
            plan = user.get("plan", "pro").lower()
            if plan in PLAN_DEFAULTS and "weekly_limit" not in user:
                cfg.update(PLAN_DEFAULTS[plan])
            cfg.update(user)
        except Exception:
            pass
    else:
        try:
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2) + "\n")
        except Exception:
            pass
    return cfg

# ── Formatting ────────────────────────────────────────────────────────────────

def fmt_tokens(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n) if n else "0"

def fmt_cost(inp: int, out: int, cfg: dict) -> str:
    c = inp / 1_000_000 * cfg["pricing_input"] + out / 1_000_000 * cfg["pricing_output"]
    if c < 0.0001: return "< $0.0001"
    if c < 0.01:   return f"~${c:.4f}"
    if c < 1.0:    return f"~${c:.3f}"
    return f"~${c:.2f}"

def parse_ts(raw):
    try:
        if isinstance(raw, (int, float)): return datetime.fromtimestamp(raw)
        return datetime.fromisoformat(str(raw)[:19])
    except Exception:
        return datetime.now()

# ── Progress bar ──────────────────────────────────────────────────────────────

BAR_WIDTH = 20

def bar_color(pct: float) -> str:
    if pct >= 0.90: return "#EF4444"
    if pct >= 0.70: return "#F59E0B"
    return "#A78BFA"

def make_bar(used: int, limit: int):
    """Returns (bar_str, pct_float, hex_color)."""
    pct    = min(used / limit, 1.0) if limit > 0 else 0.0
    filled = round(pct * BAR_WIDTH)
    bar    = "\u2588" * filled + "\u2591" * (BAR_WIDTH - filled)
    return bar, pct, bar_color(pct)

# ── Parse local Claude Code sessions ──────────────────────────────────────────

def parse_local(session_window_hours: float = 5.0):
    """
    Walk ~/.claude/projects/**/*.jsonl.
    Returns by_date, projects set, file count, session input/output tokens.
    Session = tokens from the last session_window_hours.
    """
    by_date  = defaultdict(lambda: {"in": 0, "out": 0, "cache_r": 0, "cache_w": 0})
    projects = set()
    n_files  = 0
    sess_in  = 0
    sess_out = 0
    cutoff   = datetime.now() - timedelta(hours=session_window_hours)

    if not CLAUDE_DIR.exists():
        return by_date, projects, n_files, sess_in, sess_out

    for jsonl in CLAUDE_DIR.rglob("*.jsonl"):
        projects.add(jsonl.parent)
        n_files += 1
        try:
            lines = jsonl.read_text(errors="ignore").splitlines()
        except OSError:
            continue

        for raw_line in lines:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                msg = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            ts_raw = msg.get("timestamp") or msg.get("ts") or msg.get("created_at")
            ts     = parse_ts(ts_raw) if ts_raw else datetime.now()
            d      = ts.date()

            usage = msg.get("usage") or {}
            if not usage:
                inner = msg.get("message")
                if isinstance(inner, dict):
                    usage = inner.get("usage") or {}

            inp = int(usage.get("input_tokens")                or 0)
            out = int(usage.get("output_tokens")               or 0)
            cr  = int(usage.get("cache_read_input_tokens")     or 0)
            cw  = int(usage.get("cache_creation_input_tokens") or 0)

            if inp or out:
                by_date[d]["in"]      += inp
                by_date[d]["out"]     += out
                by_date[d]["cache_r"] += cr
                by_date[d]["cache_w"] += cw
                if ts >= cutoff:
                    sess_in  += inp
                    sess_out += out

    return by_date, projects, n_files, sess_in, sess_out

# ── Optional: Anthropic API usage ─────────────────────────────────────────────

def fetch_api_usage():
    if not API_KEY:
        return None
    try:
        import urllib.request
        start = (date.today() - timedelta(days=29)).isoformat()
        url   = f"https://api.anthropic.com/v1/usage?start_date={start}&granularity=day"
        req   = urllib.request.Request(url, headers={
            "x-api-key":         API_KEY,
            "anthropic-version": "2023-06-01",
        })
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"_error": str(e)}

# ── Window aggregation ────────────────────────────────────────────────────────

def window(by_date, start: date, end: date = None):
    end = end or date.today()
    inp = out = cr = cw = 0
    d = start
    while d <= end:
        s    = by_date.get(d, {})
        inp += s.get("in", 0)
        out += s.get("out", 0)
        cr  += s.get("cache_r", 0)
        cw  += s.get("cache_w", 0)
        d   += timedelta(days=1)
    return inp, out, cr, cw

# ── SwiftBar output helpers ───────────────────────────────────────────────────

def ln(text: str, **attrs):
    if attrs:
        print(f"{text} | " + " ".join(f"{k}={v}" for k, v in attrs.items()))
    else:
        print(text)

def progress_section(label: str, used: int, limit: int, cfg: dict):
    """Render a two-line progress block: bar + label with counts."""
    bar, pct, color = make_bar(used, limit)
    pct_str         = f"{pct*100:.0f}%"
    remaining       = max(limit - used, 0)
    ln(f"{bar}  {pct_str}", color=color, font="Menlo", size=11)
    ln(f"{label}   {fmt_tokens(used)} used  ·  {fmt_tokens(remaining)} left  /  {fmt_tokens(limit)}",
       color="#94A3B8", size=11)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()

    today     = date.today()
    yesterday = today - timedelta(days=1)
    week_ago  = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)

    by_date, projects, n_files, sess_in, sess_out = parse_local(
        session_window_hours=cfg["session_window_hours"]
    )

    t_in, t_out, t_cr, t_cw = window(by_date, today)
    y_in, y_out, *_          = window(by_date, yesterday, yesterday)
    w_in, w_out, *_          = window(by_date, week_ago)
    m_in, m_out, *_          = window(by_date, month_ago)

    total_today   = t_in + t_out
    total_week    = w_in + w_out
    total_session = sess_in + sess_out
    total_month   = m_in + m_out

    weekly_limit  = int(cfg["weekly_limit"])
    session_limit = int(cfg["session_limit"])

    w_pct = min(total_week    / weekly_limit,  1.0) if weekly_limit  else 0.0
    s_pct = min(total_session / session_limit, 1.0) if session_limit else 0.0

    # ── Menu bar label ─────────────────────────────────────────────────────────
    dominant_pct = max(w_pct, s_pct)
    col = bar_color(dominant_pct)

    if total_today == 0:
        print("⚡ idle | color=#6B7280")
    else:
        pct_display = f"{dominant_pct*100:.0f}%"
        print(f"⚡ {fmt_tokens(total_today)} · {pct_display} | color={col}")
    print("---")

    # ── Progress bars ──────────────────────────────────────────────────────────
    ln("USAGE LIMITS", color="#F8FAFC", font="Helvetica-Bold", size=10)
    progress_section("weekly  (7 days)", total_week, weekly_limit, cfg)
    print(" ")
    swh = int(cfg["session_window_hours"])
    progress_section(f"session ({swh}h rolling)", total_session, session_limit, cfg)
    ln("Edit ~/.claude_usage.json to change limits",
       color="#475569", size=10)
    print("---")

    # ── Today detail ───────────────────────────────────────────────────────────
    ln("TODAY", color="#F8FAFC", font="Helvetica-Bold", size=10)
    if total_today:
        ln(f"↑ {fmt_tokens(t_in)} input   ↓ {fmt_tokens(t_out)} output",
           color="#CBD5E1", size=12)
        if t_cr or t_cw:
            ln(f"📦 {fmt_tokens(t_cr)} cache read  ·  {fmt_tokens(t_cw)} written",
               color="#94A3B8", size=12)
        ln(fmt_cost(t_in, t_out, cfg) + " estimated", color="#86EFAC", size=12)
    else:
        ln("No activity yet today", color="#64748B", size=12)
    print("---")

    if y_in + y_out:
        ln(f"Yesterday   {fmt_tokens(y_in+y_out)} tokens   {fmt_cost(y_in, y_out, cfg)}",
           color="#94A3B8", size=12)
        print("---")

    ln("LAST 7 DAYS", color="#F8FAFC", font="Helvetica-Bold", size=10)
    if total_week:
        ln(f"{fmt_tokens(total_week)} tokens   {fmt_cost(w_in, w_out, cfg)}",
           color="#CBD5E1", size=12)
    else:
        ln("No activity this week", color="#64748B", size=12)
    print("---")

    ln("LAST 30 DAYS", color="#F8FAFC", font="Helvetica-Bold", size=10)
    if total_month:
        ln(f"{fmt_tokens(total_month)} tokens   {fmt_cost(m_in, m_out, cfg)}",
           color="#CBD5E1", size=12)
    else:
        ln("No activity this month", color="#64748B", size=12)
    print("---")

    ln("CLAUDE CODE", color="#F8FAFC", font="Helvetica-Bold", size=10)
    if CLAUDE_DIR.exists():
        ln(f"{len(projects)} project dir(s)   {n_files} session file(s)",
           color="#94A3B8", size=12)
    else:
        ln("~/.claude/projects not found", color="#EF4444", size=12)
    print("---")

    api = fetch_api_usage()
    if api and "_error" not in api:
        data    = api.get("data") or []
        api_in  = sum(int(d.get("input_tokens") or 0) for d in data)
        api_out = sum(int(d.get("output_tokens") or 0) for d in data)
        ln("API USAGE (30d)", color="#F8FAFC", font="Helvetica-Bold", size=10)
        ln(f"{fmt_tokens(api_in+api_out)} tokens   {fmt_cost(api_in, api_out, cfg)}",
           color="#CBD5E1", size=12)
        print("---")
    elif API_KEY:
        ln("API key set — usage endpoint unavailable", color="#64748B", size=11)
        print("---")
    else:
        ln("Set ANTHROPIC_API_KEY for org-level API usage", color="#64748B", size=11)
        print("---")

    ln(f"Updated {datetime.now().strftime('%H:%M:%S')}   plan: {cfg['plan']}",
       color="#475569", size=10)
    ln("Refresh now", refresh="true", color="#64748B", size=11)


if __name__ == "__main__":
    main()
