import time
from systeminfo import collect_process_snapshot


REFRESH_INTERVAL = 2  # seconds


def monitor_loop():
    print("OS Process Monitor Started")
    print("Press Ctrl + C to stop.\n")

    try:
        while True:
            processes = collect_process_snapshot()

            print("=" * 60)
            print("Top CPU Consuming Processes")
            print("=" * 60)

            for proc in processes[:10]:
                print(
                    f"{proc['name'][:18]:18} | "
                    f"PID: {proc['pid']:6} | "
                    f"CPU: {proc['cpu']:6}% | "
                    f"MEM: {proc['memory']:7} MB | "
                    f"STATE: {proc['status']}"
                )

            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user. Exiting safely.")


if __name__ == "__main__":
    monitor_loop()
