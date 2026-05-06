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
from scheduler.memory_penalty import MemoryPenaltyConfig, apply_memory_penalty

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

    parser.add_argument(
        "--enable-memory-penalty",
        action="store_true",
        help="Enable memory penalty model",
    )

    parser.add_argument(
        "--memory-penalty-factor",
        type=float,
        default=0.5,
        help="Penalty factor for remote_memory processes",
    )

    return parser.parse_args()


def print_scheduled_processes(
    algorithm_name: str, scheduled_processes: list[ScheduledProcess]
) -> None:
    print(f"\n{algorithm_name} schedule:")

    for process in scheduled_processes:
        print(
            f"{process.pid}: "
            f"base_burst={process.resolved_base_burst_time}, "
            f"effective_burst={process.effective_burst_time}, "
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

    if args.memory_penalty_factor < 0:
        raise ValueError("memory_penalty_factor must be >= 0")

    if args.enable_memory_penalty:
        memory_penalty_config = MemoryPenaltyConfig(
            memory_penalty_factor=args.memory_penalty_factor
        )

        processes = apply_memory_penalty(processes, memory_penalty_config)

        print("Memory penalty: enabled")
        print(f"Penalty factor: {args.memory_penalty_factor}")
    else:
        print("Memory penalty: disabled")

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
