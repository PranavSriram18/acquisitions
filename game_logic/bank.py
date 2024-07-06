import random
from typing import List, Optional, Tuple 

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

    def execute_transaction(
            self, 
            player: PlayerState, 
            buy_order: List[int],
            hotel_sizes: List[int]) -> Tuple[bool, str]:
        """ 
        buy_order is a list of quantities of each share player wants.
        """
        valid, cost, msg = self.validate_transaction(player, buy_order, hotel_sizes)
        if not valid:
            return False, msg    
        player.money -= cost
        for i in range(NUM_HOTELS):
            player.property[i] += buy_order[i]
            self.property[i] -= buy_order[i]
        msg += f"Property for {player.name}: {player.property}"
        return True, msg

    def validate_transaction(
            self, 
            player: PlayerState, 
            buy_order: List[int],
            hotel_sizes: List[int]) -> Tuple[bool, int, str]:
        share_prices = [share_price(hotel, size) for (hotel, size) in zip(Hotel, hotel_sizes)]
        total_shares = sum(buy_order)
        if total_shares > MAX_SHARES_PER_TURN:
            msg = f"Transaction rejected. Max {MAX_SHARES_PER_TURN} can be purchased in one turn. Please try again."
            return False, 0, msg            
        cost = 0
        for (hotel, num_shares, size, price) in zip(Hotel, buy_order, hotel_sizes, share_prices):
            if size == 0 and num_shares > 0:
                msg = f"Transaction rejected; attempt to purchase {hotel.name}, which is not on board. Please try again."
                return False, 0, msg
            if num_shares > self.property[hotel.value]:
                msg = f"Transaction rejected; only {self.property[hotel.value]} shares of {hotel.name} available. Please try again."
                return False, 0, msg
            cost += num_shares * price
        if cost > player.money:
            msg = "Transaction rejected; player has insufficient funds. Please try again."
            return False, 0, msg
        msg = "Transaction successful!"
        return True, cost, msg
    
    def grant_awards(self, players: List[PlayerState], hotel: Hotel, size):
        pass # TODO

    def liquidate_shares(
            self, 
            player: PlayerState, 
            liquidated_hotel: Hotel,
            size: int,
            sell: int, 
            twofer: int, 
            owning_hotel: Hotel) -> Tuple[bool, str]:
        # validation
        transaction_shares = sell + twofer 
        if transaction_shares > player.property[liquidated_hotel.value]:
            msg = f"{player.name} does not have enough shares for this transaction. Please try again."
            return False, msg
        
        if twofer % 2:
            msg = "Rolling over remainder of twofer to sell"
            twofer -= 1
            sell += 1

        owning_hotel_shares = twofer // 2
        if self.property[owning_hotel.value] < owning_hotel_shares:
            msg = f"Rejecting transaction; bank has insufficient shares of {owning_hotel.name} for selected twofer. Please try again."
            return False, msg
        
        # execution
        price = share_price(liquidated_hotel, size)
        player.money += price * sell
        player.property[liquidated_hotel.value] -= transaction_shares
        self.property[liquidated_hotel.value] += transaction_shares
        player.property[owning_hotel.value] += owning_hotel_shares
        self.property[owning_hotel.value] -= owning_hotel_shares
        return True, "success"    

    def tally_scores(self, players: List[PlayerState], hotel_sizes: List[int]):
        for (hotel, size) in zip(Hotel, hotel_sizes):
            if hotel.value < NUM_HOTELS:
                self.liquidate_all(players, hotel, hotel_sizes[hotel.value])

    def liquidate_all(
            self, players: List[PlayerState], hotel: Hotel, size: int):
        self.grant_awards(players, hotel, size)
        share_value = share_price(hotel, size)
        for player in players:
            player.money += share_value * player.property[hotel.value]
