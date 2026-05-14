from scheduler.models import (
    ExecutionSegment,
    Process,
    ScheduledProcess,
    SchedulingResult,
)
from scheduler.timeline import add_exec_segment


def schedule_edf(processes: list[Process]) -> SchedulingResult:
    """
    Earliest Deadline First scheduling.

    EDF je preemptive real-time scheduling algoritam.

    U svakom trenutku bira se dostupni proces sa najranijim deadline-om.

    Priority rule:
      earlier absolute deadline = higher priority
    """

    if not processes:
        return SchedulingResult(
            scheduled_processes=[],
            execution_segments=[],
        )

    indexed_processes = list(enumerate(processes))

    remaining_times = {
        index: process.burst_time for index, process in indexed_processes
    }

    first_start_times: dict[int, int] = {}
    completed_indices: set[int] = set()

    completed_processes: list[ScheduledProcess] = []
    execution_segments: list[ExecutionSegment] = []

    current_time = 0

    while len(completed_processes) < len(processes):
        avaliable_processes = [
            (index, process)
            for index, process in indexed_processes
            if process.arrival_time <= current_time
            and index not in completed_indices
            and remaining_times[index] > 0
        ]

        if not avaliable_processes:
            future_arrival_times = [
                process.arrival_time
                for index, process in indexed_processes
                if index not in completed_indices and remaining_times[index] > 0
            ]

            if not future_arrival_times:
                break

            current_time = min(future_arrival_times)
            continue

        selected_index, selected_process = min(
            avaliable_processes,
            key=lambda item: (
                item[1].deadline,
                item[1].arrival_time,
                item[0],
            ),
        )

        if selected_index not in first_start_times:
            first_start_times[selected_index] = current_time

        segment_start_time = current_time

        remaining_times[selected_index] -= 1
        current_time += 1

        add_exec_segment(
            execution_segments=execution_segments,
            pid=selected_process.pid,
            start_time=segment_start_time,
            end_time=current_time,
        )

        if remaining_times[selected_index] == 0:
            completed_indices.add(selected_index)

            completed_processes.append(
                ScheduledProcess(
                    pid=selected_process.pid,
                    arrival_time=selected_process.arrival_time,
                    burst_time=selected_process.burst_time,
                    deadline=selected_process.deadline,
                    start_time=first_start_times[selected_index],
                    completion_time=current_time,
                    memory_tier=selected_process.memory_tier,
                    memory_intensity=selected_process.memory_intensity,
                    base_burst_time=selected_process.resolved_base_burst_time,
                )
            )

    return SchedulingResult(
        scheduled_processes=completed_processes, execution_segments=execution_segments
    )
