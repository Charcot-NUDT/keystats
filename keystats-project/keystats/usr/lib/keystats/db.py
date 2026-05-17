#!/usr/bin/env python3
"""
keystats - Lightweight keyboard statistics database module.
Uses SQLite for minimal resource footprint.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from pathlib import Path

DB_DIR = "/var/lib/keystats"
DB_PATH = os.path.join(DB_DIR, "keystats.db")


def init_db():
    """Initialize the SQLite database with required tables."""
    os.makedirs(DB_DIR, exist_ok=True, mode=0o777)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keystats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            key_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hour INTEGER NOT NULL,
            key_count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(date, hour)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS key_type_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            key_type TEXT NOT NULL,
            key_count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(date, key_type)
        )
    """)

    conn.commit()
    conn.close()


def _get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def increment_keypress(key_type="general"):
    """
    Increment the keypress count for today.
    Call this on every keypress event.
    """
    today = date.today().isoformat()
    now = datetime.now().isoformat()
    hour = datetime.now().hour

    conn = _get_connection()
    cursor = conn.cursor()

    try:
        # Update daily count
        cursor.execute("""
            INSERT INTO keystats (date, key_count, created_at, updated_at)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                key_count = key_count + 1,
                updated_at = ?
        """, (today, now, now, now))

        # Update hourly count
        cursor.execute("""
            INSERT INTO hourly_stats (date, hour, key_count)
            VALUES (?, ?, 1)
            ON CONFLICT(date, hour) DO UPDATE SET
                key_count = key_count + 1
        """, (today, hour))

        # Update key type count
        cursor.execute("""
            INSERT INTO key_type_stats (date, key_type, key_count)
            VALUES (?, ?, 1)
            ON CONFLICT(date, key_type) DO UPDATE SET
                key_count = key_count + 1
        """, (today, key_type))

        conn.commit()
    except sqlite3.Error as e:
        pass  # Silently fail to avoid disrupting typing
    finally:
        conn.close()


def get_today_stats():
    """Get today's keypress statistics."""
    today = date.today().isoformat()
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT key_count FROM keystats WHERE date = ?",
        (today,)
    )
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0


def get_stats_by_date(target_date):
    """Get keypress count for a specific date (YYYY-MM-DD)."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT key_count FROM keystats WHERE date = ?",
        (target_date,)
    )
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0


def get_range_stats(start_date, end_date):
    """Get statistics for a date range."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, key_count FROM keystats
        WHERE date >= ? AND date <= ?
        ORDER BY date DESC
    """, (start_date, end_date))

    results = cursor.fetchall()
    conn.close()

    return results


def get_all_time_total():
    """Get the all-time total keypress count."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(key_count) FROM keystats")
    row = cursor.fetchone()
    conn.close()

    return row[0] if row and row[0] else 0


def get_daily_average():
    """Get the daily average keypress count."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(key_count), COUNT(*) FROM keystats
        WHERE key_count > 0
    """)
    row = cursor.fetchone()
    conn.close()

    return row[0] if row and row[0] else 0


def get_hourly_breakdown(target_date=None):
    """Get hourly keypress breakdown for a date."""
    if target_date is None:
        target_date = date.today().isoformat()

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hour, key_count FROM hourly_stats
        WHERE date = ?
        ORDER BY hour
    """, (target_date,))

    results = cursor.fetchall()
    conn.close()

    # Fill in missing hours with 0
    hourly = {h: 0 for h in range(24)}
    for h, count in results:
        hourly[h] = count
    return hourly


def get_top_days(limit=10):
    """Get the top N most active days."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, key_count FROM keystats
        ORDER BY key_count DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()

    return results


def get_weekly_summary():
    """Get a summary of the last 7 days."""
    from datetime import timedelta

    today = date.today()
    week_ago = (today - timedelta(days=6)).isoformat()
    today_str = today.isoformat()

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, key_count FROM keystats
        WHERE date >= ? AND date <= ?
        ORDER BY date DESC
    """, (week_ago, today_str))

    results = cursor.fetchall()
    conn.close()

    return results


def get_streak():
    """Calculate the current daily typing streak."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, key_count FROM keystats
        WHERE key_count > 0
        ORDER BY date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    check_date = date.today()

    for row_date_str, count in rows:
        row_date = date.fromisoformat(row_date_str)
        if row_date == check_date and count > 0:
            streak += 1
            check_date -= timedelta(days=1)
        elif row_date == check_date + timedelta(days=1):
            continue
        else:
            break

    return streak


def get_key_stats(target_date=None, limit=30):
    """Get per-key statistics for a specific date."""
    if target_date is None:
        target_date = date.today().isoformat()

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT key_type, key_count FROM key_type_stats
        WHERE date = ?
        ORDER BY key_count DESC
        LIMIT ?
    """, (target_date, limit))

    results = cursor.fetchall()
    conn.close()

    return results


def get_all_time_key_stats(limit=30):
    """Get all-time per-key statistics aggregated across all days."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT key_type, SUM(key_count) as total
        FROM key_type_stats
        GROUP BY key_type
        ORDER BY total DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()

    return results
