from typing import List 

from acquisitions.game_logic.player import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.board_state import *
from acquisitions.game_logic.bank import *
from acquisitions.ui.render import *
from acquisitions.ui.user_input import *

class GameOrchestrator:
    def __init__(self, player_names: List[str]):
        self.players = [PlayerState(name) for name in player_names]
        self.bank = BankState()
        self.board_state = BoardState()
        self.n_players = len(self.players)
        self.init_tiles()
    
    def play(self):
        """
        Core game loop.
        """
        for turn in range(NUM_ROWS * NUM_COLS):
            self.play_turn(turn % self.n_players)
        self.bank.tally_scores(self.players, self.board_state.hotel_sizes)

    def play_turn(self, player_id: int):
        render_board_text(self.board_state.board)
        player = self.players[player_id]
        tile = self.get_tile(player)
        self.place_tile(player, tile)
        self.execute_purchases(player)
        self.bank.draw_tile(player)

    def get_tile(self, player: PlayerState) -> Tile:
        tile = get_tile_from_user(player)
        player.tiles.remove(tile)
        return tile

    def place_tile(self, player: PlayerState, tile: Tile):
        game_event = self.board_state.place_tile(tile)
        self.handle_game_event(player, tile, game_event)

    def execute_purchases(self, player: PlayerState):
        print("Skipping execute purchases")
        return  # TODO

    def handle_game_event(self, player: PlayerState, tile: Tile, game_event: GameEvent):
        if game_event == GameEvent.NOOP:
            return
        if game_event == GameEvent.START_CHAIN:
            return self.start_chain(player, tile)
        elif game_event == GameEvent.MERGER:
            return self.handle_merger(player, tile)
        else:
            print("Skipping handling tile event")  # TODO
        return
    
    def start_chain(self, player: PlayerState, tile: Tile):
        available_hotels = self.board_state.available_hotels()
        if not available_hotels:
            print("No available hotels to start.")
            return
        print(f"Congratulations {player.name}, you can start a hotel.")
        hotel = get_hotel_from_user(available_hotels)
        self.bank.issue_free_share(player, hotel)
        self.board_state.mark_recursive(tile, hotel)

    def init_tiles(self):
        for player in self.players:
            for _ in range(TILES_PER_PLAYER):
                self.bank.draw_tile(player)

    def handle_merger(self, player: PlayerState, tile: Tile):
        can_merge, majority_options, multiway, hotels = self.board_state.check_merger(tile)
        if not can_merge:
            return self.board_state.mark_dead_tile(tile)
        print("A merger has occurred!")
        if len(majority_options) > 1:
            print(f"Due to a tie, {player.name}" 
                  "must select which hotel *remains* on the board.")
            hotel = get_hotel_from_user(majority_options)
            # move this hotel to the front
            hotels.remove(hotel)
            hotels.insert(0, hotel)
        print(f"Merging {hotels[1:]} into {hotels[0]}")
        return self.board_state.execute_merger(tile, hotels)
