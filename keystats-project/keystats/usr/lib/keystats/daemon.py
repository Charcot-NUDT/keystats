#!/usr/bin/env python3
"""keystats-daemon - Keyboard statistics daemon. Uses python-evdev."""

import os, sys, time, signal, struct, select, logging, sqlite3
from datetime import datetime, date
from evdev import InputDevice, categorize, ecodes, list_devices

# ======== Config ========
LOG_DIR = "/var/log/keystats"
DB_DIR = "/var/lib/keystats"
DB_PATH = os.path.join(DB_DIR, "keystats.db")

# ======== Logging ========
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, "daemon.log"))],
)
logger = logging.getLogger("keystats")

# ======== DB ========
def init_db():
    os.makedirs(DB_DIR, exist_ok=True, mode=0o777)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keystats (
            date TEXT UNIQUE NOT NULL,
            key_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS hourly_stats (
            date TEXT NOT NULL, hour INTEGER NOT NULL,
            key_count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(date, hour)
        )
    """)
    conn.commit()
    conn.close()

def add_keystrokes(n=1, key_types=None):
    if n <= 0: return
    today = date.today().isoformat()
    now = datetime.now().isoformat()
    hour = datetime.now().hour
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Insert or update daily total (add n keypresses)
        c.execute("""
            INSERT INTO keystats(date,key_count,created_at,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(date) DO UPDATE SET key_count=key_count+?, updated_at=?
        """, (today, n, now, now, n, now))
        # Insert or update hourly total (add n keypresses)
        c.execute("""
            INSERT INTO hourly_stats(date,hour,key_count) VALUES(?,?,?)
            ON CONFLICT(date,hour) DO UPDATE SET key_count=key_count+?
        """, (today, hour, n, n))
        # Insert or update per-key-type counts
        if key_types:
            for key_name, count in key_types.items():
                c.execute("""
                    INSERT INTO key_type_stats(date,key_type,key_count)
                    VALUES(?,?,?)
                    ON CONFLICT(date,key_type) DO UPDATE SET
                        key_count=key_count+?
                """, (today, key_name, count, count))
        conn.commit()
    except Exception as e:
        logger.error("DB: %s", e)
    finally:
        conn.close()

# ======== Device Discovery (using evdev) ========
def find_keyboards():
    """Find keyboard devices using python-evdev."""
    devices = []
    for path in list_devices():
        try:
            dev = InputDevice(path)
            # Check if device has key capabilities
            caps = dev.capabilities()
            if ecodes.EV_KEY in caps:
                # Filter out mice (they also have EV_KEY but few keys)
                key_count = len(caps[ecodes.EV_KEY])
                if key_count > 50:  # Keyboards have 100+ keys, mice have ~3
                    devices.append(path)
                    logger.info("Found keyboard: %s (%s, %d keys)", path, dev.name, key_count)
            dev.close()
        except (PermissionError, OSError) as e:
            logger.debug("Cannot access %s: %s", path, e)
        except Exception as e:
            logger.debug("Error checking %s: %s", path, e)
    return devices

# ======== Main Loop ========
def run():
    logger.info("=" * 50)
    logger.info("Keystats daemon starting (PID: %d)", os.getpid())

    running = True
    def on_signal(signum, frame):
        nonlocal running
        logger.info("Signal %d received", signum)
        running = False
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    init_db()
    logger.info("Database ready: %s", DB_PATH)

    fds = {}
    key_buffer = 0
    key_type_buffer = {}  # key_name -> count
    last_flush = time.time()
    flush_interval = 3  # flush every 3 seconds for near-real-time
    scan_interval = 30
    last_scan = 0

    while running:
        # (Re)discover devices if needed
        if not fds or time.time() - last_scan > scan_interval:
            # Close old devices
            for fd, dev in list(fds.items()):
                try: dev.close()
                except: pass
            fds.clear()

            paths = find_keyboards()
            last_scan = time.time()

            if not paths:
                logger.warning("No keyboard devices found. Retrying in %ds...", scan_interval)
                for _ in range(scan_interval):
                    if not running: break
                    time.sleep(1)
                continue

            for path in paths:
                try:
                    dev = InputDevice(path)
                    fds[dev.fd] = dev
                    logger.info("Opened: %s (%s)", path, dev.name)
                except (PermissionError, OSError) as e:
                    logger.error("Cannot open %s: %s", path, e)

            if not fds:
                logger.warning("Could not open any devices. Retrying...")
                time.sleep(scan_interval)
                continue

            logger.info("Monitoring %d device(s)", len(fds))

        # Event loop
        try:
            readable, _, _ = select.select(list(fds.keys()), [], [], 1.0)
            for fd in readable:
                dev = fds[fd]
                try:
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY and event.value == 1:  # key press
                            key_buffer += 1
                            # Get key name from keycode
                            key_name = ecodes.KEY.get(event.code, f"KEY_{event.code}")
                            key_type_buffer[key_name] = key_type_buffer.get(key_name, 0) + 1
                except (OSError, BlockingIOError):
                    pass

            # Periodic flush
            now = time.time()
            if key_buffer > 0 and now - last_flush >= flush_interval:
                logger.info("Flushing %d keypresses (%d unique keys)", key_buffer, len(key_type_buffer))
                add_keystrokes(key_buffer, key_type_buffer)
                key_buffer = 0
                key_type_buffer = {}
                last_flush = now

        except select.error as e:
            if e.args[0] == 4:  # EINTR
                continue
            logger.error("select error: %s", e)
            time.sleep(1)
        except Exception as e:
            logger.exception("Main loop error")
            time.sleep(1)

    # Shutdown
    if key_buffer > 0:
        add_keystrokes(key_buffer)
        logger.info("Final flush: %d", key_buffer)
    for dev in fds.values():
        try: dev.close()
        except: pass
    logger.info("Keystats daemon stopped")

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: keystats-daemon [--foreground]")
        sys.exit(0)

    if "--foreground" in sys.argv:
        run()
    else:
        try:
            pid = os.fork()
            if pid > 0: sys.exit(0)
        except OSError: sys.exit(1)
        os.chdir("/"); os.setsid(); os.umask(0)
        try:
            pid = os.fork()
            if pid > 0: sys.exit(0)
        except OSError: sys.exit(1)
        with open("/dev/null", "r") as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open("/dev/null", "a+") as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
        try:
            with open("/var/run/keystats.pid", "w") as f:
                f.write(str(os.getpid()))
        except: pass
        run()

if __name__ == "__main__":
    main()
