import json
from pathlib import Path
from typing import Any, cast

from scheduler.models import MemoryTier, Process


def load_process_from_json(file_path: str | Path) -> list[Process]:
    """
    Za ucitavanje liste procesa iz JSON fajlova
    """

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        raw_data: Any = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError("Workload JSON must contain list of processes")

    processes: list[Process] = []

    for item_index, item in enumerate(raw_data):
        if not isinstance(item, dict):
            raise ValueError(f"Process at index {item_index} must be an object")

        try:
            pid = str(item["pid"])
            arrival_time = int(item["arrival_time"])
            burst_time = int(item["burst_time"])
            deadline = int(item["deadline"])
        except KeyError as error:
            raise ValueError(
                f"Missing required field {error} in process at index {item_index}"
            ) from error

        memory_tier_value = item.get("memory_tier", "local_dram")

        if memory_tier_value not in ("local_dram", "cxl_like_memory"):
            raise ValueError(
                f"Invalid memory_tier '{memory_tier_value}' in process {pid}"
                "Expected 'local_dram' or 'cxl_like_memory'"
            )

        memory_intensity = float(item.get("memory_intensity", 1.0))

        if arrival_time < 0:
            raise ValueError(f"arrival_time for process {pid} must be >= 0")

        if burst_time < 0:
            raise ValueError(f"burst_time for process {pid} must be >= 0")

        if deadline < 0:
            raise ValueError(f"deadline for process {pid} must be >= 0")

        if memory_intensity < 0:
            raise ValueError(f"memory_intensity for process {pid} must be >= 0")

        processes.append(
            Process(
                pid=pid,
                arrival_time=arrival_time,
                burst_time=burst_time,
                deadline=deadline,
                memory_tier=cast(MemoryTier, memory_tier_value),
                memory_intensity=memory_intensity,
            )
        )
    return processes
