import time
# import sys
import random
import signal
import concurrent.futures
import os
from multiprocessing import Process
import zmq


class Market():

    def __init__(
            self,
            #shared_variables: SharedVariables,
    ):

        super().__init__()
        self.context = zmq.Context()
        self.socket_pub = self.context.socket(zmq.PUB)
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_pub.bind('tcp://*:5558')
        self.socket_sub.bind('tcp://localhost:5557')

        self.market_price = 1.5
        self.day = 0
        self.threads = []
        self.start_time = time.time()

        # self.eventProcess = Process(target=self.EventsTrigger, args=())

        self.ENERGY = {
            'bought' : 0,
            'sold': 0,
            'bought_total': 0,
            'sold_total': 0,
        }

        ''' Modulation coefficients for market price calculation '''
        self.COEFFS = {
            'ATT': 0.99,
            'INTERN': [0, -0.01],
            'EXTERN': [1],
        }

        ''' Internal factors that influences market price'''
        self.INTERNAL_FACTORS = {
            'temperature': 20,
            'energy_stock': 0, #Difference between energy sold and energy bought
        }

        ''' External factors that influences market price'''
        self.EXTERNAL_FACTORS = {
            'DIPLOMATIC': 0,
            'NATURAL': 0,
        }

        self.run()

        

    def variation(self, coeffs: list, factors: dict):
        return sum([ a * b for a, b in zip(list(factors.values()), coeffs) ])


    def updatePrice(self, oldprice: float):

        attenuation_variation = self.COEFFS['ATT']*oldprice #Calculates price attenuation
        internal_variation = self.variation(self.COEFFS['INTERN'], self.INTERNAL_FACTORS)
        external_variation = self.variation(self.COEFFS['EXTERN'], self.EXTERNAL_FACTORS)
        return attenuation_variation + internal_variation + external_variation

    def sendMessage(self, mtype, pid, data):   
        ''' Send a message to Home '''
        response = (bytes("%s:%s:%s" %(mtype, pid, data), 'utf-8'))
        return self.socket_pub.send(response)
        

    def newDay(self):

        self.day += 1
        self.INTERNAL_FACTORS['energy_stock'] += (self.ENERGY['sold'] - self.ENERGY['bought'])
        self.market_price = self.updatePrice(self.market_price)
        self.ENERGY['bought'] = 0
        self.ENERGY['sold'] = 0

        print('starting new day...')

    def getMessage(self):
        return self.formatMessage(self.socket_sub.recv().decode('utf-8'))

    def formatMessage(self, message: str):
    
        if isinstance(message, str):
            data = message.split(';')
            if len(data) == 3:
                if all([ x.isdigit() for x in data]): #Si chaque valeur de data est un nombre
                    msg = {
                        'type' : data[0],
                        'pid' : data[1],
                        'value' : data[2]
                    }
                    return msg

        print('Incorrect format. Ignored message : %s' % message)
        return False

    def run(self):

        # signal.signal(signal.SIGUSR1, self.diplomaticEvent)
        # signal.signal(signal.SIGUSR2, self.naturalEvent)

        with concurrent.futures.ThreadPoolExecutor(max_workers = 100) as executor:
            while True:
                msg = self.getMessage()
                print("Home request received : %s" % msg)

                if msg:
                    if msg['type'] == '1':
                        executor.submit(self.sendMessage, '1', msg['pid'], self.market_price)
                    elif msg['type'] == '2':
                        executor.submit(self.sendMessage, '2', msg['pid'], self.market_price*int(msg['value']))
                        self.ENERGY['sold'] += int(msg['value'])
                    elif msg['type'] == '3':
                        executor.submit(self.sendMessage, '3', msg['pid'], self.market_price*int(msg['value']))
                        self.ENERGY['bought'] += int(msg['value'])
                    elif msg['type'] == '5':
                        self.newDay()

                time.sleep(0.1)

    def EventsTrigger(self):
        n = 50
        while True:
            time.sleep(1)
            x = random.randint(0,n)
            if x == 0:
                os.kill(os.getppid(), signal.SIGUSR1)
                n = 50
            if x == 1:
                os.kill(os.getppid(), signal.SIGUSR2)
                n = 50
            else:
                n += -1
    
    def diplomaticEvent(self):
        self.EXTERNAL_FACTORS['DIPLOMATIC'] = 1
    
    def naturalEvent(self):
        self.EXTERNAL_FACTORS['NATURAL'] = 1
            
    


if __name__ == '__main__':
    
    print('''-------------------------------
        MARKET SIMULATION
-------------------------------''')

    market = Market()
   

