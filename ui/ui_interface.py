from abc import ABC, abstractmethod
from typing import List, Tuple 

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *
from acquisitions.game_logic.board_state import *
from acquisitions.ui.ui_interface import *

class BaseUI(ABC):
    @abstractmethod
    def render_board(self, cell_states):
        pass

    def display_message(self, msg: str):
        pass

    def display_property(self, player: PlayerState):
        pass

    @abstractmethod
    def get_tile_from_user(self, player: PlayerState) -> Tile:
        pass

    def get_hotel_from_user(self, player: PlayerState, hotels: List[Hotel]) -> Hotel:
        pass

    def get_buy_order_from_user(self, player: PlayerState) -> List[int]:
        pass

    def get_user_liquidation_option(self, name: str, num_shares: int) -> Tuple[int, int]:
        pass

