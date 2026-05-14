import argparse
from pathlib import Path

from scheduler.algorithms.rms import schedule_rms
from scheduler.algorithms.edf import schedule_edf
from scheduler.csv_exporter import (
    export_metrics_to_csv,
    export_schedule_to_csv,
    export_timeline_to_csv,
)
from scheduler.memory_penalty import MemoryPenaltyConfig, apply_memory_penalty
from scheduler.metrics import calculate_metrics
from scheduler.periodic_task_generator import generate_processes_from_periodic_tasks
from scheduler.periodic_task_loader import load_periodic_task_workload_from_json

DEFAULT_PERIODIC_WORKLOAD_PATH = Path("data/periodic_tasks_basic.json")
DEFAULT_OUTPUT_DIR = Path("results/rms")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run periodic scheduling algorithms on a periodic task workload"
    )

    parser.add_argument(
        "workload_path",
        nargs="?",
        default=str(DEFAULT_PERIODIC_WORKLOAD_PATH),
        help="Path to periodic task workload JSON file.",
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where RMS result files will be saved",
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
        help="Penalty factor for processes using slower/remote memory",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.memory_penalty_factor < 0:
        raise ValueError("memory_penalty_factor must be >= 0.")

    workload = load_periodic_task_workload_from_json(args.workload_path)

    processes = generate_processes_from_periodic_tasks(workload)

    if args.enable_memory_penalty:
        memory_penalty_config = MemoryPenaltyConfig(
            memory_penalty_factor=args.memory_penalty_factor
        )

        processes = apply_memory_penalty(processes, memory_penalty_config)

        print("Memory penalty: enabled")
        print(f"Memory penalty factor: {args.memory_penalty_factor}")
    else:
        print("Memory penalty: disabled")

    task_periods = {task.task_id: task.period for task in workload.tasks}

    scheduling_results = {
        "RMS": schedule_rms(processes, task_periods),
        "EDF": schedule_edf(processes),
    }

    completed_schedules = {
        algorithm_name: result.scheduled_processes
        for algorithm_name, result in scheduling_results.items()
    }

    timelines = {
        algorithm_name: result.execution_segments
        for algorithm_name, result in scheduling_results.items()
    }

    all_metrics = [
        calculate_metrics(algorithm_name, scheduled_processes)
        for algorithm_name, scheduled_processes in completed_schedules.items()
    ]

    print(f"Loaded periodic workload: {args.workload_path}")
    print(f"Simulation time: {workload.simulation_time}")
    print(f"Periodic task count: {len(workload.tasks)}")
    print(f"Generated process count: {len(processes)}")

    for algorithm_name, scheduled_processes in completed_schedules.items():
        print()
        print(f"{algorithm_name} schedule:")
        for process in scheduled_processes:
            print(
                f"{process.pid}: "
                f"base_burst={process.resolved_base_burst_time}, "
                f"effective_burst={process.effective_burst_time}, "
                f"arrival={process.arrival_time}, "
                f"start={process.start_time}, "
                f"completion={process.completion_time}, "
                f"deadline={process.deadline}, "
                f"turnaround={process.turnaround_time}, "
                f"waiting={process.waiting_time}, "
                f"response={process.response_time}, "
                f"deadline_missed={process.deadline_missed}"
            )

        print()
        print(calculate_metrics(algorithm_name, scheduled_processes))

    output_dir = Path(args.output_dir)

    metrics_output_path = output_dir / "metrics.csv"
    schedule_output_path = output_dir / "schedule.csv"
    timeline_output_path = output_dir / "timeline.csv"

    export_metrics_to_csv(all_metrics, metrics_output_path)
    export_schedule_to_csv(completed_schedules, schedule_output_path)
    export_timeline_to_csv(timelines, timeline_output_path)

    print()
    print(f"Metrics exported to: {metrics_output_path}")
    print(f"Schedule exported to: {schedule_output_path}")
    print(f"Timeline exported to: {timeline_output_path}")


if __name__ == "__main__":
    main()
