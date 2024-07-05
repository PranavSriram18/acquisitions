from typing import List 

from acquisitions.game_logic.player import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.board_state import *
from acquisitions.game_logic.bank import *
from acquisitions.ui.render import *

class GameOrchestrator:
    def __init__(self, player_names: List[str]):
        self.players = [PlayerState(name) for name in player_names]
        self.bank = BankState()
        self.board_state = BoardState()
        self.game_ended = False
        self.n_players = len(self.players)
        self.init_tiles()
    
    def play(self):
        """
        Core game loop.
        """
        for turn in range(NUM_ROWS * NUM_COLS):
            self.play_turn(turn % self.n_players)
        self.calculate_scores()

    def play_turn(self, player_id: int):
        render_board_text(self.board_state.board)
        player = self.players[player_id]
        tile = self.get_tile(player)
        self.place_tile(player, tile)
        self.execute_purchases(player)
        self.draw_tile(player)

    def get_tile(self, player: PlayerState) -> Tile:
        received_valid_tile = False 
        while not received_valid_tile:
            tile_str = input(f"Enter a tile, {player.name}. Your available tiles are {player.tiles}\n")
            tile = Tile.from_str(tile_str)
            if not tile.is_valid():
                print(f"Invalid tile string; input must be 2-3 characters" 
                    "e.g. A0, B7, etc. and must be between A0 and I11")
                continue
            if not player.has_tile(tile):
                print(f"Player {player.name} does not have tile {tile}, try again.")
                continue
            received_valid_tile = True
        player.tiles.remove(tile)
        return tile

    def place_tile(self, player: PlayerState, tile: Tile):
        game_event = self.board_state.place_tile(tile)
        self.handle_game_event(player, tile, game_event)

    def execute_purchases(self, player: PlayerState):
        print("Skipping execute purchases")
        return  # TODO

    def draw_tile(self, player: PlayerState):
        tile = self.bank.draw_tile()
        if tile:
            player.tiles.append(tile)

    def handle_game_event(self, player: PlayerState, tile: Tile, game_event: GameEvent):
        if game_event == GameEvent.START_CHAIN:
            return self.start_chain(player, tile)
        elif game_event == GameEvent.DEAD_TILE:
            return self.board_state.mark_dead_tile(tile)
        elif game_event == GameEvent.MERGER:
            print("A merger has occurred!")
        else:
            print("Skipping handling tile event")  # TODO
        return
    
    def start_chain(self, player: PlayerState, tile: Tile):
        available_hotels = self.board_state.available_hotels()
        if not available_hotels:
            print("No available hotels to start.")
            return
        # TODO - move this block to ui
        print(f"Congratulations {player.name}, you can start a hotel.")
        while True:
            print(f"Available hotels: {available_hotels}")
            user_selection = input("Enter first 2 letters of hotel you wish to "
                                    "start, or XX for no hotel: ")
            hotel = Hotel.from_str(user_selection)
            if hotel in available_hotels:
                break
            print("invalid selection")
        # User gets 1 free share of this hotel
        self.bank.issue_free_share(player, hotel)
        # Board state needs to be updated
        self.board_state.mark_recursive(tile, hotel)

    def init_tiles(self):
        for player in self.players:
            for _ in range(TILES_PER_PLAYER):
                self.draw_tile(player)

    def calculate_scores(self):
        pass  # TODO