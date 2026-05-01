import argparse
from pathlib import Path

from scheduler.algorithms.fcfs import schedule_fcfs
from scheduler.algorithms.rr import schedule_rr
from scheduler.algorithms.spn import schedule_spn
from scheduler.algorithms.srt import schedule_srt
from scheduler.algorithms.hrrn import schedule_hrrn
from scheduler.metrics import calculate_metrics
from scheduler.models import ScheduledProcess
from scheduler.workload_loader import load_process_from_json

DEFAULT_WORKLOAD_PATH = Path("data/workload_basic.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare CPU scheduling algorithms on a selected workload"
    )

    parser.add_argument(
        "workload_path",
        nargs="?",
        default=str(DEFAULT_WORKLOAD_PATH),
        help="Path to workload JSON file",
    )

    parser.add_argument(
        "--quantum", type=int, default=2, help="Time quantum for Round Robin scheduling"
    )

    return parser.parse_args()


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
    args = parse_args()

    processes = load_process_from_json(args.workload_path)

    print(f"Loaded workload: {args.workload_path}")
    print(f"Process count: {len(processes)}")
    print(f"Round Robin quantum: {args.quantum}")

    fcfs_result = schedule_fcfs(processes)
    rr_result = schedule_rr(processes, time_quantum=args.quantum)
    spn_result = schedule_spn(processes)
    srt_result = schedule_srt(processes)
    hrrn_result = schedule_hrrn(processes)

    print_scheduled_processes("FCFS", fcfs_result)
    print(calculate_metrics("FCFS", fcfs_result))

    print_scheduled_processes("Round Robin", rr_result)
    print(calculate_metrics("Round Robin", rr_result))

    print_scheduled_processes("SPN", spn_result)
    print(calculate_metrics("SPN", spn_result))

    print_scheduled_processes("SRT", srt_result)
    print(calculate_metrics("SRT", srt_result))

    print_scheduled_processes("HRRN", hrrn_result)
    print(calculate_metrics("HRRN", hrrn_result))


if __name__ == "__main__":
    main()
