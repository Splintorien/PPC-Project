from multiprocessing import Process, Barrier, Array
from random import randint
import zmq


class Home(Process):
    """
    Class representing a home that will communicate each day with the marketplace.
    """

    def __init__(
        self,
        home_barrier: Barrier,
        weather_shared: Array,
        home_pid: int,
        homes_ipc_file: str,
        market_homes_ipc: str
    ) -> None:
        super().__init__()
        self.home_barrier = home_barrier
        self.weather_shared = weather_shared
        self.home_pid = home_pid
        self.consumption = 75
        self.market_mq = None

        self.context = zmq.Context()
        self.homes_pub = self.context.socket(zmq.PUB)
        self.homes_sub = self.context.socket(zmq.SUB)
        self.homes_pub.bind(homes_ipc_file)
        self.homes_sub.bind(homes_ipc_file)

        self.market_pub = self.context.socket(zmq.PUB)
        self.market_sub = self.context.socket(zmq.SUB)
        self.market_pub.bind(market_homes_ipc)
        self.market_sub.bind(market_homes_ipc)

        print('Home rdy')

    def run(self) -> None:
        """
        Home run #Baseball
        """
        try:
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

        self.consumption = Home.get_daily_consumption(temperature)

        print(f"$ Home {self.pid} consumption: {self.consumption}")
        self.market_pub.send_string("1;%s;%s"%(self.pid, self.consumption))
        self.home_barrier.wait()

    @staticmethod
    def get_daily_consumption(temperature: int) -> int:
        """
        Allows to process and get the daily consumption, calculated from the temperature
        :param temperature: The temperature of the day
        :return: The daily consumption in kWh
        """

        daily_consumption = 75 + randint(-10, 10)
        if temperature <= 0:
            daily_consumption += 20
        elif temperature >= 30:
            daily_consumption += 8

        return daily_consumption

    def kill(self) -> None:
        print(f"Mass murdering the home {self.home_pid}")
        super().kill()
