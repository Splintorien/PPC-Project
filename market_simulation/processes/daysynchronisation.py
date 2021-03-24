from time import sleep

from multiprocessing import Process
from .sharedvariables import SharedVariables

class DaySynchronisation(Process):
    """
    Class used to display the current day and wait for a
    specified interval before beginning the next day
    """

    def __init__(self, shared_variables: SharedVariables, interval: int) -> None:
        super().__init__()
        self.shared_variables = shared_variables

        self.interval = interval
        self.day = 0

    def run(self):
        while True:
            self.write()
            self.shared_variables.sync_barrier.wait()
            self.update()

    def update(self) -> None:
        print(f"Day {self.day} ended, beginning day {self.day + 1}")

    def write(self) -> None:
        self.day += 1
        sleep(self.interval)
        print("Timer expired")

    def kill(self) -> None:
        print("Stopping day synchronisation")
        super().kill()
