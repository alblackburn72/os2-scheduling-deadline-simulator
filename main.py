from scheduler.algorithms.fcfs import schedule_fcfs
from scheduler.models import Process


def main() -> None:
    processes = [
        Process(pid="P1", arrival_time=0, burst_time=8, deadline=12),
        Process(pid="P2", arrival_time=1, burst_time=4, deadline=7),
        Process(pid="P3", arrival_time=2, burst_time=2, deadline=6),
    ]

    scheduled_processes = schedule_fcfs(processes)

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


if __name__ == "__main__":
    main()
