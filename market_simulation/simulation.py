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
            sync_barrier = Barrier(parties=4)

            self.shared_variables = SharedVariables(
                weather_shared=weather_shared, sync_barrier=sync_barrier
            )

            self.sync = DaySynchronisation(
                shared_variables=self.shared_variables,
                interval=config["simulation"]["interval"],
            )

            self.market = Market(
                shared_variables=self.shared_variables,
                coeffs=config["market"]["coeffs"],
                internal_factors=config["market"]["internal_factors"],
                external_factors=config["market"]["external_factors"],
                market_city_ipc_key=config["city"]["market_city_ipc_key"],
                city_market_ipc_key=config["city"]["city_market_ipc_key"],
                event_probability=config["market"]["event_probability"]
            )

            self.city = City(
                shared_variables=self.shared_variables,
                home_number=config["city"]["home_number"],
                homes_city_ipc_key=config["city"]["homes_city_ipc_key"],
                city_homes_ipc_key=config["city"]["city_homes_ipc_key"],
                market_city_ipc_key=config["city"]["market_city_ipc_key"],
                city_market_ipc_key=config["city"]["city_market_ipc_key"],
                base_consumption=config["city"]["base_consumption"],
                minimal_consumption=config["city"]["minimal_consumption"],
                wind_turbine_efficiency=config["city"]["wind_turbine_efficiency"],
                solar_panel_efficiency=config["city"]["solar_panel_efficiency"],
            )

            self.weather = Weather(shared_variables=self.shared_variables)

            # self.market = Market(
            #     shared_variables=self.shared_variables,
            #     market_homes_ipc=config["market"]["market_homes_ipc"]
            # )

            self.city.start()
            self.sync.start()
            self.weather.start()
            self.market.start()

            print("°°° Simulation has been initialized °°°\n\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Missing config file.\n"
            "Please run the following command : python simulation.py <config_file>"
        )
    else:
        simulation = Simulation(sys.argv[1])
