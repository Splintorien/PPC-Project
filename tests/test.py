import numpy as np
import random


COEFFS = {
    'ATT': 0.99,
    'INTERN': [0, -0.01, 0.01],
    'EXTERN': 1
}

INTERNAL_FACTORS = {
    'TEMPERATURE': 20,
    'ENERGY_SOLD': 0,
    'ENERGY_BOUGHT': 0
}


wind = 0
season = 2
day = 6

season = round((day-5) / 10)
temperature = int(random.gauss(25 - (5*season), 4))
wind = int(np.random.lognormal(3.7, 0.5))
daily_consumption = int(random.gauss(100 - (3*temperature), 4))

print(f'Season : {season}, temperature : {temperature}, Wind speed : {wind}, daily_cons : {daily_consumption}')