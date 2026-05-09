from scheduler.models import (
    Process,
    ScheduledProcess,
    ExecutionSegment,
    SchedulingResult,
)
from scheduler.timeline import add_exec_segment


def schedule_hrrn(processes: list[Process]) -> SchedulingResult:
    """
    Highest Response Ration Next

    Prilikom svakog rasporedjivanja, bira se dostupan proces sa najvecim
    response_ratio:

      response_ratio = (waiting_time + burst_time) / burst_time

    Neprekidan algoritam - Proces se izvrsava dok se ne zavrsi
    """

    if not processes:
        return []

    indexed_processes = list(enumerate(processes))

    remaining_processes = sorted(
        indexed_processes, key=lambda item: (item[1].arrival_time, item[0])
    )

    scheduled_processes: list[ScheduledProcess] = []
    execution_segments: list[ExecutionSegment] = []
    current_time = 0

    while remaining_processes:
        avaliable_processes = [
            item for item in remaining_processes if item[1].arrival_time <= current_time
        ]

        # ako nema pristiglih procesa, predji na sledeci arrival time
        if not avaliable_processes:
            current_time = remaining_processes[0][1].arrival_time
            continue

        def response_ratio(item: tuple[int, Process]) -> float:
            _, process = item

            waiting_time = current_time - process.arrival_time

            return (waiting_time + process.burst_time) / process.burst_time

        # izbor dostupnog procesa sa najvecim response ratio
        # Tie-breakers:
        # 1. raniji arrival time
        # 2. originalni redosled dolaska
        selected_index, selected_process = max(
            avaliable_processes,
            key=lambda item: (response_ratio(item), -item[1].arrival_time, -item[0]),
        )

        start_time = current_time
        completion_time = start_time + selected_process.burst_time

        add_exec_segment(
            execution_segments=execution_segments,
            pid=selected_process.pid,
            start_time=start_time,
            end_time=completion_time,
        )

        scheduled_processes.append(
            ScheduledProcess(
                pid=selected_process.pid,
                arrival_time=selected_process.arrival_time,
                burst_time=selected_process.burst_time,
                deadline=selected_process.deadline,
                start_time=start_time,
                completion_time=completion_time,
                memory_tier=selected_process.memory_tier,
                memory_intensity=selected_process.memory_intensity,
                base_burst_time=selected_process.resolved_base_burst_time,
            )
        )

        current_time = completion_time

        remaining_processes = [
            item for item in remaining_processes if item[0] != selected_index
        ]

    return SchedulingResult(
        scheduled_processes=scheduled_processes, execution_segments=execution_segments
    )
