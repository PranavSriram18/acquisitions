from typing import List, Tuple 

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *
from acquisitions.game_logic.board_state import *
from acquisitions.ui.ui_interface import *

class TextUI(BaseUI):
    """ 
    Basic terminal-based text UI used in testing. Not actively maintained.
    """
    def run(self):
        print("Starting game!")

    def render_board(self, cell_states: List[List[CellState]]):
        print("Current board: \n\n")
        for r in range(NUM_ROWS):
            for c in range(NUM_COLS):
                print(cell_states[r][c])
            print("\n")

    def display_message(self, msg: str):
        print(msg)

    def display_event(self, player, tile, game_event):
        pass # TODO

    def get_tile_from_user(self, player: PlayerState) -> Tile:
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

    def get_hotel_from_user(self, player: PlayerState, hotels: List[Hotel]) -> Hotel:
        while True:
            print(f"Select a hotel from the following options: {hotels}")
            user_selection = input("Enter first 2 letters of hotel selection, or XX for no hotel: ")
            hotel = Hotel.from_str(user_selection)
            if hotel in hotels:
                break
            print("Invalid selection.")
        return hotel

    def get_buy_order_from_user(self, player: PlayerState, hotels: List[Hotel]) -> List[int]:
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

    def get_user_liquidation_option(self, name: str, num_shares: int) -> Tuple[int, int]:
        strs = input(f"{name}, you have {num_shares} shares. Enter sell, twofer: ").split(',')
        sell = int(strs[0].strip())
        twofer = int(strs[1].strip())
        return sell, twofer
    