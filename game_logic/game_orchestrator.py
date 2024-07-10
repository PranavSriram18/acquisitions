import asyncio
import logging

from typing import List 

from acquisitions.game_logic.player import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.board_state import *
from acquisitions.game_logic.bank import *
from acquisitions.ui.ui_interface import *
from acquisitions.ui.text_ui import *
from acquisitions.ui.web_ui import *

class GameOrchestrator:
    def __init__(self, uis: List[WebUI]):
        self.players = []
        self.bank = BankState()
        self.board_state = BoardState()
        self.uis = uis
        self.player_to_id = {}

    def add_player(self, player_name: str):
        self.players.append(PlayerState(player_name))
        logging.debug(f"Added player {player_name}")

    def is_ready(self) -> bool:
        return len(self.players) >= 2

    async def play(self):
        """Core game loop."""
        logging.debug("In play!")
        self.player_to_id = {player: i for i, player in enumerate(self.players)}
        for player in self.players:
            self.message_one(
                f"Welcome {player.name}! Beginning Acquisitions game",
                player
            )
        self.render_boards()
        self.init_tiles()
        logging.debug("Starting turns")
        for turn in range(NUM_ROWS * NUM_COLS):
            logging.debug(f"Playing turn {turn}")
            await self.play_turn(turn)
        await self.handle_game_end()

    async def play_turn(self, turn: int):
        self.curr_player_id = turn % len(self.players)
        player = self.players[self.curr_player_id]
        logging.debug(f"Playing turn {turn} rendering board")
        tile = await self.get_tile(player)
        self.place_tile(player, tile)
        self.render_boards()
        await self.execute_purchases(player)
        self.bank.draw_tile(player)

    def init_tiles(self):
        for player in self.players:
            for _ in range(TILES_PER_PLAYER):
                self.bank.draw_tile(player)

    async def get_tile(self, player: PlayerState) -> Tile:
        tile = await self.ui(player).get_tile_from_user(player)
        player.tiles.remove(tile)
        return tile

    def place_tile(self, player: PlayerState, tile: Tile):
        game_event = self.board_state.place_tile(tile)
        if game_event == GameEvent.START_CHAIN:
            return self.start_chain(player, tile)
        elif game_event == GameEvent.MERGER:
            return self.handle_merger(player, tile)
        else:
            self.message_all(f"Player {player.name} placed tile {tile}.")

    async def execute_purchases(self, player: PlayerState):
        hotels = self.board_state.hotels_on_board()
        if not hotels:
            await self.message_all("No hotels on board; skipping purchases")
            return
        while True:
            buy_order = await self.ui(
                player).get_buy_order_from_user(player, hotels)
            success, msg = self.bank.execute_transaction(
                player, buy_order, self.board_state.hotel_sizes)
            self.message_all(msg)
            if success:
                break
        self.message_one(player.property(), player)        
    
    async def start_chain(self, player: PlayerState, tile: Tile):
        available_hotels = self.board_state.available_hotels()
        if not available_hotels:
            self.message_all("No available hotels to start.")
            return
        self.message_all(f"{player.name}, gets to start a hotel!")
        hotel = await self.ui(player).get_hotel_from_user(player, available_hotels)
        self.bank.issue_free_share(player, hotel)
        self.board_state.mark_recursive(tile, hotel)

    async def handle_merger(self, player: PlayerState, tile: Tile):
        can_merge, majority_options, hotels = self.board_state.check_merger(tile)
        if not can_merge:
            return self.board_state.mark_dead_tile(tile)
        self.message_all("A merger has occurred!")
        if len(majority_options) > 1:
            self.message_all(f"Due to a tie, {player.name}" 
                  " must select which hotel *remains* on the board.")
            hotel = await self.ui(player).get_hotel_from_user(player, majority_options)
            hotels.remove(hotel)
            hotels.insert(0, hotel)
        self.message_all(f"Merging {hotels[1:]} into {hotels[0].name}")
        for hotel in hotels[1:]:
            self.execute_liquidity_event(hotel, hotels[0])
        return self.board_state.execute_merger(tile, hotels)
    
    def execute_liquidity_event(
            self, liquidated_hotel: Hotel, owning_hotel: Hotel):
        size = self.board_state.hotel_sizes[liquidated_hotel.value]
        award_msg = self.bank.grant_awards(self.players, liquidated_hotel, size)
        self.message_all(award_msg)
        ownership = [p.property[liquidated_hotel.value] for p in self.players]
        for (player, shares) in sorted(zip(self.players, ownership), key=lambda x: -x[1]):
            while True:
                sell, twofer = asyncio.create_task(
                    self.ui(player).get_user_liquidation_option(player.name, shares))
                success, msg = self.bank.liquidate_shares(
                    player, liquidated_hotel, size, sell, twofer, owning_hotel)
                self.message_all(msg)
                if success:
                    break
    
    async def handle_game_end(self):
        msg = self.bank.tally_scores(self.players, self.board_state.hotel_sizes)
        await self.message_all(msg)

    def render_boards(self):
        for ui in self.uis:
            ui.render_board(self.board_state.board)
    
    def message_all(self, msg: str):
        for ui in self.uis:
            ui.display_message(msg)

    def message_one(self, msg: str, player: PlayerState):
        self.ui(player).display_message(msg)

    def id(self, player: PlayerState):
        return self.player_to_id[player]
    
    def ui(self, player: PlayerState):
        return self.uis[self.id(player)]
    
    def receive_input(self, data):
        self.uis[self.curr_player_id].receive_input(data)
