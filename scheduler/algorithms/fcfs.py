from scheduler.models import Process, ScheduledProcess


def schedule_fcfs(processes: list[Process]) -> list[ScheduledProcess]:
    """
    First-Come First-Served rasporedjivanje

    Procesi su izvršavani u redoslodu kojim dolaze.
    Kada proces dobije CPU, izvršava se do kraja.

    Neprekidan algoritam.
    """

    scheduled_processes: list[ScheduledProcess] = []

    # Sortira se po arrival time
    # Ako 2 procesa dodju u isto vreme, njihov originalni red dolaska se zadrzava
    indexed_processes = list(enumerate(processes))
    sorted_processes = sorted(
        indexed_processes, key=lambda item: (item[1].arrival_time, item[0])
    )

    current_time = 0

    for _, process in sorted_processes:
        # Ako je CPU idle pre dolaska procesa,
        # dodaj trenutno vreme na vreme dolaska procesa (arrival time)
        start_time = max(current_time, process.arrival_time)

        completion_time = start_time + process.burst_time

        scheduled_process = ScheduledProcess(
            pid=process.pid,
            arrival_time=process.arrival_time,
            burst_time=process.burst_time,
            deadline=process.deadline,
            start_time=start_time,
            completion_time=completion_time,
            memory_tier=process.memory_tier,
            memory_intensity=process.memory_intensity,
        )

        scheduled_processes.append(scheduled_process)

        # Sledeci proces ce se izvrsavati samo kad se trenutni zavrsi
        current_time = completion_time

    return scheduled_processes
