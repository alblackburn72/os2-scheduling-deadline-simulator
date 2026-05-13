import json
from pathlib import Path
from typing import Any, cast

from scheduler.models import MemoryTier, PeriodicTask, PeriodicTaskWorkload


def load_periodic_task_workload_from_json(
    file_path: str | Path,
) -> PeriodicTaskWorkload:
    """
    Loads periodic task workload from a JSON file.
    """

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        raw_data: Any = json.load(file)

    if not isinstance(raw_data, dict):
        raise ValueError("Periodic workload JSON must contain an object.")

    if "simulation_time" not in raw_data:
        raise ValueError("Missing required field 'simulation_time'.")

    if "tasks" not in raw_data:
        raise ValueError("Missing required field 'tasks'.")

    simulation_time = int(raw_data["simulation_time"])
    raw_tasks = raw_data["tasks"]

    if simulation_time <= 0:
        raise ValueError("simulation_time must be > 0.")

    if not isinstance(raw_tasks, list):
        raise ValueError("'tasks' must be a list.")

    tasks: list[PeriodicTask] = []

    for item_index, item in enumerate(raw_tasks):
        if not isinstance(item, dict):
            raise ValueError(f"Task at index {item_index} must be an object.")

        try:
            task_id = str(item["task_id"])
            period = int(item["period"])
            execution_time = int(item["execution_time"])
            relative_deadline = int(item["relative_deadline"])
        except KeyError as error:
            raise ValueError(
                f"Missing required field {error} in task at index {item_index}."
            ) from error

        memory_tier_value = item.get("memory_tier", "local_dram")

        if memory_tier_value not in ("local_dram", "remote_memory"):
            raise ValueError(
                f"Invalid memory_tier '{memory_tier_value}' in task {task_id}. "
                "Expected 'local_dram' or 'remote_memory.'"
            )

        memory_intensity = float(item.get("memory_intensity", 1.0))

        if period <= 0:
            raise ValueError(f"period for task {task_id} must be > 0.")

        if execution_time <= 0:
            raise ValueError(f"execution_time for task {task_id} must be > 0.")

        if relative_deadline <= 0:
            raise ValueError(f"relative_deadline for task {task_id} must be > 0.")

        if execution_time > period:
            raise ValueError(f"execution_time for task {task_id} must be <= period.")

        if relative_deadline > period:
            raise ValueError(f"relative_deadline for task {task_id} must be <= period.")

        if memory_intensity < 0:
            raise ValueError(f"memory_intensity for task {task_id} must be >= 0.")

        tasks.append(
            PeriodicTask(
                task_id=task_id,
                period=period,
                execution_time=execution_time,
                relative_deadline=relative_deadline,
                memory_tier=cast(MemoryTier, memory_tier_value),
                memory_intensity=memory_intensity,
            )
        )

    return PeriodicTaskWorkload(simulation_time=simulation_time, tasks=tasks)
