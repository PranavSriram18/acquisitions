from typing import List, Tuple 

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *

def get_tile_from_user(player: PlayerState) -> Tile:
    while True:
        tile_str = input(f"Enter a tile, {player.name}. Your available tiles are: {player.tiles}\n")
        tile = Tile.from_str(tile_str)
        if not tile.is_valid():
            print(f"Invalid tile string; input must be 2-3 characters" 
                "e.g. A0, B7, etc. and must be between A0 and I11")
            continue
        if not player.has_tile(tile):
            print(f"Player {player.name} does not have tile {tile}, try again.")
            continue
        break
    return tile 

def get_hotel_from_user(hotels: List[Hotel]) -> Hotel:
    while True:
        print(f"Select a hotel from the following options: {hotels}")
        user_selection = input("Enter first 2 letters of hotel selection, or XX for no hotel: ")
        hotel = Hotel.from_str(user_selection)
        if hotel in hotels:
            break
        print("Invalid selection.")
    return hotel

def get_buy_order_from_user() -> List[int]:
    buy_order = [0] * NUM_HOTELS
    # TODO - more descriptive instructions here
    s = input("Enter purchase: ").split(',')
    for x in s:
        x = x.strip()
        hotel = Hotel.from_str(x[0:2])
        quantity = int(x[-1])
        assert(hotel.value < NUM_HOTELS)
        buy_order[hotel.value] = quantity 
    return buy_order

def get_liquidation_option_from_user(name: str, num_shares: int) -> Tuple[int, int]:
    strs = input(f"{name}, you have {num_shares} shares. Enter sell, twofer: ").split(',')
    sell = int(strs[0].strip())
    twofer = int(strs[1].strip())
    return sell, twofer


