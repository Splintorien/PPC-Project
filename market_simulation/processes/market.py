import time

# import sys
import random
import signal
import concurrent.futures
import os
from multiprocessing import Process
import sysv_ipc
from .sharedvariables import SharedVariables
import math


class Market(Process):
    def __init__(
        self,
        shared_variables: SharedVariables,
        coeffs,
        internal_factors,
        external_factors,
        market_city_ipc_key: str,
        city_market_ipc_key: str,
        event_probability: int,
    ):

        super().__init__()
        self.shared_variables = shared_variables

        self.city2market = sysv_ipc.MessageQueue(
            city_market_ipc_key, sysv_ipc.IPC_CREAT
        )
        self.market2city = sysv_ipc.MessageQueue(
            market_city_ipc_key, sysv_ipc.IPC_CREAT
        )

        self.market_price = 1.5
        self.day = 0
        self.threads = []
        self.event_probability = event_probability

        self.ENERGY = {
            "bought": 0,
            "sold": 0,
            "bought_total": 0,
            "sold_total": 0,
        }

        """ Modulation coefficients for market price calculation """
        self.COEFFS = coeffs
        """ Internal factors that influences market price"""
        self.INTERNAL_FACTORS = internal_factors
        """ External factors that influences market price"""
        self.EXTERNAL_FACTORS = external_factors

    def variation(self, coeffs: list, factors: dict):
        return sum([a * b for a, b in zip(list(factors.values()), coeffs)])

    def calc_stock(self, sold, bought):
        """Calculates new energy stock influence"""
        stock = self.INTERNAL_FACTORS["energy_stock"] + (sold - bought)
        if stock == 0:
            self.INTERNAL_FACTORS["energy_stock"] = 0
        elif stock < 0:
            self.INTERNAL_FACTORS["energy_stock"] = -1 * math.log(abs(stock))
        else:
            self.INTERNAL_FACTORS["energy_stock"] = math.log(stock)

    def update_price(self, oldprice: float):

        attenuation_variation = (
            self.COEFFS["att"] * oldprice
        )  # Calculates price attenuation
        internal_variation = self.variation(
            self.COEFFS["intern"], self.INTERNAL_FACTORS
        )
        external_variation = self.variation(
            self.COEFFS["extern"], self.EXTERNAL_FACTORS
        )
        price = round(
            attenuation_variation + internal_variation + external_variation, 2
        )
        return price

    def send_message(self, mtype, pid, data):
        """ Send a message to Home """
        response = bytes("%s;%s;%s" % (mtype, pid, data), "utf-8")
        return self.market2city.send(response)

    def new_day(self):

        self.day += 1
        self.calc_stock(self.ENERGY["sold"], self.ENERGY["bought"])
        self.market_price = self.update_price(self.market_price)
        self.ENERGY["bought"] = 0
        self.ENERGY["sold"] = 0

        print("Market Price is at : %s$/KWh" % self.market_price)
        print(
            "Market stock difference : %s" % self.INTERNAL_FACTORS["energy_stock"]
        )
        self.shared_variables.sync_barrier.wait()

    def get_message(self):
        message, t = self.city2market.receive()
        return self.formatMessage(message.decode("utf-8"))

    def formatMessage(self, message: str):
        if isinstance(message, str):
            data = message.split(";")
            if len(data) == 3:
                if all(
                    [x.isdigit() for x in data]
                ):  # Si chaque valeur de data est un nombre
                    msg = {"type": data[0], "pid": data[1], "value": data[2]}
                    return msg

        print("Incorrect format. Ignored message : %s" % message)
        return False

    def run(self):
        try:
            signal.signal(signal.SIGUSR1, self.diplomatic_event)
            signal.signal(signal.SIGUSR2, self.natural_event)

            self.eventProcess = Process(target=self.events_trigger, args=())
            self.eventProcess.start()

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                self.shared_variables.sync_barrier.wait()

                while True:
                    msg = self.get_message()

                    if msg:
                        if msg["type"] == "1":
                            executor.submit(
                                self.send_message,
                                "1",
                                msg["pid"],
                                round(self.market_price * int(msg["value"]), 2),
                            )
                            self.ENERGY["sold"] += int(msg["value"])
                        elif msg["type"] == "2":
                            executor.submit(
                                self.send_message,
                                "2",
                                msg["pid"],
                                round(self.market_price * int(msg["value"]), 2),
                            )
                            self.ENERGY["bought"] += int(msg["value"])
                        elif msg["type"] == "5":
                            self.new_day()
        except KeyboardInterrupt:
            self.market2city.remove()
            self.city2market.remove()

    def events_trigger(self):
        n = 50
        while True:
            time.sleep(self.event_probability)
            x = random.randint(0, n)
            if x == 0:
                print("KILLING OS")
                os.kill(os.getpid(), signal.SIGUSR1)
                n = 50
            if x == 1:
                os.kill(os.getpid(), signal.SIGUSR2)
                n = 50
            else:
                n += -1

    def diplomatic_event(self, sig, _):
        self.EXTERNAL_FACTORS['diplomatic'] = 1
        print(
            "£££££££££££££££££££££££££££££££££\n"
            "DIPLOMATIC EVENT TRIGGERED !\n"
            "£££££££££££££££££££££££££££££££££\n"
        )

    def natural_event(self, sig, _):
        self.EXTERNAL_FACTORS['natural'] = 1
        print(
            "£££££££££££££££££££££££££££££££££\n"
            "NATURAL EVENT TRIGGERED !\n"
            "£££££££££££££££££££££££££££££££££\n"
        )
