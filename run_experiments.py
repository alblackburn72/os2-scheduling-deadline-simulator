import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Experiment:
    name: str
    workload_path: Path
    output_dir: Path
    rr_quantum: int = 2
    enable_memory_penalty: bool = False
    memory_penalty_factor: float | None = None


DEFAULT_OUTPUT_ROOT = Path("results/experiments")


def build_experiments(output_root: Path) -> list[Experiment]:
    return [
        Experiment(
            name="basic",
            workload_path=Path("data/workload_basic.json"),
            output_dir=output_root / "basic",
        ),
        Experiment(
            name="spn_vs_hrrn",
            workload_path=Path("data/workload_spn_vs_hrrn.json"),
            output_dir=output_root / "spn_vs_hrrn",
        ),
        Experiment(
            name="spn_vs_hrrn_quantum_3",
            workload_path=Path("data/workload_spn_vs_hrrn.json"),
            output_dir=output_root / "spn_vs_hrrn_quantum_3",
            rr_quantum=3,
        ),
        Experiment(
            name="memory_penalty_disabled",
            workload_path=Path("data/workload_remote_memory.json"),
            output_dir=output_root / "memory_penalty_disabled",
            enable_memory_penalty=False,
        ),
        Experiment(
            name="memory_penalty_factor_0_25",
            workload_path=Path("data/workload_remote_memory.json"),
            output_dir=output_root / "memory_penalty_factor_0_25",
            enable_memory_penalty=True,
            memory_penalty_factor=0.25,
        ),
        Experiment(
            name="memory_penalty_factor_0_5",
            workload_path=Path("data/workload_remote_memory.json"),
            output_dir=output_root / "memory_penalty_factor_0_5",
            enable_memory_penalty=True,
            memory_penalty_factor=0.5,
        ),
        Experiment(
            name="memory_penalty_factor_1_0",
            workload_path=Path("data/workload_remote_memory.json"),
            output_dir=output_root / "memory_penalty_factor_1_0",
            enable_memory_penalty=True,
            memory_penalty_factor=1.0,
        ),
    ]


def run_experiment(experiment: Experiment) -> None:
    command = [
        sys.executable,
        "main.py",
        str(experiment.workload_path),
        "--quantum",
        str(experiment.rr_quantum),
        "--output-dir",
        str(experiment.output_dir),
    ]

    if experiment.enable_memory_penalty:
        command.append("--enable-memory-penalty")

    if experiment.memory_penalty_factor is not None:
        command.extend(
            ["--memory-penalty-factor", str(experiment.memory_penalty_factor)]
        )

    print()
    print(f"Running experiment: {experiment.name}")
    print("Command:", " ".join(command))

    subprocess.run(command, check=True)


def collect_combined_metrics(
    experiments: list[Experiment],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []

    for experiment in experiments:
        metrics_path = experiment.output_dir / "metrics.csv"

        if not metrics_path.exists():
            raise FileNotFoundError(
                f"Metrics file not found for experiment '{experiment.name}': "
                f"{metrics_path}"
            )

        with metrics_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                combined_row = {
                    "experiment_name": experiment.name,
                    "workload_path": str(experiment.workload_path),
                    "rr_quantum": str(experiment.rr_quantum),
                    "memory_penalty_enabled": str(experiment.enable_memory_penalty),
                    "memory_penalty_factor": (
                        ""
                        if experiment.memory_penalty_factor is None
                        else str(experiment.memory_penalty_factor)
                    ),
                    "algorithm_name": row["algorithm_name"],
                    "average_waiting_time": row["average_waiting_time"],
                    "average_turnaround_time": row["average_turnaround_time"],
                    "average_response_time": row["average_response_time"],
                    "deadline_miss_count": row["deadline_miss_count"],
                    "deadline_miss_ratio": row["deadline_miss_ratio"],
                }

                rows.append(combined_row)

    fieldnames = [
        "experiment_name",
        "workload_path",
        "rr_quantum",
        "memory_penalty_enabled",
        "memory_penalty_factor",
        "algorithm_name",
        "average_waiting_time",
        "average_turnaround_time",
        "average_response_time",
        "deadline_miss_count",
        "deadline_miss_ratio",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all predefined scheduling experiments"
    )

    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root directory where experiment results will be saved",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_root = Path(args.output_root)
    experiments = build_experiments(output_root)

    for experiment in experiments:
        run_experiment(experiment)

    combined_metrics_path = output_root / "combined_metrics.csv"
    collect_combined_metrics(experiments, combined_metrics_path)

    print()
    print("All experiments completed.")
    print(f"Combined metrics exported to: {combined_metrics_path}")


if __name__ == "__main__":
    main()
