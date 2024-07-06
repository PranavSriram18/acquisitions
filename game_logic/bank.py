import random
from typing import List, Optional 

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.player import *
from acquisitions.game_logic.tile import *

class BankState:
    def __init__(self):
        self.property = [TOTAL_SHARES] * NUM_HOTELS
        self.tiles = [Tile(r, c) for r in range(NUM_ROWS) for c in range(NUM_COLS)]
        random.shuffle(self.tiles)

    def draw_tile(self, player: PlayerState):
        tile = self.tiles.pop() if self.tiles else None
        if tile:
            player.tiles.append(tile) 
    
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

    def tally_scores(self, players: List[PlayerState], hotel_sizes: List[int]):
        for hotel in Hotel:
            self.liquidate(players, hotel, hotel_sizes[hotel.value])

    def liquidate(self, players: List[PlayerState], hotel: Hotel, size: int):
        share_value = share_price(hotel, size)
        for player in players:
            player.money += share_value * player.property[hotel.value]
        # TODO - compensate majority and minority shareholders
