from multiprocessing import Process
from .sharedvariables import SharedVariables


class SimulationProcess(Process):
    def __init__(self, shared_variables: SharedVariables):
        super().__init__()
        self.shared_variables = shared_variables

    def run(self):
        try:
            self.update()
            self.shared_variables.sync_barrier.wait()

            self.write()
            self.run()
        except KeyboardInterrupt:
            print("Killing the process", end="")

    def update(self) -> None:
        """
        Hello there! (General Kenobi?)
        """

    def write(self) -> None:
        """
        Goodbye there! (Private Grievious?)
        """
