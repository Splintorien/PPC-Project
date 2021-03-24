from multiprocessing import Array, Barrier
import json
import sys

from processes.sharedvariables import SharedVariables
from processes.daysynchronisation import DaySynchronisation
from processes.city import City
from processes.weather import Weather
from processes.market import Market

class Simulation:
    """
    Simulation class
    """

    def __init__(self, config_file: str) -> None:
        with open(config_file) as file:
            config = json.load(file)
            weather_shared = Array("i", 3)
            sync_barrier = Barrier(parties=3)

            self.shared_variables = SharedVariables(
                weather_shared=weather_shared,
                sync_barrier=sync_barrier
            )

            self.sync = DaySynchronisation(
                shared_variables=self.shared_variables,
                interval=config["simulation"]["interval"]
            )

            self.city = City(
                shared_variables=self.shared_variables,
                home_number=config["city"]["home_number"],
                homes_ipc_file=config["city"]["homes_ipc_file"]
            )

            self.weather = Weather(
                shared_variables=self.shared_variables
            )

            self.market = Market(
                shared_variables=self.shared_variables,
                market_homes_ipc=config["market"]["market_homes_ipc"]
            )

            self.city.start()
            self.sync.start()
            self.weather.start()

            print("Simulation has been initialized")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Missing config file.\n"
            "Please run the following command : python simulation.py <config_file>"
        )
    else:
        simulation = Simulation(sys.argv[1])
