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
            self.transfer(player, hotel, 1)

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
        msg += f"Awarding the following shares: \n"
        for (hotel, shares) in filter(lambda p: p[1], zip(Hotel, buy_order)):
            msg += f"{hotel.name}: {shares}, "
            self.transfer(player, hotel, shares)
        return True, msg

    def validate_transaction(
            self, 
            player: PlayerState, 
            buy_order: List[int],
            hotel_sizes: List[int]) -> Tuple[bool, int, str]:
        share_prices = [share_price(hotel, size) for (hotel, size) in zip(Hotel, hotel_sizes)]
        total_shares = sum(buy_order)
        if total_shares > MAX_SHARES_PER_TURN:
            msg = f"Transaction rejected.\n Max {MAX_SHARES_PER_TURN} can be purchased in one turn. Please try again."
            return False, 0, msg 
        if any(x < 0 for x in buy_order):
            msg = (
                f"Transaction rejected. Cannot have negative "
                f"entries in buy order. Please try again."
            )
            return False, 0, msg

        cost = 0
        for (hotel, num_shares, size, price) in zip(Hotel, buy_order, hotel_sizes, share_prices):
            if size == 0 and num_shares > 0:
                msg = (
                    f"Transaction rejected; attempt to purchase {hotel.name} "
                    f"which is not on board. Please try again."
                )
                return False, 0, msg
            if num_shares > self.property[hotel.value]:
                msg = (
                    f"Transaction rejected; only {self.property[hotel.value]} "
                    f"shares of {hotel.name} available. Please try again."
                )
                return False, 0, msg
            cost += num_shares * price
        if cost > player.money:
            msg = (
                f"Transaction rejected; player has insufficient funds.\n"
                f"Please try again."
            )
            return False, 0, msg
        msg = f"Transaction valid!\n"
        return True, cost, msg
    
    def grant_awards(self, players: List[PlayerState], hotel: Hotel, size):
        """
        In the most common case, the player with the most shares of hotel
        receives a majority award, and the player with the 2nd most shares
        receives a minority award. However, there are several tricky edge cases
        to deal with. We enumerate all cases below:
        Case 0: No one has any shares of the hotel (extremely rare). Then no one
        gets an award.
        Case 1: 2 or more players tied for 1st. They split the total 
        (majority+minority) bonus.
        Case 2: 1 winner, rest of players have 0 shares. The winner receives
        both majority and minority bonuses.
        Case 3: The common case; 1 winner and 1 runner-up.
        Case 4: 1 winner, 2 or more players tied for runner up. The runners up
        split the minority bonus.
        """
        ownership = [p.property[hotel.value] for p in players]
        ranking = sorted(zip(players, ownership), key=lambda x: -x[1])
        msg = f"Granting awards for {hotel.name}.\n"
        if ranking[0][1] == 0:
            msg += f"No shareholders of {hotel.name}"
            return msg  # Case 0
        
        majority_bonus = majority_holder_award(hotel, size)
        minority_bonus = minority_holder_award(hotel, size)
        msg += (
            f"Majority and minority awards are "
            f"{majority_bonus} and {minority_bonus}.\n"
        )
        num_majority_holders = sum(1 for x in ranking if x[1] == ranking[0][1])
        if num_majority_holders >= 2:  # Case 1
            msg += f"Splitting majority bonus among: "
            bonus_per_winner = (majority_bonus + minority_bonus) // num_majority_holders
            bonus_per_winner = (bonus_per_winner // 100) * 100  # round to nearest 100
            for i in range(num_majority_holders):
                ranking[i][0].money += bonus_per_winner
                msg += f"{ranking[i][0].name}, "
            return
        # Cases 2-4
        msg += f"Awarding majority bonus to: {ranking[0][0].name}\n"
        ranking[0][0].money += majority_bonus
        num_minority_holders = sum(1 for x in ranking if x[1] == ranking[1][1] and x[1] > 0)
        if num_minority_holders == 0:  # Case 2
            msg += f"No minority holders; awarding minority bonus " \
                 f"to {ranking[0][0].name}"
            ranking[0][0].money += minority_bonus
            return msg
        # Cases 3 and 4
        bonus_per_runnerup = minority_bonus // num_minority_holders
        bonus_per_runnerup = (bonus_per_runnerup // 100) * 100
        msg += f"Awarding minority grant to: " 
        for i in range(1, num_minority_holders+1):
            msg += f"{ranking[i][0].name}, "
            ranking[i][0].money += bonus_per_runnerup
        return msg

    def liquidate_shares(
            self, 
            player: PlayerState, 
            liquidated_hotel: Hotel,
            size: int,
            sell: int, 
            twofer: int, 
            owning_hotel: Hotel) -> Tuple[bool, str]:
        # validation
        msg = ""
        transaction_shares = sell + twofer 
        if transaction_shares > player.property[liquidated_hotel.value]:
            msg = (
                f"{player.name} does not have enough shares for this"
                f"transaction. Please try again."
            )
            return False, msg
        
        if twofer % 2:
            msg = "Rolling over remainder of twofer to sell\n"
            twofer, sell = twofer-1, sell+1

        owning_hotel_shares = twofer // 2
        if self.property[owning_hotel.value] < owning_hotel_shares:
            msg = (
                f"Rejecting transaction; bank has insufficient shares of" 
                f"{owning_hotel.name} for selected twofer. Please try again."
            )
            return False, msg
        
        # execution
        player.money += share_price(liquidated_hotel, size) * sell
        self.transfer(player, liquidated_hotel, -transaction_shares)
        self.transfer(player, owning_hotel, owning_hotel_shares)
        return True, msg + f"\nLiquidation successful"

    def tally_scores(
            self, players: List[PlayerState], hotel_sizes: List[int]) -> str:
        for (hotel, size) in zip(Hotel, hotel_sizes):
            if hotel.value < NUM_HOTELS:
                self.liquidate_all(players, hotel, hotel_sizes[hotel.value])
        msg = f"Final scores:\n "
        scores = [p.money for p in players]
        rankings = sorted(zip(players, scores), key=lambda x: -x[1])
        for (player, money) in rankings:
            msg += f"{player.name}: {money} \n"
        # TODO - handle ties
        msg += f"The winner is: {rankings[0][0].name}. Congratulations!"
        return msg

    def liquidate_all(
            self, players: List[PlayerState], hotel: Hotel, size: int):
        self.grant_awards(players, hotel, size)
        share_value = share_price(hotel, size)
        for player in players:
            player.money += share_value * player.property[hotel.value]

    def transfer(self, player: PlayerState, hotel: Hotel, k: int):
        """
        Transfer k shares *from* bank *to* player. 
        Negative value of k means transfer of |k| from player to bank.
        pre: all validation done prior to this call.
        """
        player.property[hotel.value] += k
        self.property[hotel.value] -= k
