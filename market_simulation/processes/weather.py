from random import randint
import random
import numpy as np
from multiprocessing import Process
from .sharedvariables import SharedVariables


class Weather(Process):
    def __init__(self, shared_variables: SharedVariables):
        super().__init__()
        self.shared_variables = shared_variables
        self.day = 0
        self.season = 0

    def run(self):
        self.shared_variables.sync_barrier.wait()
        while True:
            self.write()
            self.shared_variables.sync_barrier.wait()

    def write(self) -> None:
        """
        Update each day the weather conditions
        """
        with self.shared_variables.weather_shared.get_lock():
            self.updateSeason()
            # Temperature
            temperature = self.shared_variables.weather_shared[0] = int(
                random.gauss(25 - (6 * self.season), 4)
            )
            # Cloud coverage
            cloud_coverage = self.shared_variables.weather_shared[1] = randint(
                0, (30 * self.season) + 10
            )
            # Wind speed
            wind_speed = self.shared_variables.weather_shared[2] = int(
                np.random.lognormal(3.7, 0.4)
            )

            print(
                "****************************\n"
                f"** METEO REPORT - Season {self.season+1}**\n"
                f"The temperature is {temperature}°C\n"
                f"The cloud coverage is at {cloud_coverage}%\n"
                f"The wind speed is currently at {wind_speed} km/h\n"
                "****************************\n"
            )

    def kill(self) -> None:
        """
        Kills the process
        """
        print("Killing the weather. It might be the end of the world")
        super().kill()

    def updateSeason(self):
        self.day += 1
        self.season = round((self.day-2) / 4)
        if self.season > 3:
            self.day = 0
            self.season = 0
