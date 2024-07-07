from typing import List 

from acquisitions.game_logic.player import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.board_state import *
from acquisitions.game_logic.bank import *
from acquisitions.ui.ui_interface import *
from acquisitions.ui.text_ui import *

class GameOrchestrator:
    def __init__(self, player_names: List[str], ui: BaseUI):
        self.players = [PlayerState(name) for name in player_names]
        self.bank = BankState()
        self.board_state = BoardState()
        self.ui = ui
        self.init_tiles()
    
    def play(self):
        """Core game loop."""
        self.ui.display_initial()
        for turn in range(NUM_ROWS * NUM_COLS):
            self.play_turn(self.players[turn % len(self.players)])
        self.bank.tally_scores(self.players, self.board_state.hotel_sizes)
        self.ui.display_final_scores(self.players)

    def play_turn(self, player: PlayerState):
        self.ui.render_board(self.board_state.board)
        tile = self.get_tile(player)
        self.place_tile(player, tile)
        self.execute_purchases(player)
        self.bank.draw_tile(player)

    def get_tile(self, player: PlayerState) -> Tile:
        tile = self.ui.get_tile_from_user(player)
        player.tiles.remove(tile)
        return tile

    def place_tile(self, player: PlayerState, tile: Tile):
        game_event = self.board_state.place_tile(tile)
        if game_event == GameEvent.START_CHAIN:
            return self.start_chain(player, tile)
        elif game_event == GameEvent.MERGER:
            return self.handle_merger(player, tile)
        else:
            self.ui.display_event(player, tile, game_event)

    def execute_purchases(self, player: PlayerState):
        hotels = self.board_state.hotels_on_board()
        if not hotels:
            self.ui.display_message("No hotels on board; skipping purchases")
            return
        while 1:
            buy_order = self.ui.get_buy_order_from_user(player)
            success, msg = self.bank.execute_transaction(
                player, buy_order, self.board_state.hotel_sizes)
            self.ui.display_message(msg)
            if success:
                break
        self.ui.display_property(player)        
    
    def start_chain(self, player: PlayerState, tile: Tile):
        available_hotels = self.board_state.available_hotels()
        if not available_hotels:
            self.ui.display_message("No available hotels to start.")
            return
        self.ui.display_message(f"Congratulations {player.name}, you can start a hotel!")
        hotel = self.ui.get_hotel_from_user(player, available_hotels)
        self.bank.issue_free_share(player, hotel)
        self.board_state.mark_recursive(tile, hotel)

    def init_tiles(self):
        for player in self.players:
            for _ in range(TILES_PER_PLAYER):
                self.bank.draw_tile(player)

    def handle_merger(self, player: PlayerState, tile: Tile):
        can_merge, majority_options, hotels = self.board_state.check_merger(tile)
        if not can_merge:
            return self.board_state.mark_dead_tile(tile)
        self.ui.display_message("A merger has occurred!")
        if len(majority_options) > 1:
            self.ui.display_message(f"Due to a tie, {player.name}" 
                  "must select which hotel *remains* on the board.")
            hotel = self.ui.get_hotel_from_user(player, majority_options)
            # move this hotel to the front
            hotels.remove(hotel)
            hotels.insert(0, hotel)
        self.ui.display_message(f"Merging {hotels[1:]} into {hotels[0]}")
        for hotel in hotels[1:]:
            # TODO - should this merge order be backwards?
            self.execute_liquidity_event(hotel, hotels[0])
        return self.board_state.execute_merger(tile, hotels)
    
    def execute_liquidity_event(
            self, liquidated_hotel: Hotel, owning_hotel: Hotel):
        size = self.board_state.hotel_sizes[liquidated_hotel.value]
        award_msg = self.bank.grant_awards(self.players, liquidated_hotel, size)
        self.ui.display_message(award_msg)
        # players liquidate in decreasing order of ownership
        ownership = [p.property[liquidated_hotel.value] for p in self.players]
        for (player, shares) in sorted(zip(self.players, ownership), key=lambda x:-x[1]):
            while 1:
                sell, twofer = self.ui.get_user_liquidation_option(player.name, shares)
                success, msg = self.bank.liquidate_shares(
                    player, liquidated_hotel, size, sell, twofer, owning_hotel)
                self.ui.display_message(msg)
                if success:
                    break
    