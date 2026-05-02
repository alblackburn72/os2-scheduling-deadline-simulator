from scheduler.models import Process, ScheduledProcess


def schedule_srt(processes: list[Process]) -> list[ScheduledProcess]:
    """
    Shortest Remaining Time

    U svakom trenutku izaberi proces koji trenutno ima najmanje preostalog
    vremena za izvrsavanje

    Prekidni algoritam - Proces koji se trenutno izvrsava moze se prekinuti
    od strane drugog procesa sa manjim preostalim vremenom izvrsavanja
    """

    if not processes:
        return []

    indexed_processes = list(enumerate(processes))

    processes_by_index = {index: process for index, process in indexed_processes}
    remaining_times = {
        index: process.burst_time for index, process in indexed_processes
    }

    first_start_times: dict[int, int] = {}
    completed_processes: list[ScheduledProcess] = []

    completed_indices: set[int] = set()

    current_time = 0

    while len(completed_processes) < len(processes):
        avaliable_processes = [
            (index, process)
            for index, process in indexed_processes
            if process.arrival_time <= current_time
            and index not in completed_indices
            and remaining_times[index] > 0
        ]

        # ako nema trenutno dostupnih procesa, idi na sledeci arrival time

        if not avaliable_processes:
            future_processes = [
                process.arrival_time
                for index, process in indexed_processes
                if index not in completed_indices and remaining_times[index] > 0
            ]

            if not future_processes:
                break

            current_time = min(future_processes)
            continue

        # bira se proces sa najmanjim preostalim vremenom izvrsavanja
        # Tie-breakers:
        # 1. raniji arrival time
        # 2. originalni red dolaska
        selected_index, selected_process = min(
            avaliable_processes,
            key=lambda item: (remaining_times[item[0]], item[1].arrival_time, item[0]),
        )

        if selected_index not in first_start_times:
            first_start_times[selected_index] = current_time

        # simulira se jedna po jedna vremenska jedinica, zato sto SRT
        # moze da prekine izvrsavani proces kad god kraci proces stigne
        remaining_times[selected_index] -= 1
        current_time += 1

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
    return completed_processes
