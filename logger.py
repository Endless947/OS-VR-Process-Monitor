# ============================================================
#  logger.py — Log terminated processes to file
# ============================================================

import datetime
from config import LOG_FILE


def log_termination(pid, name, message=""):
    """Append a termination record to the log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}]  PID: {pid:>6}  |  Name: {name}  |  {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
