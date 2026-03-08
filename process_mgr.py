# ============================================================
#  process_mgr.py — OS Process collection, protection & termination
# ============================================================

import psutil
from config import (
    MAX_PROCESSES_SHOWN, PROTECTED_PIDS, PROTECTED_NAMES,
    STATUS_COLORS,
)


def get_processes():
    """
    Return a list of process dicts sorted by CPU% desc.
    Each dict: { pid, name, cpu, memory, status, color }
    """
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            info = p.info
            pid = info['pid']
            if pid in PROTECTED_PIDS:
                continue

            name = info['name'] or "Unknown"
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
