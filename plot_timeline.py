import argparse
import csv
import colorsys
import random
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

DEFAULT_TIMELINE_PATH = Path("results/experiments/basic/timeline.csv")
DEFAULT_OUTPUT_DIR = Path("results/experiments/plots/timeline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Gantt/timeline plots from timeline.csv"
    )

    parser.add_argument(
        "--input", default=str(DEFAULT_TIMELINE_PATH), help="Path to timeline.csv"
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where timeline plots will be saved",
    )

    return parser.parse_args()


def build_process_color(
    process_ids: list[str],
) -> dict[str, tuple[float, float, float]]:
    """
    Dodeljujem razlicite boje za svaki proces. Boje se generisu automatski za svaki proces.
    """

    rng = random.Random(42)

    count = max(1, len(process_ids))
    hues = [index / count for index in range(count)]
    rng.shuffle(hues)

    process_colors: dict[str, tuple[float, float, float]] = {}

    for pid, hue in zip(process_ids, hues):
        saturation = 0.65 + 0.15 * rng.random()
        value = 0.75 + 0.15 * rng.random()

        process_colors[pid] = colorsys.hsv_to_rgb(hue, saturation, value)

    return process_colors


def get_text_color(rgb_color: tuple[float, float, float]) -> str:
    """
    Bira se crni ili beli tekst u zavisnosti od osvetljenja pozadine, da
    mozemo da procitamo oznaku procesa
    """

    red, green, blue = rgb_color
    luminance = 0.299 * red + 0.587 * green + 0.114 * blue

    return "black" if luminance > 0.6 else "white"


def load_timeline_rows(input_path: Path) -> list[dict[str, str]]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Timeline file not found: {input_path}."
            "Run main.py or run_experiments.py first."
        )

    with input_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def group_rows_by_algorithm(
    rows: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    grouped_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        grouped_rows[row["algorithm_name"]].append(row)

    return grouped_rows


def sanitize_filename(value: str) -> str:
    return value.replace("/", "_").replace("\\", "_").replace(" ", "_")


def plot_timeline_for_algorithms(
    algorithm_name: str,
    rows: list[dict[str, str]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    process_ids = sorted({row["pid"] for row in rows})
    process_positions = {pid: index * 10 for index, pid in enumerate(process_ids)}

    process_colors = build_process_color(process_ids)

    plt.figure(figsize=(10, 4))

    for row in rows:
        pid = row["pid"]
        start_time = int(row["start_time"])
        duration = int(row["duration"])

        color = process_colors[pid]
        y_position = process_positions[pid]

        plt.broken_barh(
            [(start_time, duration)],
            (process_positions[pid], 8),
            facecolors=color,
            edgecolors="black",
        )

        plt.text(
            start_time + duration / 2,
            y_position + 4,
            pid,
            ha="center",
            va="center",
            fontsize=9,
            color=get_text_color(color),
        )

    y_ticks = [position + 4 for position in process_positions.values()]

    plt.yticks(y_ticks, process_ids)
    plt.xlabel("Time")
    plt.ylabel("Process")
    plt.title(f"Execution timeline - {algorithm_name}")
    plt.grid(axis="x")
    plt.tight_layout()

    output_path = output_dir / f"{sanitize_filename(algorithm_name)}.png"
    plt.savefig(output_path)
    plt.close()

    print(f"Saved timeline plot: {output_path}")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    rows = load_timeline_rows(input_path)
    grouped_rows = group_rows_by_algorithm(rows)

    for algorithm_name, algorithm_rows in grouped_rows.items():
        plot_timeline_for_algorithms(
            algorithm_name=algorithm_name, rows=algorithm_rows, output_dir=output_dir
        )

    print()
    print("All timeline plots generated.")


if __name__ == "__main__":
    main()
