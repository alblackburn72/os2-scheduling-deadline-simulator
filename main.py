import argparse
from pathlib import Path

from scheduler.algorithms.fcfs import schedule_fcfs
from scheduler.algorithms.rr import schedule_rr
from scheduler.algorithms.spn import schedule_spn
from scheduler.algorithms.srt import schedule_srt
from scheduler.algorithms.hrrn import schedule_hrrn
from scheduler.models import ScheduledProcess
from scheduler.workload_loader import load_process_from_json
from scheduler.metrics import SchedulingMetrics, calculate_metrics
from scheduler.csv_exporter import export_metrics_to_csv, export_schedule_to_csv

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

    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory where CSV result files will be saved",
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

    schedules = {
        "FCFS": schedule_fcfs(processes),
        "Round Robin": schedule_rr(processes, time_quantum=args.quantum),
        "SPN": schedule_spn(processes),
        "SRT": schedule_srt(processes),
        "HRRN": schedule_hrrn(processes),
    }

    all_metrics: list[SchedulingMetrics] = []

    for algorithm_name, scheduled_processes in schedules.items():
        print_scheduled_processes(algorithm_name, scheduled_processes)

        metrics = calculate_metrics(algorithm_name, scheduled_processes)
        all_metrics.append(metrics)

        print(metrics)

    output_dir = Path(args.output_dir)

    metrics_output_path = output_dir / "metrics.csv"
    schedule_output_path = output_dir / "schedule.csv"

    export_metrics_to_csv(all_metrics, metrics_output_path)
    export_schedule_to_csv(schedules, schedule_output_path)

    print()
    print(f"Metrics exported to: {metrics_output_path}")
    print(f"Schedule exported to: {schedule_output_path}")


if __name__ == "__main__":
    main()
