from multiprocessing import Process, Barrier, Array
from random import randint
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
        base_consumption: int,
        minus_consumption: int,
        plus_consumption: int,
        base_production: int,
        minus_production: int,
        plus_production: int,
        city_pid: int
    ) -> None:
        super().__init__()

        print("HOME PID", home_pid)

        self.home_barrier = home_barrier
        self.weather_shared = weather_shared
        self.home_pid = home_pid
        self.city_pid = city_pid

        self.base_consumption = base_consumption
        self.real_consumption = 0
        self.minus_consumption = minus_consumption
        self.plus_consumption = plus_consumption

        self.base_production = base_production
        self.real_production = 0
        self.minus_production = minus_production
        self.plus_production = plus_production

        self.homes_city_mq = sysv_ipc.MessageQueue(homes_city_ipc_key)
        self.city_homes_mq = sysv_ipc.MessageQueue(city_homes_ipc_key)


    def run(self) -> None:
        """
        Home run #Baseball
        """
        try:
            self.home_barrier.wait()
            print(f"STARTING HOME {self.pid}")
            while True:
                self.daily_turn()
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
            "\n-------------\n"
            f"Home {self.pid}\n"
            f"** Consumption: {self.real_consumption}\n"
            f"** Production: {self.real_production}\n"
            "-------------\n"
        )

        if self.real_production > self.real_consumption:
            # Home has energy to sell, so it sends a message of type 1
            energy_to_sell = self.real_production - self.real_consumption
            message = f"2;{energy_to_sell}".encode()
            self.homes_city_mq.send(message, type=self.pid)
            to_sell, t = self.city_homes_mq.receive(self.pid)
            print(f"HOME n°{self.pid} : TO SELL {to_sell.decode()}")
        elif self.real_production < self.real_consumption:
            energy_to_buy = self.real_consumption - self.real_production
            message = f"2;{energy_to_buy}".encode()
            self.homes_city_mq.send(message, type=self.pid)
            to_buy, t = self.city_homes_mq.receive(self.pid)
            print(f"HOME n°{self.pid} : TO BUY {to_buy.decode()}")
        else:
            message = "0;0".encode()
            self.homes_city_mq.send(message, type=self.pid)

        self.home_barrier.wait()

    def get_daily_production(self, cloud_coverage: int, wind_speed: int) -> int:
        """
        Get the daily energy production of a house considering the cloud coverage
        and the wind speed of the day
        """
        return 0

    def get_daily_consumption(self, temperature: int) -> int:
        """
        Allows to process and get the daily consumption, calculated from the temperature
        :param temperature: The temperature of the day
        :return: The daily consumption in kWh
        """

        daily_consumption = self.base_consumption + randint(self.minus_consumption, self.plus_consumption)
        if temperature <= 0:
            daily_consumption += 20
        elif temperature >= 30:
            daily_consumption += 8

        return daily_consumption

    def kill(self) -> None:
        print(f"Mass murdering the home {self.home_pid}")
        super().kill()
