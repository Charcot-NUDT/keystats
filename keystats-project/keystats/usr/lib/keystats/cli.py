#!/usr/bin/env python3
"""
keystats-cli - Command-line interface for viewing keyboard statistics.
"""

import sys
import os
from datetime import datetime, date, timedelta

# Ensure we can import the db module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import (
    init_db,
    get_today_stats,
    get_stats_by_date,
    get_range_stats,
    get_all_time_total,
    get_daily_average,
    get_hourly_breakdown,
    get_top_days,
    get_weekly_summary,
    get_streak,
    get_key_stats,
    get_all_time_key_stats,
)


def format_number(n):
    """Format large numbers with commas."""
    if n is None:
        return "0"
    return f"{int(n):,}"


def show_today():
    """Show today's statistics."""
    count = get_today_stats()
    print(f"\n{'='*50}")
    print(f"  TODAY'S KEYBOARD ACTIVITY")
    print(f"{'='*50}")
    print(f"  Date: {date.today().strftime('%A, %B %d, %Y')}")
    print(f"  Keystrokes: {format_number(count)}")
    print(f"{'='*50}\n")


def show_summary():
    """Show daily summary with insights."""
    today = date.today()
    today_str = today.isoformat()

    today_count = get_today_stats()
    all_time = get_all_time_total()
    avg = get_daily_average()
    streak = get_streak()

    # Get yesterday for comparison
    yesterday = (today - timedelta(days=1)).isoformat()
    yesterday_count = get_stats_by_date(yesterday)

    # Get weekly data
    weekly = get_weekly_summary()
    weekly_total = sum(c for _, c in weekly)
    weekly_days = len(weekly)

    # Peak hour
    hourly = get_hourly_breakdown()
    peak_hour = max(hourly, key=hourly.get)
    peak_count = hourly[peak_hour]

    # Top keys today
    top_keys = get_key_stats(today_str, limit=10)

    print(f"\n{'='*50}")
    print(f"  DAILY KEYBOARD SUMMARY")
    print(f"  {today.strftime('%A, %B %d, %Y')}")
    print(f"{'='*50}")

    print(f"\n  TODAY")
    print(f"    Keystrokes: {format_number(today_count)}")

    if yesterday_count > 0:
        diff = today_count - yesterday_count
        pct = (diff / yesterday_count) * 100 if yesterday_count > 0 else 0
        if diff >= 0:
            print(f"    vs Yesterday: +{format_number(diff)} ({pct:+.1f}%)")
        else:
            print(f"    vs Yesterday: {format_number(diff)} ({pct:+.1f}%)")
    else:
        print(f"    vs Yesterday: No data")

    # WPM estimate (average word = 5 chars, avg typing session = active hours)
    active_hours = sum(1 for c in hourly.values() if c > 0)
    if today_count > 0 and active_hours > 0:
        est_words = today_count // 5
        est_wpm = today_count // max(active_hours * 60, 1)
        print(f"    Est. Words: ~{format_number(est_words)}")
        print(f"    Est. Avg WPM: ~{est_wpm}")

    print(f"\n  THIS WEEK ({weekly_days} days)")
    print(f"    Total Keystrokes: {format_number(weekly_total)}")
    print(f"    Daily Average: {format_number(weekly_total // max(weekly_days, 1))}")

    print(f"\n  ALL TIME")
    print(f"    Total Keystrokes: {format_number(all_time)}")
    print(f"    Daily Average: {format_number(int(avg))}")
    print(f"    Current Streak: {streak} day{'s' if streak != 1 else ''}")

    print(f"\n  PEAK ACTIVITY TODAY")
    print(f"    Busiest Hour: {peak_hour}:00-{peak_hour+1}:00 ({format_number(peak_count)} strokes)")

    # Top keys
    if top_keys:
        print(f"\n  TOP KEYS TODAY")
        for i, (key_name, count) in enumerate(top_keys[:8], 1):
            display_name = key_name.replace("KEY_", "")
            bar = "█" * min(int(count / max(top_keys[0][1], 1) * 20), 20)
            print(f"    {i}. {display_name:<15} {format_number(count):>6}  {bar}")

    # Simple bar chart for hourly activity
    print(f"\n  HOURLY BREAKDOWN")
    print(f"    {'Hour':>6} | {'Count':>10} | Bar")
    print(f"    {'-'*6}-+-{'-'*10}-+{'-'*30}")
    max_count = max(hourly.values()) if hourly.values() else 1
    for h in range(24):
        count = hourly.get(h, 0)
        bar = "█" * int((count / max(max_count, 1)) * 25) if count > 0 else ""
        marker = " *" if h == datetime.now().hour else ""
        print(f"    {h:02d}:00 | {format_number(count):>10} | {bar}{marker}")

    # Mood/activity assessment
    print(f"\n  ASSESSMENT")
    if today_count > 10000:
        print(f"    Heavy typing day! Your fingers are working hard.")
    elif today_count > 5000:
        print(f"    Productive day with solid typing activity.")
    elif today_count > 1000:
        print(f"    Moderate activity today.")
    elif today_count > 0:
        print(f"    Light typing day. Taking it easy?")
    else:
        print(f"    No typing recorded yet today.")

    if streak >= 7:
        print(f"    On fire! {streak}-day streak!")
    elif streak >= 3:
        print(f"    Nice {streak}-day consistency streak!")

    print(f"{'='*50}\n")


def show_weekly():
    """Show last 7 days of activity."""
    weekly = get_weekly_summary()

    print(f"\n{'='*50}")
    print(f"  LAST 7 DAYS ACTIVITY")
    print(f"{'='*50}\n")

    if not weekly:
        print("  No data available.\n")
        return

    max_count = max(c for _, c in weekly)
    total = 0

    for date_str, count in weekly:
        d = date.fromisoformat(date_str)
        day_name = d.strftime("%a")
        bar = "█" * int((count / max(max_count, 1)) * 30) if count > 0 else ""
        marker = " TODAY" if d == date.today() else ""
        print(f"  {d.isoformat()} {day_name} | {format_number(count):>8} | {bar}{marker}")
        total += count

    avg = total // len(weekly)
    print(f"\n  Total: {format_number(total)} | Average: {format_number(avg)}/day")
    print(f"{'='*50}\n")


def show_top():
    """Show top 10 most active days."""
    top = get_top_days(10)

    print(f"\n{'='*50}")
    print(f"  TOP 10 MOST ACTIVE DAYS")
    print(f"{'='*50}\n")

    if not top:
        print("  No data available.\n")
        return

    for i, (date_str, count) in enumerate(top, 1):
        d = date.fromisoformat(date_str)
        day_name = d.strftime("%A, %B %d, %Y")
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
        print(f"  {medal} #{i} {day_name} - {format_number(count)} keystrokes")

    print(f"{'='*50}\n")


def show_date(target_date):
    """Show stats for a specific date."""
    try:
        d = date.fromisoformat(target_date)
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD.")
        return

    count = get_stats_by_date(target_date)
    day_name = d.strftime("%A, %B %d, %Y")

    print(f"\n  {day_name}: {format_number(count)} keystrokes\n")


def show_key_stats():
    """Show per-key statistics for today."""
    today = date.today()
    today_str = today.isoformat()

    keys = get_key_stats(today_str, limit=50)

    print(f"\n{'='*50}")
    print(f"  KEY BREAKDOWN - {today.strftime('%A, %B %d, %Y')}")
    print(f"{'='*50}")

    if not keys:
        print("\n  No key data available yet.")
        print(f"{'='*50}\n")
        return

    total = sum(c for _, c in keys)

    # Top 20 with bar chart
    print(f"\n  TOP KEYS (of {len(keys)} unique)")
    print(f"    {'Key':<20} | {'Count':>8} | {'%':>5} | Bar")
    print(f"    {'-'*20}-+-{'-'*8}-+-{'-'*5}-+{'-'*20}")

    for i, (key_name, count) in enumerate(keys[:20], 1):
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 2) if pct > 0 else ""
        # Clean up key name display
        display_name = key_name.replace("KEY_", "")
        print(f"    {display_name:<20} | {format_number(count):>8} | {pct:4.1f}% | {bar}")

    if len(keys) > 20:
        others = sum(c for _, c in keys[20:])
        others_pct = (others / total * 100) if total > 0 else 0
        print(f"    {'(others)':<20} | {format_number(others):>8} | {others_pct:4.1f}% |")

    print(f"\n  Total tracked: {format_number(total)} keystrokes")
    print(f"  Unique keys: {len(keys)}")
    print(f"{'='*50}\n")


def show_all_time_keys():
    """Show all-time per-key statistics."""
    keys = get_all_time_key_stats(limit=30)

    print(f"\n{'='*50}")
    print(f"  ALL-TIME KEY STATISTICS")
    print(f"{'='*50}")

    if not keys:
        print("\n  No key data available yet.")
        print(f"{'='*50}\n")
        return

    total = sum(c for _, c in keys)

    print(f"\n  TOP KEYS (all time)")
    print(f"    {'Key':<20} | {'Count':>10} | {'%':>5} | Bar")
    print(f"    {'-'*20}-+-{'-'*10}-+-{'-'*5}-+{'-'*20}")

    for i, (key_name, count) in enumerate(keys[:20], 1):
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 2) if pct > 0 else ""
        display_name = key_name.replace("KEY_", "")
        print(f"    {display_name:<20} | {format_number(count):>10} | {pct:4.1f}% | {bar}")

    print(f"\n  Total tracked: {format_number(total)} keystrokes")
    print(f"  Unique keys: {len(keys)}")
    print(f"{'='*50}\n")


def show_help():
    """Show help message."""
    print(f"""
keystats-cli - View your keyboard activity statistics

Usage:
    keystats-cli              Show today's count
    keystats-cli summary      Show detailed daily summary
    keystats-cli keys         Show today's per-key breakdown
    keystats-cli allkeys      Show all-time per-key statistics
    keystats-cli week         Show last 7 days
    keystats-cli top          Show top 10 active days
    keystats-cli date YYYY-MM-DD  Show specific date
    keystats-cli help         Show this help

The keystats daemon must be running to collect data.
Start it with: sudo systemctl start keystats
""")


def main():
    """Main CLI entry point."""
    init_db()

    args = sys.argv[1:]

    if not args:
        show_today()
    elif args[0] in ("summary", "s"):
        show_summary()
    elif args[0] in ("keys", "k"):
        show_key_stats()
    elif args[0] in ("allkeys", "ak"):
        show_all_time_keys()
    elif args[0] in ("week", "w"):
        show_weekly()
    elif args[0] in ("top", "t"):
        show_top()
    elif args[0] == "date" and len(args) > 1:
        show_date(args[1])
    elif args[0] in ("help", "-h", "--help"):
        show_help()
    else:
        print(f"Unknown command: {args[0]}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
