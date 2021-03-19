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



items = list(INTERNAL_FACTORS.values())

dictlist = [ a * b for a, b in zip(items, COEFFS['INTERN']) ]

