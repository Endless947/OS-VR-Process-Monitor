import psutil
import time


def collect_process_snapshot():
    """
    Collects a single snapshot of all user-accessible OS processes
    with CPU usage, memory usage, and process state.
    """

    processes = []

    # First pass: prime CPU counters
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sampling interval (important for CPU % accuracy)
    time.sleep(2)

    # Second pass: actual data collection
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            pid = proc.pid

            # Skip kernel-only / critical system processes
            if pid in (0, 4):
                continue

            name = proc.name() or "Unknown"
            cpu = proc.cpu_percent(interval=None)
            memory = proc.memory_info().rss / (1024 * 1024)  # MB
            status = proc.status()

            processes.append({
                "pid": pid,
                "name": name,
                "cpu": round(cpu, 2),
                "memory": round(memory, 2),
                "status": status
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort by CPU usage (descending)
    processes.sort(key=lambda p: p["cpu"], reverse=True)

    return processes


if __name__ == "__main__":
    snapshot = collect_process_snapshot()

    # Display top 10 active processes
    for proc in snapshot[:10]:
        print(proc)
