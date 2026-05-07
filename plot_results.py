import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

DEFAULT_INPUT_PATH = Path("results/experiments/combined_metrics.csv")
DEFAULT_OUTPUT_DIR = Path("results/experiments/plots")

MetricConfig = tuple[str, str, str]

METRICS: list[MetricConfig] = [
    ("deadline_miss_ratio", "Deadline miss ratio", "deadline_miss_ratio"),
    ("average_waiting_time", "Average waiting time", "average_waiting_time"),
    ("average_turnaround_time", "Average turnaround time", "average_turnaround_time"),
    ("average_response_time", "Average response time", "average_response_time"),
]

MEMORY_PENALTY_EXPERIMENTS = [
    ("memory_penalty_disabled", "disabled"),
    ("memory_penalty_factor_0_25", "0.25"),
    ("memory_penalty_factor_0_5", "0.5"),
    ("memory_penalty_factor_1_0", "1.0"),
]


def load_metrics(input_path: Path) -> list[dict[str, str]]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Combined metrics file not found: {input_path}. "
            "Run python .\\run_experiments.py first."
        )

    with input_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def sanitize_filename(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").replace(" ", "_")


def group_rows_by_experiment(
    rows: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    grouped_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        grouped_rows[row["experiment_name"]].append(row)

    return grouped_rows


def plot_metric_for_each_experiment(
    grouped_rows: dict[str, list[dict[str, str]]],
    metric_name: str,
    title: str,
    ylabel: str,
    output_dir: Path,
) -> None:
    metric_output_dir = output_dir / metric_name
    metric_output_dir.mkdir(parents=True, exist_ok=True)

    for experiment_name, experiment_rows in grouped_rows.items():
        algorithms = [row["algorithm_name"] for row in experiment_rows]
        values = [float(row[metric_name]) for row in experiment_rows]

        plt.figure(figsize=(10, 5))
        plt.bar(algorithms, values)
        plt.title(f"{title} - {experiment_name}")
        plt.xlabel("Scheduling algorithm")
        plt.ylabel(ylabel)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()

        output_path = metric_output_dir / f"{sanitize_filename(experiment_name)}.png"

        plt.savefig(output_path)
        plt.close()

        print(f"Saved plot: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate plots from combined experiment metrics."
    )

    parser.add_argument(
        "--input", default=str(DEFAULT_INPUT_PATH), help="Path to combined_metrics.csv"
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where plot images will be saved.",
    )

    return parser.parse_args()


def find_metric_value(
    rows: list[dict[str, str]],
    experiment_name: str,
    algorithm_name: str,
    metric_name: str,
) -> float | None:
    for row in rows:
        if (
            row["experiment_name"] == experiment_name
            and row["algorithm_name"] == algorithm_name
        ):
            return float(row[metric_name])

    return None


def plot_memory_penalty_trend(
    rows: list[dict[str, str]],
    metric_name: str,
    title: str,
    ylabel: str,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    algorithm_names = sorted(
        {
            row["algorithm_name"]
            for row in rows
            if row["experiment_name"]
            in {experiment_name for experiment_name, _ in MEMORY_PENALTY_EXPERIMENTS}
        }
    )

    x_labels = [label for _, label in MEMORY_PENALTY_EXPERIMENTS]

    plt.figure(figsize=(10, 5))

    for algorithm_name in algorithm_names:
        values: list[float] = []

        for experiment_name, _ in MEMORY_PENALTY_EXPERIMENTS:
            value = find_metric_value(
                rows=rows,
                experiment_name=experiment_name,
                algorithm_name=algorithm_name,
                metric_name=metric_name,
            )

            if value is None:
                values.append(float("nan"))
            else:
                values.append(value)

        plt.plot(x_labels, values, marker="o", label=algorithm_name)

    plt.title(title)
    plt.xlabel("Memory penalty factor")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()

    output_path = output_dir / f"memory_penalty_{metric_name}.png"
    plt.savefig(output_path)
    plt.close()

    print(f"Saved plot: {output_path}")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    rows = load_metrics(input_path)
    grouped_rows = group_rows_by_experiment(rows)

    for metric_name, title, ylabel in METRICS:
        plot_metric_for_each_experiment(
            grouped_rows=grouped_rows,
            metric_name=metric_name,
            title=title,
            ylabel=ylabel,
            output_dir=output_dir,
        )

    plot_memory_penalty_trend(
        rows=rows,
        metric_name="deadline_miss_ratio",
        title="Deadline miss ratio under different memory penalty factors",
        ylabel="Deadline miss ratio",
        output_dir=output_dir,
    )


if __name__ == "__main__":
    main()
