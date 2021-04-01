from dataclasses import dataclass
from multiprocessing import Array, Barrier


@dataclass
class SharedVariables:
    weather_shared: Array
    sync_barrier: Barrier
