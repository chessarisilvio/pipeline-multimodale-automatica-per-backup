#!/usr/bin/env python3
"""
Watcher script for pipeline-multimodale-automatica-per-backup.
Monitors the data/ directory for new files and processes them based on extension.
"""

import os
import time
import subprocess
import sys
from pathlib import Path

try:
    import pyinotify
except ImportError:
    print("Error: pyinotify module not installed. Install it with: pip install pyinotify", file=sys.stderr)
    sys.exit(1)

# Base directory of the project (where this script resides)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "watcher.log"

# Extension sets
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma'}

def log_message(message):
    """Append a timestamped message to the log file."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
    # Also print to stdout for visibility
    print(f"[{timestamp}] {message}")

def process_file(filepath):
    """Determine file type and call appropriate processing script."""
    ext = filepath.suffix.lower()
    if ext in IMAGE_EXTS:
        script = SCRIPTS_DIR / "process_image.sh"
        log_message(f"Image detected: {filepath.name} -> invoking {script.name}")
    elif ext in AUDIO_EXTS:
        script = SCRIPTS_DIR / "process_audio.sh"
        log_message(f"Audio detected: {filepath.name} -> invoking {script.name}")
    else:
        log_message(f"Ignored file (unsupported extension): {filepath.name}")
        return

    if not script.is_file():
        log_message(f"Processing script not found: {script}")
        return

    try:
        # Run the processing script with the file path as argument
        result = subprocess.run([str(script), str(filepath)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log_message(f"Processing succeeded for {filepath.name}")
        else:
            log_message(f"Processing failed for {filepath.name}: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log_message(f"Processing timed out for {filepath.name}")
    except Exception as e:
        log_message(f"Error running processing script for {filepath.name}: {e}")

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        # Ignore directories
        if not os.path.isdir(event.pathname):
            filepath = Path(event.pathname)
            log_message(f"New file detected: {filepath.name}")
            process_file(filepath)

def main():
    if not DATA_DIR.is_dir():
        log_message(f"Data directory not found: {DATA_DIR}")
        sys.exit(1)

    log_message(f"Starting watcher on {DATA_DIR}")
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wm.add_watch(str(DATA_DIR), mask, rec=False)

    try:
        notifier.loop()
    except KeyboardInterrupt:
        log_message("Watcher stopped by user")
    except Exception as e:
        log_message(f"Watcher error: {e}")
    finally:
        notifier.stop()

if __name__ == "__main__":
    main()