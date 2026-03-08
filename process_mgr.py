# ============================================================
#  process_mgr.py — OS Process collection, protection & termination
#  Filters to only show user-visible applications (with windows)
# ============================================================

import ctypes
import ctypes.wintypes
import psutil
from config import (
    MAX_PROCESSES_SHOWN, PROTECTED_PIDS, PROTECTED_NAMES,
    STATUS_COLORS, SYSTEM_PROCESS_NAMES,
)


# ---- Win32: collect PIDs that own at least one visible window -----
user32 = ctypes.windll.user32

# Callback type for EnumWindows
WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.wintypes.BOOL,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LPARAM,
)


def _get_windowed_pids():
    """Return a set of PIDs that own at least one visible, titled window."""
    pids = set()

    def _cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            # Only count windows that have a non-empty title
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                pid = ctypes.wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                pids.add(pid.value)
        return True  # continue enumeration

    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return pids


def get_processes():
    """
    Return a list of process dicts sorted by CPU% desc.
    Only includes processes that have a visible window (user apps).
    Each dict: { pid, name, cpu, memory, status, color }
    """
    windowed_pids = _get_windowed_pids()

    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            info = p.info
            pid = info['pid']

            # Skip protected PIDs
            if pid in PROTECTED_PIDS:
                continue

            # Only show processes that have a visible window
            if pid not in windowed_pids:
                continue

            name = info['name'] or "Unknown"

            # Skip known system / background process names
            if name.lower() in SYSTEM_PROCESS_NAMES:
                continue

            cpu = info['cpu_percent'] or 0.0
            mem_bytes = info['memory_info'].rss if info['memory_info'] else 0
            mem_mb = round(mem_bytes / (1024 * 1024), 1)
            status = info['status'] or "unknown"

            color = STATUS_COLORS.get(status, STATUS_COLORS["default"])

            procs.append({
                "pid": pid,
                "name": name,
                "cpu": round(cpu, 1),
                "memory": mem_mb,
                "status": status,
                "color": color,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    procs.sort(key=lambda p: p["cpu"], reverse=True)
    return procs[:MAX_PROCESSES_SHOWN]


def is_protected(pid, name=""):
    """Check if a process should never be killed."""
    if pid in PROTECTED_PIDS:
        return True
    if name.lower() in PROTECTED_NAMES:
        return True
    return False


def terminate_process(pid, name=""):
    """
    Attempt to terminate a process by PID.
    Returns (success: bool, message: str).
    """
    if is_protected(pid, name):
        return False, f"Protected process: {name} (PID {pid})"

    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return True, f"Terminated: {name} (PID {pid})"
    except psutil.NoSuchProcess:
        return False, f"Process no longer exists (PID {pid})"
    except psutil.AccessDenied:
        return False, f"Access denied: {name} (PID {pid})"
    except Exception as e:
        return False, f"Error: {e}"
