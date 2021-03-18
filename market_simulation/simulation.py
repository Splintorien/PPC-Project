from multiprocessing import Array, Barrier

from processes.sharedvariables import SharedVariables
from processes.daysynchronisation import DaySynchronisation
from processes.city import City

class Simulation:
    """
    Simulation class
    """

    def __init__(self) -> None:
        weather_shared = Array("i", 1)
        sync_barrier = Barrier(parties=2)

        self.shared_variables = SharedVariables(
            weather_shared=weather_shared,
            sync_barrier=sync_barrier
        )

        self.sync = DaySynchronisation(
            shared_variables=self.shared_variables,
            interval=5
        )

        self.city = City(
            shared_variables=self.shared_variables,
            home_number=4
        )

        self.city.start()
        self.sync.start()

        print("Simulation has been initialized")

if __name__ == "__main__":
    simulation = Simulation()
