import time
from systeminfo import collect_process_snapshot
from normalization import normalize_process_data

REFRESH_INTERVAL = 2  # seconds


def monitor_loop():
    print("OS Process Monitor Started")
    print("Press Ctrl + C to stop.\n")

    try:
        while True:
            raw_processes = collect_process_snapshot()
            processes = normalize_process_data(raw_processes)


            print("=" * 60)
            print("Top CPU Consuming Processes")
            print("=" * 60)

            for proc in processes[:10]:
                print(
                    f"{proc['name'][:18]:18} | "
                    f"PID: {proc['pid']:6} | "
                    f"CPU: {proc['cpu']:6}% ({proc['cpu_norm']}) | "
                    f"MEM: {proc['memory']:7} MB ({proc['mem_norm']}) | "
                    f"COLOR: {proc['visual']['color']}"
                )


            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user. Exiting safely.")


if __name__ == "__main__":
    monitor_loop()
