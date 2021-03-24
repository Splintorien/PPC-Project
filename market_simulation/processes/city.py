from multiprocessing import Array, Barrier
import sys
import zmq

from .simulationprocess import SimulationProcess
from .sharedvariables import SharedVariables
from .home import Home


class City(SimulationProcess):
    """
    Class City that represents a group of homes.
    This process will be used to launch all the home processes and instanciate communication
    between homes.
    """

    def __init__(
        self,
        shared_variables: SharedVariables,
        home_number: int,
        homes_ipc_file: str
    ) -> None:
        super().__init__(shared_variables)
        self.home_number = home_number
        self.home_barrier = Barrier(self.home_number + 1)

        self.context = zmq.Context()
        self.homes_pub = self.context.socket(zmq.PUB)
        self.homes_sub = self.context.socket(zmq.SUB)
        self.homes_pub.bind(homes_ipc_file)
        self.homes_sub.bind(homes_ipc_file)

        self.homes = [
            Home(
                home_barrier=self.home_barrier,
                weather_shared=shared_variables.weather_shared,
                home_pid=home_pid + 1,
                homes_ipc_file=homes_ipc_file
            )
            for home_pid in range(self.home_number)
        ]

        print("Starting city with {} homes.".format(self.home_number))

        for home in self.homes:
            home.start()

    def update(self) -> None:
        """
        Function that the city runs each day
        """
        self.home_barrier.wait()

    def kill(self) -> None:
        """
        Brutaly kill the city and all its inhabitants
        """
        print("Killing the whole city")
        super().kill()
