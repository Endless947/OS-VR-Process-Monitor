def normalize_process_data(processes):
    """
    Converts raw OS process data into normalized,
    visualization-ready values.
    """

    if not processes:
        return []

    # Find max memory usage in current snapshot
    max_memory = max(p["memory"] for p in processes) or 1

    normalized = []

    for proc in processes:
        cpu_norm = min(proc["cpu"] / 100.0, 1.0)
        mem_norm = min(proc["memory"] / max_memory, 1.0)

        # Map process state to color (for visualization later)
        if proc["status"] == "running":
            color = "green"
        elif proc["status"] == "stopped":
            color = "red"
        else:
            color = "yellow"

        normalized.append({
            **proc,

            # Normalized values
            "cpu_norm": round(cpu_norm, 3),
            "mem_norm": round(mem_norm, 3),

            # Visualization hints
            "visual": {
                "size": round(mem_norm, 3),
                "height": round(cpu_norm, 3),
                "color": color
            }
        })

    return normalized
