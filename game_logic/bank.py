import random
from typing import Optional 

from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *

class BankState:
    def __init__(self):
        self.property = [TOTAL_SHARES] * NUM_HOTELS
        self.tiles = [Tile(r, c) for r in range(NUM_ROWS) for c in range(NUM_COLS)]
        random.shuffle(self.tiles)

    def draw_tile(self) -> Optional[Tile]:
        return self.tiles.pop() if self.tiles else None
    
    def issue_free_share(self, player: PlayerState, hotel: Hotel):
        if self.property[hotel.value] > 0:
            player.property[hotel.value] += 1
            self.property[hotel.value] -= 1

    def sell_shares(self, player: PlayerState, hotel: Hotel, num_shares: int):
        """
        Sell shares to the given player.
        """
        if self.property[hotel.value] < num_shares:
            print("Bank has insufficient shares")
            return
        pass  # TODO
        

    