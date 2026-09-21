#!/usr/bin/env python3
"""
Build the /ai_usage/ page snapshot from local Claude Code and Codex logs.

Reads (never published):
    ~/.claude/stats-cache.json         Claude Code's own /stats summary
    ~/.codex/sessions/**/*.jsonl       Codex session logs

Writes (published):
    _includes/ai_usage_terminal.html   aggregate counts only — no prompts,
                                       paths, project names or session IDs

Usage:
    python3 _scripts/build_ai_usage.py
"""

import html
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
CLAUDE_STATS = HOME / ".claude" / "stats-cache.json"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "_includes" / "ai_usage_terminal.html"

BAR_WIDTH = 20
HEATMAP_WEEKS = 26


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_tokens(n):
    """Human-readable token count: 1234567 -> '1.2M'."""
    for unit, size in (("B", 1e9), ("M", 1e6), ("k", 1e3)):
        if n >= size:
            return f"{n / size:.1f}{unit}"
    return str(int(n))


def fmt_duration(ms):
    """Milliseconds -> '14d 4h 46m'."""
    minutes = int(ms // 60000)
    d, rem = divmod(minutes, 1440)
    h, m = divmod(rem, 60)
    parts = [f"{d}d"] if d else []
    if d or h:
        parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)


def fmt_hour(h):
    """24h integer -> '9 AM'."""
    suffix = "AM" if h < 12 else "PM"
    return f"{(h % 12) or 12} {suffix}"


def pretty_model(name):
    """'claude-opus-4-8' -> 'Opus 4.8'; non-Claude names pass through."""
    if not name.startswith("claude-"):
        return name
    parts = name.removeprefix("claude-").split("-")
    family = parts[0].capitalize()
    version = ".".join(p for p in parts[1:] if p.isdigit() and len(p) < 3)
    return f"{family} {version}".strip()


def bar(share):
    filled = round(share * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def streaks(active_days):
    """Return (longest, current) run of consecutive active days."""
    days = sorted(active_days)
    longest = run = 0
    prev = None
    for d in days:
        run = run + 1 if prev and d - prev == timedelta(days=1) else 1
        longest = max(longest, run)
        prev = d
    current = 0
    d = date.today()
    if d not in active_days:            # today not over yet; count from yesterday
        d -= timedelta(days=1)
    while d in active_days:
        current += 1
        d -= timedelta(days=1)
    return longest, current


def heatmap(counts_by_day):
    """GitHub-style 7-row grid of the last HEATMAP_WEEKS weeks."""
    shades = " ░▒▓█"
    today = date.today()
    start = today - timedelta(days=today.weekday() + 7 * (HEATMAP_WEEKS - 1))
    nonzero = sorted(v for v in counts_by_day.values() if v > 0)
    # Quartile cut-points so a few huge days don't flatten everything else
    cuts = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)] if nonzero else []

    def shade(v):
        if v <= 0:
            return "·"
        return shades[1 + sum(v > c for c in cuts)]

    rows = []
    for dow, label in enumerate(["Mon", "   ", "Wed", "   ", "Fri", "   ", "Sun"]):
        cells = []
        for w in range(HEATMAP_WEEKS):
            d = start + timedelta(days=7 * w + dow)
            cells.append(" " if d > today else shade(counts_by_day.get(d, 0)))
        rows.append(f"  {label} {''.join(cells)}")
    rows.append(f"      less · ░▒▓█ more   (last {HEATMAP_WEEKS} weeks)")
    return rows


# ---------------------------------------------------------------------------
# Claude Code
# ---------------------------------------------------------------------------

def claude_summary():
    s = json.loads(CLAUDE_STATS.read_text())

    model_tokens = {
        m: u["inputTokens"] + u["outputTokens"]
        + u["cacheReadInputTokens"] + u["cacheCreationInputTokens"]
        for m, u in s["modelUsage"].items()
    }
    model_output = {m: u["outputTokens"] for m, u in s["modelUsage"].items()}

    activity = {date.fromisoformat(d["date"]): d["messageCount"] for d in s["dailyActivity"]}
    hours = {int(h): c for h, c in s["hourCounts"].items()}
    first = datetime.fromisoformat(s["firstSessionDate"].replace("Z", "+00:00")).date()

    return {
        "model_tokens": model_tokens,
        "model_output": model_output,
        "sessions": s["totalSessions"],
        "messages": s["totalMessages"],
        "tool_calls": sum(d.get("toolCallCount", 0) for d in s["dailyActivity"]),
        "longest": fmt_duration(s["longestSession"]["duration"]),
        "longest_msgs": s["longestSession"]["messageCount"],
        "activity": activity,
        "peak_hour": max(hours, key=hours.get) if hours else None,
        "first": first,
        "as_of": s["lastComputedDate"],
    }


# ---------------------------------------------------------------------------
# Codex
# ---------------------------------------------------------------------------

def codex_summary():
    model_tokens = Counter()
    model_output = Counter()
    activity = Counter()             # turns per local day
    hours = Counter()                # sessions started per local hour
    sessions = 0
    turns = 0
    first = last = None

    for path in sorted(CODEX_SESSIONS.rglob("*.jsonl")):
        model = None
        prev_total = prev_out = 0
        started = False

        for line in path.open():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = ev.get("payload") or {}
            ts = ev.get("timestamp")
            local = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone() if ts else None

            if ev.get("type") == "turn_context":
                model = payload.get("model", model)
                turns += 1
                if local:
                    activity[local.date()] += 1
                    if not started:
                        started = True
                        sessions += 1
                        hours[local.hour] += 1
                        first = min(first or local.date(), local.date())
                        last = max(last or local.date(), local.date())

            elif payload.get("type") == "token_count" and payload.get("info"):
                # Cumulative per session; take deltas so repeated events
                # don't double count, and attribute them to the active model.
                total = payload["info"]["total_token_usage"]
                delta = total["total_tokens"] - prev_total
                delta_out = total["output_tokens"] - prev_out
                if delta > 0 and model:
                    model_tokens[model] += delta
                    model_output[model] += max(delta_out, 0)
                prev_total, prev_out = total["total_tokens"], total["output_tokens"]

    longest, current = streaks(set(activity))
    return {
        "model_tokens": dict(model_tokens),
        "model_output": dict(model_output),
        "sessions": sessions,
        "turns": turns,
        "activity": dict(activity),
        "peak_hour": max(hours, key=hours.get) if hours else None,
        "first": first,
        "last": last,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def kv(pairs):
    """Two-column key/value lines."""
    return [f"  {k + ':':<18}{v}" for k, v in pairs]


def model_lines(model_tokens, model_output):
    total = sum(model_tokens.values()) or 1
    ranked = sorted(model_tokens.items(), key=lambda kv_: kv_[1], reverse=True)
    width = max((len(pretty_model(m)) for m, _ in ranked), default=0)
    lines = []
    for m, t in ranked:
        share = t / total
        if share < 0.001:
            continue
        lines.append(
            f"  {pretty_model(m):<{width}}  {bar(share)} {share * 100:5.1f}%"
            f"  {fmt_tokens(t):>6}  (out {fmt_tokens(model_output.get(m, 0))})"
        )
    return lines


def block(command, lines):
    body = "\n".join(html.escape(l) for l in lines)
    return (
        '<div class="term">\n'
        '  <div class="term-bar"><span></span><span></span><span></span></div>\n'
        f'<pre><span class="prompt">❯</span> {html.escape(command)}\n\n{body}\n</pre>\n'
        "</div>\n"
    )


def render(claude, codex):
    today = date.today()
    out = []

    # ---- Claude Code --------------------------------------------------------
    c_fav = max(claude["model_tokens"], key=claude["model_tokens"].get)
    c_days = len(claude["activity"])
    c_span = (today - claude["first"]).days + 1
    c_long, c_cur = streaks(set(claude["activity"]))
    lines = ["  Claude Code · Overview", ""]
    lines += kv([
        ("Favorite model", pretty_model(c_fav)),
        ("Total tokens", fmt_tokens(sum(claude["model_tokens"].values())) + "  (incl. cache)"),
        ("Sessions", f"{claude['sessions']:,}"),
        ("Messages", f"{claude['messages']:,}"),
        ("Tool calls", f"{claude['tool_calls']:,}"),
        ("Longest session", f"{claude['longest']}  ({claude['longest_msgs']:,} msgs)"),
        ("Active days", f"{c_days}/{c_span}"),
        ("Longest streak", f"{c_long} days"),
        ("Current streak", f"{c_cur} days"),
        ("Most active hour", fmt_hour(claude["peak_hour"])),
        ("Using since", claude["first"].strftime("%b %d, %Y")),
    ])
    lines += ["", "  Models", ""] + model_lines(claude["model_tokens"], claude["model_output"])
    lines += ["", "  Activity (messages/day)", ""] + heatmap(claude["activity"])
    out.append(block("claude /stats", lines))

    # ---- Codex --------------------------------------------------------------
    if codex["sessions"]:
        x_fav = max(codex["model_tokens"], key=codex["model_tokens"].get)
        x_span = (today - codex["first"]).days + 1
        x_long, x_cur = streaks(set(codex["activity"]))
        lines = ["  Codex · Overview", ""]
        lines += kv([
            ("Favorite model", x_fav),
            ("Total tokens", fmt_tokens(sum(codex["model_tokens"].values())) + "  (incl. cache)"),
            ("Sessions", f"{codex['sessions']:,}"),
            ("Turns", f"{codex['turns']:,}"),
            ("Active days", f"{len(codex['activity'])}/{x_span}"),
            ("Longest streak", f"{x_long} days"),
            ("Current streak", f"{x_cur} days"),
            ("Most active hour", fmt_hour(codex["peak_hour"])),
            ("Using since", codex["first"].strftime("%b %d, %Y")),
        ])
        lines += ["", "  Models", ""] + model_lines(codex["model_tokens"], codex["model_output"])
        lines += ["", "  Activity (turns/day)", ""] + heatmap(codex["activity"])
        out.append(block("codex /status", lines))

    stamp = (
        f'<p class="term-note">Snapshot generated {today:%b %d, %Y} from local logs '
        f"(Claude Code stats as of {claude['as_of']}). Aggregate counts only.</p>\n"
    )
    return "<!-- Generated by _scripts/build_ai_usage.py — do not edit by hand -->\n" + "".join(out) + stamp


def main():
    claude = claude_summary()
    codex = codex_summary() if CODEX_SESSIONS.exists() else {"sessions": 0}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(claude, codex))
    print(f"Wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
