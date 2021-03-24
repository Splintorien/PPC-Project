from random import randint

from .simulationprocess import SimulationProcess


class Weather(SimulationProcess):
    def write(self) -> None:
        """
        Update each day the weather conditions
        """
        with self.shared_variables.weather_shared.get_lock():
            # Temperature
            temperature = self.shared_variables.weather_shared[0] = randint(15, 25)
            # CLoud coverage
            cloud_coverage = self.shared_variables.weather_shared[1] = randint(0, 80)
            # Wind speed
            wind_speed = self.shared_variables.weather_shared[2] = randint(0, 140)

            print(
                "** METEO REPORT **\n"
                f"The temperature is {temperature}°C\n"
                f"The cloud coverage is at {cloud_coverage}%\n"
                f"The wind speed is currently at {wind_speed} km/h\n"
            )

    def kill(self) -> None:
        """
        Kills the process
        """
        print("Killing the weather. It might be the end of the world")
        super().kill()
