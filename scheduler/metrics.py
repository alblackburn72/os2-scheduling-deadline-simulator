from dataclasses import dataclass

from scheduler.models import ScheduledProcess


@dataclass(frozen=True)
class SchedulingMetrics:
    algorithm_name: str
    average_waiting_time: float
    average_turnaround_time: float
    average_response_time: float
    deadline_miss_count: int
    deadline_miss_ratio: float


def calculate_metrics(
    algorithm_name: str,
    scheduled_processes: list[ScheduledProcess],
) -> SchedulingMetrics:
    if not scheduled_processes:
        return SchedulingMetrics(
            algorithm_name=algorithm_name,
            average_waiting_time=0.0,
            average_turnaround_time=0.0,
            average_response_time=0.0,
            deadline_miss_count=0,
            deadline_miss_ratio=0.0,
        )
    process_count = len(scheduled_processes)

    total_waiting_time = sum(process.waiting_time for process in scheduled_processes)
    total_turnaround_time = sum(
        process.turnaround_time for process in scheduled_processes
    )
    total_response_time = sum(process.response_time for process in scheduled_processes)

    deadline_miss_count = sum(
        1 for process in scheduled_processes if process.deadline_missed
    )

    return SchedulingMetrics(
        algorithm_name=algorithm_name,
        average_waiting_time=total_waiting_time / process_count,
        average_turnaround_time=total_turnaround_time / process_count,
        average_response_time=total_response_time / process_count,
        deadline_miss_count=deadline_miss_count,
        deadline_miss_ratio=deadline_miss_count / process_count,
    )
