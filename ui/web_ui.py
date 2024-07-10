import asyncio
import logging
from flask_socketio import SocketIO
from typing import List, Tuple
from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import Tile
from acquisitions.game_logic.player import PlayerState
from acquisitions.game_logic.board_state import CellState
from acquisitions.ui.ui_interface import BaseUI

class WebUI(BaseUI):
    def __init__(self, game_id, socketio, loop):
        self.game_id = game_id
        self.socketio = socketio
        self.loop = loop
        self.user_input = asyncio.Queue()
        self.message_history = []
        self.board_data = None

    def receive_input(self, data):
        logging.debug(f"Received input: {data}")
        self.user_input.put_nowait(data)
        logging.debug("Added to user input")

    def display_message(self, msg: str):
        logging.debug(f"Displaying message: {msg}")
        self.message_history.append(msg)
        self._emit('game_update', {
            'type': 'message',
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'board': self.board_data,
            'messages': self.last_messages()
        })

    def render_board(self, cell_states: List[List[CellState]]):
        logging.debug("Rendering board")
        self._emit('game_update', {
            'type': 'board_update',
            'board': self.update_board_data(cell_states),
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })
        logging.debug("Emitted board")

    async def get_tile_from_user(self, player: PlayerState) -> Tile:
        logging.debug(f"Getting tile from user: {player.name}")
        await self._emit('game_update', {
            'type': 'input_required',
            'input_type': 'tile',
            'player': player.name,
            'available_tiles': [str(tile) for tile in player.tiles],
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })
        logging.debug("Emitted message to frontend")
        result = await self.user_input.get()
        logging.debug("Got tile str")
        return Tile.from_str(result['tile'])

    async def get_hotel_from_user(self, player: PlayerState, hotels: List[Hotel]) -> Hotel:
        logging.debug(f"Getting hotel from user: {player.name}")
        await self._emit('game_update', {
            'type': 'input_required',
            'input_type': 'hotel',
            'player': player.name,
            'available_hotels': [hotel.name for hotel in hotels],
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })
        hotel_str = await self.user_input.get()
        return Hotel.from_str(hotel_str)

    async def get_buy_order_from_user(self, player: PlayerState) -> List[int]:
        logging.debug(f"Getting buy order from user: {player.name}")
        await self._emit('game_update', {
            'type': 'input_required',
            'input_type': 'buy_order',
            'player': player.name,
            'available_hotels': [hotel.name for hotel in Hotel if hotel != Hotel.NO_HOTEL],
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })
        buy_order_data = await self.user_input.get()
        buy_order = [0] * NUM_HOTELS
        for hotel, quantity in buy_order_data.items():
            hotel_enum = Hotel.from_str(hotel)
            buy_order[hotel_enum.value] = int(quantity)
        return buy_order

    async def get_user_liquidation_option(self, name: str, num_shares: int) -> Tuple[int, int]:
        logging.debug(f"Getting liquidation option from user: {name}")
        await self._emit('game_update', {
            'type': 'input_required',
            'input_type': 'liquidation',
            'player': name,
            'num_shares': num_shares,
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })
        liquidation_data = await self.user_input.get()
        return int(liquidation_data['sell']), int(liquidation_data['twofer'])

    async def display_final_scores(self, players: List[PlayerState]):
        logging.debug("Displaying final scores")
        scores = [{'name': p.name, 'money': p.money} for p in players]
        rankings = sorted(scores, key=lambda x: -x['money'])
        await self._emit('game_update', {
            'type': 'final_scores',
            'scores': rankings,
            'board_dimensions': {'rows': NUM_ROWS, 'cols': NUM_COLS},
            'messages': self.last_messages()
        })

    def last_messages(self):
        return self.message_history[-5:] if len(self.message_history) > 5 else self.message_history[:]
    
    def update_board_data(self, cell_states):
        self.board_data = []
        for r in range(NUM_ROWS):
            row = []
            for c in range(NUM_COLS):
                cell_state = cell_states[r][c]
                cell = {
                    'occupied': cell_state.occupied,
                    'dead_zone': cell_state.dead_zone,
                    'content': cell_state.hotel.name[:2] if cell_state.occupied and cell_state.hotel != Hotel.NO_HOTEL
                               else ('ZZ' if cell_state.dead_zone else f"{r}-{c}")
                }
                row.append(cell)
            self.board_data.append(row)
        return self.board_data

    def _emit(self, event, data):
        self.socketio.emit(event, data, room=self.game_id)
