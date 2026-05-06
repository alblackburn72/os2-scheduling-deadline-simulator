from dataclasses import dataclass
from typing import Literal

MemoryTier = Literal["local_dram", "remote_memory"]


@dataclass(frozen=True)
class Process:
    """
    Predstavlja 1 proces/task koji za raspoređivanje.

    arrival_time:
      Vreme kada proces postane ready

    burst_time:
      CPU vreme potrebno za završenje procesa

    deadline:
      Vreme do kojeg proces treba biti završen

    memory_tier:
      Simulirana memorijska lokacija
      Za sad ovo neće uticati na izvršavanje, ali kasnije će se koristiti za
      simuliranje daljinske sporije memorije

    memory_intensity:
      Koliko proces zavisi od pristupa memorije.
      Što veća vrednost znači da će proces biti više utican od spore memorije

    base_burst_time:
      burst_time pre nanosenja bilo kakvog memory penalty
      Ako je None, burst_time je base value
    """

    pid: str
    arrival_time: int
    burst_time: int
    deadline: int

    memory_tier: MemoryTier = "local_dram"
    memory_intensity: float = 1.0

    base_burst_time: int | None = None

    @property
    def resolved_base_burst_time(self) -> int:
        return (
            self.base_burst_time
            if self.base_burst_time is not None
            else self.burst_time
        )

    @property
    def effective_burst_time(self) -> int:
        return self.burst_time


@dataclass(frozen=True)
class ScheduledProcess:
    """
    Ovo je proces nakon što je raspoređen i završen
    """

    pid: str

    arrival_time: int
    burst_time: int
    deadline: int

    start_time: int
    completion_time: int
    memory_tier: MemoryTier = "local_dram"
    memory_intensity: float = 1.0
    base_burst_time: int | None = None

    @property
    def resolved_base_burst_time(self) -> int:
        return (
            self.base_burst_time
            if self.base_burst_time is not None
            else self.burst_time
        )

    @property
    def effective_burst_time(self) -> int:
        return self.burst_time

    @property
    def turnaround_time(self) -> int:
        return self.completion_time - self.arrival_time

    @property
    def waiting_time(self) -> int:
        return self.turnaround_time - self.burst_time

    @property
    def response_time(self) -> int:
        return self.start_time - self.arrival_time

    @property
    def deadline_missed(self) -> bool:
        return self.completion_time > self.deadline
