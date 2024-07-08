from flask import Flask, render_template, jsonify, request
from typing import List, Tuple 
import threading
import time

from acquisitions.game_logic.constants import *
from acquisitions.game_logic.tile import *
from acquisitions.game_logic.player import *
from acquisitions.game_logic.board_state import *
from acquisitions.ui.ui_interface import BaseUI

class WebUI(BaseUI):
    def __init__(self):
        self.app = Flask(__name__)
        self.game_orchestrator = None
        self.setup_routes()
        self.user_input = None
        self.input_required = None
        self.messages = []
        self.lock = threading.Lock()
        self.game_state = {
            'board_dimensions': {
                'rows': NUM_ROWS,
                'cols': NUM_COLS
            }
        }

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/get_game_state')
        def get_game_state():
            with self.lock:
                return jsonify({
                    'board': self.game_state.get('board'),
                    'messages': self.game_state.get('messages'),
                    'input_required': self.input_required,
                    'board_dimensions': self.game_state['board_dimensions']
                })

        @self.app.route('/make_move', methods=['POST'])
        def make_move():
            with self.lock:
                self.user_input = request.json
                self.input_required = None
            return jsonify({'status': 'received'})

    def run(self):
        def run_flask():
            self.app.run(debug=True, use_reloader=False)
        
        self.flask_thread = threading.Thread(target=run_flask)
        self.flask_thread.start()

    def set_game_orchestrator(self, game_orchestrator):
        self.game_orchestrator = game_orchestrator

    def render_board(self, cell_states: List[List[CellState]]):
        board_data = []
        for r in range(NUM_ROWS):
            row = []
            for c in range(NUM_COLS):
                cell_state = cell_states[r][c]
                cell = {
                    'occupied': cell_state.occupied,
                    'dead_zone': cell_state.dead_zone,
                    'content': repr(cell_state)
                }
                row.append(cell)
            board_data.append(row)
        with self.lock:
            self.game_state['board'] = board_data

    def display_message(self, msg: str):
        with self.lock:
            self.messages.append(msg)
            if len(self.messages) > 5:
                self.messages.pop(0)
            self.game_state['messages'] = self.messages

    def display_property(self, player: PlayerState):
        msg = f"Propery for {player.name}: "
        for (hotel, num_shares) in zip(Hotel, player.property):
            if num_shares > 0:
                msg += f"{hotel.name}: {num_shares}\n"
        msg += f"Cash: {player.money}"
        self.display_message(msg)

    def display_event(self, player, tile, game_event):
        # TODO: Implement this method
        pass

    def get_tile_from_user(self, player: PlayerState) -> Tile:
        with self.lock:
            self.input_required = {
                'type': 'tile',
                'player': player.name,
                'available_tiles': [str(tile) for tile in player.tiles]
            }
        while True:
            with self.lock:
                if self.user_input is not None:
                    tile = Tile.from_str(self.user_input['tile'])
                    self.user_input = None
                    return tile
            time.sleep(0.1)  # Sleep to prevent busy-waiting

    def get_hotel_from_user(self, player: PlayerState, hotels: List[Hotel]) -> Hotel:
        with self.lock:
            self.input_required = {
                'type': 'hotel',
                'player': player.name,
                'available_hotels': [hotel.name for hotel in hotels]
            }
        while True:
            with self.lock:
                if self.user_input is not None:
                    hotel = Hotel.from_str(self.user_input['hotel'])
                    self.user_input = None
                    return hotel
                time.sleep(0.1)

    def get_user_liquidation_option(self, name: str, num_shares: int) -> Tuple[int, int]:
        with self.lock:
            self.input_required = {
                'type': 'liquidation',
                'player': name,
                'num_shares': num_shares
            }
        while True:
            with self.lock:
                if self.user_input is not None:
                    sell = int(self.user_input['sell'])
                    twofer = int(self.user_input['twofer'])
                    self.user_input = None
                    return sell, twofer
            time.sleep(0.1)

    def get_buy_order_from_user(self, player: PlayerState, hotels: List[Hotel]) -> List[int]:
        with self.lock:
            self.input_required = {
                'type': 'buy_order',
                'player': player.name,
                'available_hotels': [hotel.name for hotel in hotels]
            }
        while True:
            with self.lock:
                if self.user_input is not None:
                    buy_order = [0] * NUM_HOTELS
                    for hotel_str, quantity in self.user_input['buy_order'].items():
                        hotel = Hotel.from_str(hotel_str)
                        buy_order[hotel.value] = int(quantity)
                    self.user_input = None
                    return buy_order
            time.sleep(0.1)
