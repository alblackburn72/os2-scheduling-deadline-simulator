from scheduler.algorithms.fcfs import schedule_fcfs
from scheduler.algorithms.rr import schedule_rr
from scheduler.metrics import calculate_metrics
from scheduler.models import Process, ScheduledProcess


def print_scheduled_processes(
    algorithm_name: str, scheduled_processes: list[ScheduledProcess]
) -> None:
    print(f"\n{algorithm_name} schedule:")

    for process in scheduled_processes:
        print(
            f"{process.pid}: "
            f"start={process.start_time}, "
            f"completion={process.completion_time}, "
            f"turnaround={process.turnaround_time}, "
            f"waiting={process.waiting_time}, "
            f"response={process.response_time}, "
            f"deadline_missed={process.deadline_missed} "
        )


def main() -> None:
    processes = [
        Process(pid="P1", arrival_time=0, burst_time=8, deadline=12),
        Process(pid="P2", arrival_time=1, burst_time=4, deadline=7),
        Process(pid="P3", arrival_time=2, burst_time=2, deadline=6),
    ]

    fcfs_result = schedule_fcfs(processes)
    rr_result = schedule_rr(processes, time_quantum=2)

    print_scheduled_processes("FCFS", fcfs_result)
    print(calculate_metrics("FCFS", fcfs_result))

    print_scheduled_processes("Round Robin", rr_result)
    print(calculate_metrics("Round Robin", rr_result))


if __name__ == "__main__":
    main()
