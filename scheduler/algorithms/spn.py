from scheduler.models import Process, ScheduledProcess


def schedule_spn(processes: list[Process]) -> list[ScheduledProcess]:
    """
    Shortest Process/Job Next

    Prilikom svakog rasporedjivanja, algoritam bira proces sa
    najmanjim burst_time.

    Neprekidno rasporedjivanje - proces se izvrsava do kraja.
    """

    if not processes:
        return []

    indexed_processes = list(enumerate(processes))

    remaining_processes = sorted(
        indexed_processes,
        key=lambda item: (item[1].arrival_time, item[0]),
    )

    scheduled_processes: list[ScheduledProcess] = []
    current_time = 0

    while remaining_processes:
        avaliable_processes = [
            item for item in remaining_processes if item[1].arrival_time <= current_time
        ]

        # Ako nijedan proces jos nije stigao, uzmi sledeci arrival time
        if not avaliable_processes:
            next_arrival_time = remaining_processes[0][1].arrival_time
            current_time = next_arrival_time
            continue

        # Izbor dostupnih procesa po najkracem burst time
        # Tie-breakers:
        # 1. ranije arrival time
        # 2. originalni redosled dolaska
        selected_index, selected_process = min(
            avaliable_processes,
            key=lambda item: (item[1].burst_time, item[1].arrival_time, item[0]),
        )

        start_time = current_time
        completion_time = start_time + selected_process.burst_time

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

    return scheduled_processes
