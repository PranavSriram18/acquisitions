import random
from typing import Optional 

from acquisitions.game_logic.tile import *

class PlayerState:
    def __init__(self, name: str, money: int=6000, property=None, tiles=None):
        self.name = name
        self.money = money
        # number of shares owned of each hotel type
        self.property = property if property else [0] * NUM_HOTELS
        self.tiles = []

    def has_tile(self, tile: Tile) -> bool:
        return tile in self.tiles

class BankState:
    def __init__(self):
        self.property = [TOTAL_SHARES] * NUM_HOTELS
        self.tiles = [Tile(r, c) for r in range(NUM_ROWS) for c in range(NUM_COLS)]
        random.shuffle(self.tiles)

    def draw_tile(self) -> Optional[Tile]:
        return self.tiles.pop() if self.tiles else None
    