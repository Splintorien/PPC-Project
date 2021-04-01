from multiprocessing import Process, Barrier, Array
from random import randint
import random
import sysv_ipc


class Home(Process):
    """
    Class representing a home that will communicate each day with the marketplace.
    """

    def __init__(
        self,
        home_barrier: Barrier,
        weather_shared: Array,
        home_pid: int,
        city_homes_ipc_key: str,
        homes_city_ipc_key: str,
        market_city_ipc_key: str,
        city_market_ipc_key: str,
        base_consumption: int,
        minimal_consumption: int,
        wind_turbine_efficiency: float,
        solar_panel_efficiency: float,
        city_pid: int,
    ) -> None:
        super().__init__()

        self.home_barrier = home_barrier
        self.weather_shared = weather_shared
        self.home_pid = home_pid
        self.city_pid = city_pid

        self.base_consumption = base_consumption
        self.real_consumption = 0
        self.minimal_consumption = minimal_consumption
        self.wind_turbine_efficiency = wind_turbine_efficiency
        self.solar_panel_efficiency = solar_panel_efficiency
        self.real_production = 0

        self.homes_city_mq = sysv_ipc.MessageQueue(homes_city_ipc_key)
        self.city_homes_mq = sysv_ipc.MessageQueue(city_homes_ipc_key)

        self.market_city_mq = sysv_ipc.MessageQueue(market_city_ipc_key)
        self.city_market_mq = sysv_ipc.MessageQueue(city_market_ipc_key)

        self.balance = 100

    def run(self) -> None:
        """
        Home run #Baseball
        """
        try:
            self.home_barrier.wait()
            while True:
                self.daily_turn()
                self.home_barrier.wait()
        except KeyboardInterrupt:
            print(f"Killing softly the home process {self.home_pid}\n", end="")

    def daily_turn(self) -> None:
        """
        The daily turn of each home, where they calculate their daily consumption
        """
        with self.weather_shared.get_lock():
            temperature = self.weather_shared[0]
            cloud_coverage = self.weather_shared[1]
            wind_speed = self.weather_shared[2]

        self.real_consumption = self.get_daily_consumption(temperature)
        self.real_production = self.get_daily_production(cloud_coverage, wind_speed)
        print(
            "\n-------------------------\n"
            f"Home {self.pid}\n"
            f"** Consumption: {self.real_consumption}\n"
            f"** Production: {self.real_production}\n"
            "-------------------------\n"
        )

        if self.real_production > self.real_consumption:
            # Home has energy to sell, so it sends a message of type 1
            energy_to_sell = self.real_production - self.real_consumption
            message = f"1;{energy_to_sell}".encode()
            self.homes_city_mq.send(message, type=self.pid)
            to_sell, t = self.city_homes_mq.receive(self.pid)
            self.real_production -= int(to_sell.decode())

            diff = self.real_production - self.real_consumption
            if diff > 0:
                self.city_market_mq.send(f"1;{self.pid};{diff}")
                message, t = self.market_city_mq.receive()
                price = message.decode('utf-8').split(';')[2]
                print(f"{self.home_pid} received {price} $")

        elif self.real_production < self.real_consumption:
            energy_to_buy = self.real_consumption - self.real_production
            message = f"2;{energy_to_buy}".encode()
            self.homes_city_mq.send(message, type=self.pid)
            to_buy, t = self.city_homes_mq.receive(self.pid)

            self.real_consumption -= int(to_buy.decode())
            diff = self.real_consumption - self.real_production
            if diff > 0:
                self.city_market_mq.send(f"2;{self.pid};{diff}")
                message, t = self.market_city_mq.receive()
                price = message.decode('utf-8').split(';')[2]
                print(f"{self.home_pid} paid {price} $")
        else:
            message = "0;0".encode()
            self.homes_city_mq.send(message, type=self.pid)

        self.home_barrier.wait()

    def get_daily_production(self, cloud_coverage: int, wind_speed: int) -> int:
        """
        Get the daily energy production (kWh) of a house considering the cloud coverage
        and the wind speed of the day
        """
        wind_prod = int(self.wind_turbine_efficiency * randint(0, wind_speed))
        solar_prod = int(
            self.solar_panel_efficiency * (100 - (randint(0, cloud_coverage)))
        )
        daily_production = wind_prod + solar_prod

        return daily_production

    def get_daily_consumption(self, temperature: int) -> int:
        """
        Allows to process and get the daily consumption, calculated from the temperature
        :param temperature: The temperature of the day
        :return: The daily consumption in kWh
        """

        daily_consumption = int(
            random.gauss(self.base_consumption - (3 * temperature), 4)
        )

        if daily_consumption < self.minimal_consumption:
            daily_consumption = self.minimal_consumption

        return daily_consumption

    def kill(self) -> None:
        print(f"Mass murdering the home {self.home_pid}")
        super().kill()
