from multiprocessing import Barrier, Process
import os

from .sharedvariables import SharedVariables
from .home import Home
import sysv_ipc


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
        city_homes_ipc_key: str,
        homes_city_ipc_key: str,
        city_market_ipc_key: str,
        market_city_ipc_key: str,
        base_consumption: int,
        minimal_consumption: int,
        wind_turbine_efficiency: float,
        solar_panel_efficiency: float,

    ) -> None:
        super().__init__()
        self.shared_variables = shared_variables
        self.home_number = home_number
        self.home_barrier = Barrier(self.home_number+1)

        self.city_homes_mq = sysv_ipc.MessageQueue(city_homes_ipc_key, sysv_ipc.IPC_CREAT)
        self.homes_city_mq = sysv_ipc.MessageQueue(homes_city_ipc_key, sysv_ipc.IPC_CREAT)

        self.city_market_mq = sysv_ipc.MessageQueue(city_market_ipc_key)
        self.market_city_mq = sysv_ipc.MessageQueue(market_city_ipc_key)

        self.city_pid = os.getpid()

        self.homes = [
            Home(
                home_barrier=self.home_barrier,
                weather_shared=shared_variables.weather_shared,
                home_pid=home_pid + 1,
                city_homes_ipc_key=city_homes_ipc_key,
                homes_city_ipc_key=homes_city_ipc_key,
                market_city_ipc_key=market_city_ipc_key,
                city_market_ipc_key=city_market_ipc_key,
                base_consumption=base_consumption,
                minimal_consumption=minimal_consumption,
                wind_turbine_efficiency=wind_turbine_efficiency,
                solar_panel_efficiency=solar_panel_efficiency,
                city_pid=self.city_pid
            )
            for home_pid in range(self.home_number)
        ]

        print("Starting city with {} homes.".format(self.home_number))
        for home in self.homes:
            home.start()

        

    def run(self):
        self.shared_variables.sync_barrier.wait()
        self.home_barrier.wait()
        try:
            while True:
                self.update()
        except KeyboardInterrupt:
            self.city_homes_mq.remove()
            self.homes_city_mq.remove()

    def update(self) -> None:
        """
        Function that the city runs each day
        """
        homes_messages = dict()
        total_production = 0
        total_consumption = 0

        for i in range(self.home_number):
            message, t = self.homes_city_mq.receive()
            message = message.decode()
            trade_type = int(message.split(';')[0])
            trade_value = int(message.split(';')[1])
            
            if trade_type == 1:
                total_production += trade_value
                homes_messages[t] = dict()
                homes_messages[t]["type"] = trade_type
                homes_messages[t]["value"] = trade_value
            elif trade_type == 2:
                homes_messages[t] = dict()
                total_consumption += trade_value
                homes_messages[t]["type"] = trade_type
                homes_messages[t]["value"] = trade_value

        print(
            "\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"
            "City\n"
            f"> Total energy wanted: {total_consumption}\n"
            f"> Total enery to sell: {total_production}\n"
            "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n"

        )
        if total_consumption > total_production:
            for pid in homes_messages:
                if homes_messages[pid]["type"] == 1:
                    message = str(homes_messages[pid]["value"]).encode()
                    self.city_homes_mq.send(message, type=pid)
                elif homes_messages[pid]["type"] == 2:
                    to_buy = int(homes_messages[pid]["value"] * total_production / total_consumption)
                    self.city_homes_mq.send(str(to_buy).encode(), type=pid)
        else:
            for pid in homes_messages:
                if homes_messages[pid]["type"] == 1:
                    to_sell = int(homes_messages[pid]["value"] * total_consumption / total_production)
                    self.city_homes_mq.send(str(to_sell).encode(), type=pid)
                elif homes_messages[pid]["type"] == 2:
                    message = str(homes_messages[pid]["value"]).encode()
                    self.city_homes_mq.send(message, type=pid)

        self.home_barrier.wait()
        self.city_market_mq.send(b"5;0;0")
        self.shared_variables.sync_barrier.wait()
        self.home_barrier.wait()

    def kill(self) -> None:
        """
        Brutaly kill the city and all its inhabitants
        """
        print("Killing the whole city")
        super().kill()
