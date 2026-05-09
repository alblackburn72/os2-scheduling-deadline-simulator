import csv
from pathlib import Path

from scheduler.metrics import SchedulingMetrics
from scheduler.models import ScheduledProcess, ExecutionSegment


def export_metrics_to_csv(
    metrics: list[SchedulingMetrics], output_path: str | Path
) -> None:
    """
    Izvozi sumarum rasporedjivackih mera u CSV fajl
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "algorithm_name",
                "average_waiting_time",
                "average_turnaround_time",
                "average_response_time",
                "deadline_miss_count",
                "deadline_miss_ratio",
            ]
        )

        for item in metrics:
            writer.writerow(
                [
                    item.algorithm_name,
                    item.average_waiting_time,
                    item.average_turnaround_time,
                    item.average_response_time,
                    item.deadline_miss_count,
                    item.deadline_miss_ratio,
                ]
            )


def export_timeline_to_csv(
    timelines: dict[str, list[ExecutionSegment]],
    output_path: str | Path,
) -> None:
    """
    Izvozi segmente vremenske linije izvrsavanja u CSV file.

    Bice korisno za Gantt/timeline grafik.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "algorithm_name",
                "pid",
                "start_time",
                "end_time",
                "duration",
            ]
        )

        for algorithm_name, execution_segments in timelines.items():
            for segment in execution_segments:
                writer.writerow(
                    [
                        algorithm_name,
                        segment.pid,
                        segment.start_time,
                        segment.end_time,
                        segment.duration,
                    ]
                )


def export_schedule_to_csv(
    schedules: dict[str, list[ScheduledProcess]],
    output_path: str | Path,
) -> None:
    """
    Izvozi rezultate po procesu u CSV fajl.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "algorithm_name",
                "pid",
                "arrival_time",
                "base_burst_time",
                "effective_burst_time",
                "deadline",
                "start_time",
                "completion_time",
                "turnaround_time",
                "waiting_time",
                "response_time",
                "deadline_missed",
                "memory_tier",
                "memory_intensity",
            ]
        )

        for algorithm_name, scheduled_processes in schedules.items():
            for process in scheduled_processes:
                writer.writerow(
                    [
                        algorithm_name,
                        process.pid,
                        process.arrival_time,
                        process.base_burst_time,
                        process.effective_burst_time,
                        process.deadline,
                        process.start_time,
                        process.completion_time,
                        process.turnaround_time,
                        process.waiting_time,
                        process.response_time,
                        process.deadline_missed,
                        process.memory_tier,
                        process.memory_intensity,
                    ]
                )
