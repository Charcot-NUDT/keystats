# Keystats

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.7%2B-green.svg)]()

> A lightweight, privacy-respecting keyboard activity monitor for Linux.

Keystats runs silently in the background, counting every keypress you make throughout the day. It tracks **per-key statistics** (which keys you press and how often), hourly breakdowns, daily trends, and more — all stored locally in SQLite. Your typing content is **never recorded**, only counts.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [From .deb Package (Recommended)](#from-deb-package-recommended)
  - [From Source](#from-source)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [Daily Summary](#daily-summary)
  - [Per-Key Breakdown](#per-key-breakdown)
  - [Weekly Trends](#weekly-trends)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [Privacy](#privacy)
- [Development](#development)
- [License](#license)

---

## Features

- **Per-Key Statistics** — See exactly which keys you press most (A, Enter, Space, Backspace...)
- **Daily Keystroke Count** — Total keypresses per day
- **Hourly Breakdown** — 24-hour activity heatmap to find your peak productivity hours
- **Weekly Trends** — Compare activity across the last 7 days
- **All-Time Leaderboard** — Your most active days ever
- **Typing Streak** — Consecutive days with typing activity
- **Privacy-First Design** — Only counts are stored; **what you type is never recorded**
- **Local Storage** — All data stays in a local SQLite database
- **Systemd Integration** — Auto-starts on boot, runs as a system service
- **Lightweight** — ~10MB RAM footprint, minimal CPU usage

---

## Screenshots

### Daily Summary
```
==================================================
  DAILY KEYBOARD SUMMARY
  Sunday, May 17, 2026
==================================================

  TODAY
    Keystrokes: 12,847
    vs Yesterday: +3,210 (+33.3%)
    Est. Words: ~2,569
    Est. Avg WPM: ~36

  TOP KEYS TODAY
    1. Space              2,341  ████████████████████
    2. A                  1,892  ████████████████
    3. E                  1,543  █████████████
    4. Enter                987  ████████
    5. Backspace            654  █████
    ...
```

### Per-Key Breakdown
```
==================================================
  KEY BREAKDOWN - Sunday, May 17, 2026
==================================================

  TOP KEYS (of 62 unique)
    Key                  |    Count |     % | Bar
    ---------------------+----------+-------+--------------------
    Space                |    2,341 | 18.2% | ██████████
    A                    |    1,892 | 14.7% | ████████
    E                    |    1,543 | 12.0% | ██████
    Enter                |      987 |  7.7% | ████
    Backspace            |      654 |  5.1% | ██
    ...

  Total tracked: 12,847 keystrokes
  Unique keys: 62
==================================================
```

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux (Ubuntu/Debian recommended) |
| Kernel | 2.6+ (evdev support required) |
| Python | 3.7 or higher |
| Dependencies | `python3-evdev`, `systemd` |
| Permissions | Root access (for `/dev/input/event*` access) |

### Supported Distributions

- Ubuntu 18.04+ 
- Debian 10+
- Linux Mint 19+
- Any Debian-based distro with systemd

> **Note for other distros**: The `.deb` package is Debian-specific. For Arch, Fedora, etc., use the [manual installation](#from-source) method.

---

## Installation

### From .deb Package (Recommended)

1. **Download the latest release**
   ```bash
   wget https://github.com/yourusername/keystats/releases/download/v1.0.0/keystats_1.0.0_all.deb
   ```

2. **Install the package**
   ```bash
   sudo dpkg -i keystats_1.0.0_all.deb
   ```

3. **Fix any missing dependencies**
   ```bash
   sudo apt-get install -f
   ```

4. **Start the service**
   ```bash
   sudo systemctl start keystats
   sudo systemctl enable keystats   # Auto-start on boot
   ```

5. **Verify it's running**
   ```bash
   sudo systemctl status keystats
   ```

### From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/keystats.git
   cd keystats
   ```

2. **Install dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-evdev python3-pip
   ```

3. **Install the package manually**
   ```bash
   sudo mkdir -p /usr/lib/keystats
   sudo cp keystats/usr/lib/keystats/*.py /usr/lib/keystats/
   sudo cp keystats/usr/bin/keystats-* /usr/bin/
   sudo chmod +x /usr/bin/keystats-*
   
   # Create directories
   sudo mkdir -p /var/lib/keystats /var/log/keystats
   sudo chmod 777 /var/lib/keystats /var/log/keystats
   
   # Install systemd service
   sudo cp keystats/etc/systemd/system/keystats.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable keystats
   sudo systemctl start keystats
   ```

---

## Usage

### CLI Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `keystats-cli` | — | Show today's total keystroke count |
| `keystats-cli summary` | `s` | Detailed daily summary with insights |
| `keystats-cli keys` | `k` | Per-key breakdown for today |
| `keystats-cli allkeys` | `ak` | All-time per-key statistics |
| `keystats-cli week` | `w` | Last 7 days activity |
| `keystats-cli top` | `t` | Top 10 most active days |
| `keystats-cli date YYYY-MM-DD` | — | Stats for a specific date |
| `keystats-cli help` | `-h` | Show help message |

### Daily Summary

```bash
$ keystats-cli summary

==================================================
  DAILY KEYBOARD SUMMARY
  Sunday, May 17, 2026
==================================================

  TODAY
    Keystrokes: 12,847
    vs Yesterday: +3,210 (+33.3%)
    Est. Words: ~2,569
    Est. Avg WPM: ~36

  THIS WEEK (7 days)
    Total Keystrokes: 78,234
    Daily Average: 11,176

  ALL TIME
    Total Keystrokes: 456,789
    Daily Average: 9,135
    Current Streak: 12 days

  PEAK ACTIVITY TODAY
    Busiest Hour: 14:00-15:00 (2,341 strokes)

  TOP KEYS TODAY
    1. Space              2,341  ████████████████████
    2. A                  1,892  ████████████████
    3. E                  1,543  █████████████
    4. Enter                987  ████████
    5. Backspace            654  █████
    ...

  HOURLY BREAKDOWN
    Hour |      Count | Bar
    -------+------------+--------------------------------
    00:00 |          0 |
    01:00 |          0 |
    ...
    14:00 |      2,341 | ████████████████████████████ *
    ...

  ASSESSMENT
    Heavy typing day! Your fingers are working hard.
    On fire! 12-day streak!
==================================================
```

### Per-Key Breakdown

```bash
$ keystats-cli keys
```

Shows every key you've pressed today, sorted by frequency, with percentage and visual bar chart.

### All-Time Key Statistics

```bash
$ keystats-cli allkeys
```

Aggregates key usage across all recorded days, showing your lifetime typing patterns.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  /dev/input/    │     │  keystats-daemon │     │  SQLite DB  │
│  event*         │────▶│  (python3)       │────▶│  /var/lib/  │
│  (kernel)       │     │                  │     │  keystats/  │
└─────────────────┘     └──────────────────┘     └─────────────┘
                                │                        ▲
                                ▼                        │
                       ┌──────────────────┐              │
                       │  systemd service │              │
                       │  (auto-start)    │              │
                       └──────────────────┘              │
                                                         │
┌─────────────────┐     ┌──────────────────┐            │
│  User           │     │  keystats-cli    │────────────┘
│  (terminal)     │────▶│  (python3)       │
└─────────────────┘     └──────────────────┘
```

### Data Flow

1. **keystats-daemon** reads raw input events from Linux evdev (`/dev/input/event*`)
2. Events are parsed to extract key codes and mapped to human-readable key names
3. Keypresses are buffered in memory and flushed to SQLite every 3 seconds
4. **keystats-cli** queries the database to display statistics

### Components

| File | Purpose |
|------|---------|
| `daemon.py` | Background service that captures keyboard events |
| `db.py` | SQLite database operations |
| `cli.py` | Command-line interface for viewing statistics |
| `keystats-daemon` | Wrapper script to launch the daemon |
| `keystats-cli` | Wrapper script to launch the CLI |

---

## Database Schema

Keystats uses SQLite with three tables:

### `keystats` — Daily totals
| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT (PK) | Date in YYYY-MM-DD format |
| `key_count` | INTEGER | Total keypresses for the day |
| `created_at` | TEXT | First record timestamp |
| `updated_at` | TEXT | Last update timestamp |

### `hourly_stats` — Hourly breakdown
| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT | Date in YYYY-MM-DD format |
| `hour` | INTEGER | Hour of day (0-23) |
| `key_count` | INTEGER | Keypresses in that hour |
| *(unique: date + hour)* |

### `key_type_stats` — Per-key statistics
| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT | Date in YYYY-MM-DD format |
| `key_type` | TEXT | Key name (e.g., `KEY_A`, `KEY_ENTER`) |
| `key_count` | INTEGER | Times that key was pressed |
| *(unique: date + key_type)* |

### Database Location

```
/var/lib/keystats/keystats.db
```

You can inspect it directly with SQLite:
```bash
sqlite3 /var/lib/keystats/keystats.db "SELECT * FROM keystats ORDER BY date DESC LIMIT 5;"
```

---

## Configuration

### Service Management

```bash
# Start/stop/restart
sudo systemctl start keystats
sudo systemctl stop keystats
sudo systemctl restart keystats

# Enable/disable auto-start
sudo systemctl enable keystats
sudo systemctl disable keystats

# View status
sudo systemctl status keystats

# View logs
sudo journalctl -u keystats -f
sudo cat /var/log/keystats/daemon.log
```

### Log Files

| File | Description |
|------|-------------|
| `/var/log/keystats/daemon.log` | Daemon activity log |
| `/var/lib/keystats/keystats.db` | SQLite database |

### Flush Interval

By default, keystrokes are flushed to the database every **3 seconds**. You can modify `flush_interval` in `/usr/lib/keystats/daemon.py` if needed.

---

## Troubleshooting

### Service won't start

```bash
# Check the error
sudo journalctl -xeu keystats.service --no-pager

# Common causes:
# 1. Missing python3-evdev
sudo apt-get install python3-evdev

# 2. Permission denied on /dev/input
sudo usermod -a -G input $USER
# Then log out and back in

# 3. Database permission issues
sudo chmod 777 /var/lib/keystats
sudo chmod 666 /var/lib/keystats/keystats.db
```

### No keyboard devices found

```bash
# Check if devices exist
ls -la /dev/input/event*

# Check if your user can access them
python3 -c "from evdev import list_devices; print(list_devices())"

# If empty, you may need to add your user to the input group
sudo usermod -a -G input $USER
```

### Keystrokes not being recorded

1. Check service is running: `sudo systemctl status keystats`
2. Check the log: `sudo cat /var/log/keystats/daemon.log`
3. Verify the database: `sqlite3 /var/lib/keystats/keystats.db "SELECT * FROM keystats;"`

### High CPU or memory usage

Keystats is designed to be lightweight. If you observe high resource usage:

- Check the log for error loops
- Restart the service: `sudo systemctl restart keystats`
- Consider increasing the `flush_interval` in daemon.py

---

## Uninstallation

### Remove the package

```bash
# Keep data
sudo apt remove keystats

# Remove everything including data
sudo apt purge keystats
```

### Manual cleanup (if installed from source)

```bash
sudo systemctl stop keystats
sudo systemctl disable keystats
sudo rm -f /etc/systemd/system/keystats.service
sudo rm -f /usr/bin/keystats-daemon /usr/bin/keystats-cli
sudo rm -rf /usr/lib/keystats
sudo rm -rf /var/lib/keystats
sudo rm -rf /var/log/keystats
sudo systemctl daemon-reload
```

---

## Privacy

**Keystats does NOT record what you type.** It only counts:

- How many times each key is pressed
- When keys are pressed (hourly aggregation)
- Daily totals

The actual content of your keystrokes (passwords, messages, code) is **never stored, never transmitted, and never accessible** to Keystats or anyone else. All data remains in a local SQLite database on your machine.

---

## Development

### Project Structure

```
keystats/
├── DEBIAN/
│   ├── control           # Package metadata
│   ├── postinst          # Post-installation script
│   ├── prerm             # Pre-removal script
│   └── postrm            # Post-removal script
├── etc/
│   └── systemd/system/
│       └── keystats.service
├── usr/
│   ├── bin/
│   │   ├── keystats-cli       # CLI wrapper
│   │   └── keystats-daemon    # Daemon wrapper
│   └── lib/keystats/
│       ├── __init__.py
│       ├── daemon.py          # Core daemon
│       ├── db.py              # Database layer
│       └── cli.py             # CLI interface
└── var/
    └── lib/keystats/          # Database directory
```

### Building the .deb Package

```bash
# Install build tools
sudo apt-get install dpkg-dev

# Build
cd keystats-project
dpkg-deb --build keystats

# Verify
dpkg-deb --info keystats_1.0.0_all.deb
dpkg-deb --contents keystats_1.0.0_all.deb
```

### Running in Debug Mode

```bash
# Run daemon in foreground (no systemd)
sudo /usr/bin/keystats-daemon --foreground

# Or directly with Python
sudo python3 /usr/lib/keystats/daemon.py --foreground
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with [python-evdev](https://github.com/gvalkov/python-evdev) for Linux input event handling
- Inspired by the desire to understand personal productivity patterns
