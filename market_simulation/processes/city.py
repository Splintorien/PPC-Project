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
        market_homes_ipc: str,
        base_consumption: int,
        plus_consumption: int,
        minus_consumption: int,
        base_production: int,
        plus_production: int,
        minus_production: int,
    ) -> None:
        super().__init__()
        self.shared_variables = shared_variables
        self.home_number = home_number
        self.home_barrier = Barrier(self.home_number+1)

        self.city_homes_mq = sysv_ipc.MessageQueue(city_homes_ipc_key, sysv_ipc.IPC_CREAT)
        self.homes_city_mq = sysv_ipc.MessageQueue(homes_city_ipc_key, sysv_ipc.IPC_CREAT)

        print("PID", os.getpid())
        self.city_pid = os.getpid()

        self.homes = [
            Home(
                home_barrier=self.home_barrier,
                weather_shared=shared_variables.weather_shared,
                home_pid=home_pid + 1,
                city_homes_ipc_key=city_homes_ipc_key,
                homes_city_ipc_key=homes_city_ipc_key,
                # market_homes_ipc=market_homes_ipc,
                base_consumption=base_consumption,
                minus_consumption=minus_consumption,
                plus_consumption=plus_consumption,
                base_production=base_production,
                minus_production=minus_production,
                plus_production=plus_production,
                city_pid=self.city_pid
            )
            for home_pid in range(self.home_number)
        ]

        print("Starting city with {} homes.".format(self.home_number))
        for home in self.homes:
            home.start()

        

    def run(self):
        self.home_barrier.wait()
        print("STARTING CITY")
        while True:
            self.update()
            self.shared_variables.sync_barrier.wait()

    def update(self) -> None:
        """
        Function that the city runs each day
        """
        homes_messages = dict()
        total_production = 0
        total_consumption = 0

        for i in range(self.home_number):
            print("Waiting to receive")
            message, t = self.homes_city_mq.receive()
            print(f"MESSAGE n°{i} RECEIVED", message.decode())
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

        print("CITY TOTAL CONSUMPTION", total_consumption)
        print("CITY TOTAL PRODUCTION", total_production)
        if total_consumption > total_production:
            print("HELLO THERE")
            for pid in homes_messages:
                if homes_messages[pid]["type"] == 1:
                    message = str(homes_messages[pid]["value"]).encode()
                    print(f"Message to buy {message}")
                    self.city_homes_mq.send(message, type=pid)
                elif homes_messages[pid]["type"] == 2:
                    to_buy = homes_messages[pid]["value"] * total_production / total_consumption
                    print(f"Sending to buy {to_buy}")
                    self.city_homes_mq.send(str(to_buy).encode(), type=pid)
        else:
            print("GENERAL KENOBI")
            for pid in homes_messages:
                if homes_messages[pid]["type"] == 1:
                    to_sell = homes_messages[pid]["value"] * total_consumption / total_production
                    print(f"Sending to sell {to_sell}")
                    self.city_homes_mq.send(str(to_sell).encode(), type=pid)
                elif homes_messages[pid]["type"] == 2:
                    message = str(homes_messages[pid]["value"]).encode()
                    print(f"Message to sell {message}")
                    self.city_homes_mq.send(message, type=pid)

        print("City arrived at barrier")
        self.home_barrier.wait()
        # self.market_pub.send(b"5;0;0")
        # print("Message sent to the bro market")

    def kill(self) -> None:
        """
        Brutaly kill the city and all its inhabitants
        """
        print("Killing the whole city")
        super().kill()
