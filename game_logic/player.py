import random
from typing import Optional 

from acquisitions.game_logic.tile import *
from acquisitions.game_logic.constants import *

class PlayerState:
    def __init__(self, name: str, money: int=6000, property=None, tiles=None):
        self.name = name
        self.money = money
        # number of shares owned of each hotel type
        self.property = property if property else [0] * NUM_HOTELS
        self.tiles = []

    def has_tile(self, tile: Tile) -> bool:
        return tile in self.tiles
    
    def display_property(self):
        print(f"Propery for {self.name}: ")
        for (hotel, num_shares) in zip(Hotel, self.property):
            if num_shares > 0:
                print(f"{hotel.name}: {num_shares}")
        print(f"Cash: {self.money}")
