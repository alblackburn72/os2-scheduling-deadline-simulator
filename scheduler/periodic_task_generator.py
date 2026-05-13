from scheduler.models import PeriodicTaskWorkload, Process


def generate_processes_from_periodic_tasks(
    workload: PeriodicTaskWorkload,
) -> list[Process]:
    """
    Generise konkretne procese/poslove iz periodicnih zadataka.

    Svaki periodicni task pravi jedan proces na svaki release_time:
      release_time = 0, period, 2 * period, ...

    sve dok release_time < simulation_time

    Primer:
      T1 sa period=5 i simulation_time=20 pravi:
      T1_0, T1_1, T1_2, T1_3
    """

    generated_processes: list[Process] = []

    for task in workload.tasks:
        instance_index = 0
        release_time = 0

        while release_time < workload.simulation_time:
            absolute_deadline = release_time + task.relative_deadline

            generated_processes.append(
                Process(
                    pid=f"{task.task_id}_{instance_index}",
                    arrival_time=release_time,
                    burst_time=task.execution_time,
                    deadline=absolute_deadline,
                    memory_tier=task.memory_tier,
                    memory_intensity=task.memory_intensity,
                    base_burst_time=task.execution_time,
                )
            )

            instance_index += 1
            release_time += task.period

    return sorted(
        generated_processes, key=lambda process: (process.arrival_time, process.pid)
    )
