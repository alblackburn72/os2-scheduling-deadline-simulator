from dataclasses import dataclass, replace
from math import ceil

from scheduler.models import Process


@dataclass(frozen=True)
class MemoryPenaltyConfig:
    """ "
    Konfiguracije modela efekta usporene memorije kroz produzenje vremena izvrsavanja

    Primeri:
    - 0.25 - 25% dodatni trosak po memory_intensity jedinici
    - 0.75 - 75% dodatni trosak po memory_intensity jedinici
    - 1.00 - 100% dodatni trosak po memory_intensity jedinici
    """

    memory_penalty_factor: float = 0.5


def calculate_effective_burst_time(
    process: Process, config: MemoryPenaltyConfig
) -> int:
    """
    Racuna efektivan burst time nakon usporenja memorije
    local_dram:
      Nema penala
    remote_memory:
      povecan burst_time na osnovu memory_intensity
    Formula:
      effective_burst_time = ceil(burst_time * (1 + memory_penalty_factor * memory_intensity))
    """
    if process.memory_tier == "local_dram":
        return process.burst_time

    penalty_multiplier = 1 + config.memory_penalty_factor * process.memory_intensity

    return max(1, ceil(process.burst_time * penalty_multiplier))


def apply_memory_penalty(
    processes: list[Process], config: MemoryPenaltyConfig
) -> list[Process]:
    """
    Vraca novu listu procesa sa podesenim burst time

    Originalna lista ostaje neizmenjena
    """

    adjusted_processes: list[Process] = []

    for process in processes:
        effective_burst_time = calculate_effective_burst_time(process, config)

        adjusted_processes.append(
            replace(
                process,
                burst_time=effective_burst_time,
                base_burst_time=process.resolved_base_burst_time,
            )
        )

    return adjusted_processes
