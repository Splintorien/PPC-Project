from multiprocessing import Array, Barrier, Process
import sys
import sysv_ipc
import time

from .sharedvariables import SharedVariables
from .home import Home


class City(Process):
    """
    Class City that represents a group of homes.
    This process will be used to launch all the home processes and instanciate communication
    between homes.
    """

    def __init__(
        self,
        shared_variables: SharedVariables,
        home_number: int,
        homes_ipc_file: str,
        market_homes_ipc: str
    ) -> None:
        super().__init__()
        self.shared_variables = shared_variables
        self.home_number = home_number
        self.home_barrier = Barrier(self.home_number+1)

        
        self.market2city = sysv_ipc.MessageQueue(101, sysv_ipc.IPC_CREAT)

        self.city2homes = sysv_ipc.MessageQueue(200, sysv_ipc.IPC_CREAT)
        self.homes2city = sysv_ipc.MessageQueue(201, sysv_ipc.IPC_CREAT)

        self.homes = [
            Home(
                home_barrier=self.home_barrier,
                weather_shared=shared_variables.weather_shared,
                home_pid=home_pid + 1,
                homes_ipc_file=homes_ipc_file,
                market_homes_ipc=market_homes_ipc
            )
            for home_pid in range(self.home_number)
        ]

        print("Starting city with {} homes.".format(self.home_number))
        for home in self.homes:
            home.start()

        

    def run(self):
        print('City ready')
        self.shared_variables.sync_barrier.wait()
        time.sleep(0.1)
        self.city2market = sysv_ipc.MessageQueue(100)
        
        while True:
            self.update()
            self.shared_variables.sync_barrier.wait()

    def update(self) -> None:
        """
        Function that the city runs each day
        """
        
        self.city2market.send(b"5;0;0")
        print("City : sent new day to market")
        #wait for reply

        self.home_barrier.wait()
        self.market_pub.send(b"5;0;0")
        print("Message sent to the bro market")

    def kill(self) -> None:
        """
        Brutaly kill the city and all its inhabitants
        """
        print("Killing the whole city")
        super().kill()
