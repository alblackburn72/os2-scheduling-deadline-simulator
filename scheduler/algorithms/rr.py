from collections import deque

from scheduler.models import Process, ScheduledProcess


def schedule_rr(
    processes: list[Process],
    time_quantum: int,
) -> list[ScheduledProcess]:
    """
    Round Robin rasporedjivanje.

    Svaki proces dobija vremenski kvant.
    Ako proces ne zavrsi u tom vremenu, prekida se i vraca se na kraj reda.
    """

    if time_quantum <= 0:
        raise ValueError("time_quantum must be greater than 0")

    if not processes:
        return []

    indexed_porcesses = list(enumerate(processes))

    sorted_processes = sorted(
        indexed_porcesses,
        key=lambda item: (item[1].arrival_time, item[0]),
    )

    processes_by_index = {index: process for index, process in indexed_porcesses}

    remaining_times = {
        index: process.burst_time for index, process in indexed_porcesses
    }

    first_start_times: dict[int, int] = {}
    completed_porcesses: list[ScheduledProcess] = []

    ready_queue: deque[int] = deque()

    current_time = 0
    next_process_index = 0

    while len(completed_porcesses) < len(processes):
        # Dodaj sve pristigle porcese po trenutnom vremenu
        while (
            next_process_index < len(sorted_processes)
            and sorted_processes[next_process_index][1].arrival_time <= current_time
        ):
            process_index, _ = sorted_processes[next_process_index]
            ready_queue.append(process_index)
            next_process_index += 1

        # Ako proces nije spreman, skaci na dolazno vreme sledeceg procesa
        if not ready_queue:
            if next_process_index < len(sorted_processes):
                current_time = sorted_processes[next_process_index][1].arrival_time
                continue

            break

        process_index = ready_queue.popleft()
        process = processes_by_index[process_index]

        # Vreme odziva je momenat cim proces dobije CPU vreme
        if process_index not in first_start_times:
            first_start_times[process_index] = current_time

        run_time = min(time_quantum, remaining_times[process_index])

        current_time += run_time
        remaining_times[process_index] -= run_time

        # Tokom kvanta, novi procesi mogu da stignu
        while (
            next_process_index < len(sorted_processes)
            and sorted_processes[next_process_index][1].arrival_time <= current_time
        ):
            arrived_process_index, _ = sorted_processes[next_process_index]
            ready_queue.append(arrived_process_index)
            next_process_index += 1

        if remaining_times[process_index] == 0:
            completed_porcesses.append(
                ScheduledProcess(
                    pid=process.pid,
                    arrival_time=process.arrival_time,
                    burst_time=process.burst_time,
                    deadline=process.deadline,
                    start_time=first_start_times[process_index],
                    completion_time=current_time,
                    memory_tier=process.memory_tier,
                    memory_intensity=process.memory_intensity,
                    base_burst_time=process.resolved_base_burst_time,
                )
            )
        else:
            # Proces nije gotov, salji ga na kraj reda
            ready_queue.append(process_index)

    return completed_porcesses
