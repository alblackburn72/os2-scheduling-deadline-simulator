from scheduler.models import (
    ExecutionSegment,
    Process,
    ScheduledProcess,
    SchedulingResult,
)
from scheduler.timeline import add_exec_segment


def get_task_id_from_process_id(process_id: str) -> str:
    """
    Izvlaci periodicne task_id-eve iz id-eva generisanih procesa.

    Primer:
      T1_0 -> T1
      T2_3 -> T2

    Koristi rsplit da bi task_id-evi sa '_' i dalje radili.
    Primer:
      TASK_FAST_0 -> TASK_FAST
    """

    return process_id.rsplit("_", 1)[0]


def schedule_rms(
    processes: list[Process], task_periods: dict[str, int]
) -> SchedulingResult:
    """
    Rate Monotonic Scheduling.

    RMS je prekidni algoritam rasporedjivanja fiksnog prioriteta za periodicne zadatke.

    Pravilo prioriteta:
      kraci period = visi prioritet

    Funkcija prima konkretne procese/poslove generisanih iz periodicnih
    task-ova, npr:

      T1_0, T1_1, T2_0, ...

    task_periods mapira originalan task_id na njegov period:

      {
        "T1": 5,
        "T2": 10,
      }
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

        # ako nema dostupnih procesa, skoci na sledeci arrival_time
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

        def priority_key(item: tuple[int, Process]) -> tuple[int, int, int]:
            index, process = item

            task_id = get_task_id_from_process_id(process.pid)

            if task_id not in task_periods:
                raise ValueError(
                    f"Missing period for task '{task_id}'."
                    f"Process id was '{process.pid}'."
                )

            period = task_periods[task_id]

            return (
                period,  # manji period = veci prioritet
                process.arrival_time,
                index,
            )

        selected_index, selected_process = min(avaliable_processes, key=priority_key)

        if selected_index not in first_start_times:
            first_start_times[selected_index] = current_time

        segment_start_time = current_time

        # RMS je prekidan, zato simuliramo jednu po jednu vremensku jedinicu
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
        scheduled_processes=completed_processes,
        execution_segments=execution_segments,
    )
