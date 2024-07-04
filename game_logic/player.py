from hotel import *

class PlayerState:
    def __init__(self, name: str, money: int=6000, property=None):
        self.name = name
        self.money = money
        # number of shares owned of each hotel type
        self.property = property if property else [0] * NUM_HOTELS

class BankState:
    def __init__(self):
        self.property = [TOTAL_SHARES] * NUM_HOTELS
        