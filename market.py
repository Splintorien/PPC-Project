import time
# import sys
# import random
import threading
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

MARKET_PRICE = 1
DAY = 0
threads = []
start_time = time.time()

''' Modulation coefficients for market price calculation '''
COEFFS = {
    'ATT': 0.99,
    'INTERN': [0, -0.01, 0.01],
    'EXTERN': [1],
}

''' Internal factors that influences market price'''
INTERNAL_FACTORS = {
    'TEMPERATURE': 20,
    'ENERGY_SOLD': 0,
    'ENERGY_BOUGHT': 0,
}

''' External factors that influences market price'''
EXTERNAL_FACTORS = {
    'DIPLOMATIC': 0,
}

def variation(coeffs: list, factors: dict):
    return sum([ a * b for a, b in zip(list(factors.values()), coeffs) ])

def newPrice(oldprice: float):

    attenuation_variation = COEFFS['ATT']*oldprice #Calculates price attenuation
    internal_variation = variation(COEFFS['INTERN'], INTERNAL_FACTORS)
    external_variation = variation(COEFFS['EXTERN'], EXTERNAL_FACTORS)
    return attenuation_variation + internal_variation + external_variation

def sendHome_Price(socket, mtype, pid, data):
    
    ''' Send the market price to Home '''
    
    socket.send(b"%s:%s:%s" %(mtype, pid, data))
    return

def newDay(marketprice: float):

    marketprice = newPrice(marketprice)

if __name__ == '__main__':

    print('''-------------------------------
                MARKET SIMULATION
    --------------------------------------''')

    while True:

        print('Waiting for home requests ...')
        message = socket.recv().decode('utf-8')
        print("Home connection received : %s" % message)

        data = message.split(';')

        if len(data) >= 2:
            mtype = data[0]
            pid = data[1]
            print('mtype : %s; pid : %s' %(mtype, pid))
        else:
            print('Incorrect format. Ignored message : %s' %message)

        #ASK PRICE
        if mtype == '1':
            thread = threading.Thread(target=sendHome_Price, args=(socket, '1', pid, MARKET_PRICE))
            thread.start()
            threads.append(thread)

        #NEXT DAY
        if mtype == '5':
            for thread in threads:
                thread.join()
            DAY += 1
            newDay(MARKET_PRICE)

        time.sleep(1)

